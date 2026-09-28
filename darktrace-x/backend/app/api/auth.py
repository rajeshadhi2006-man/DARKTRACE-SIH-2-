from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import User, AuditLog
from ..schemas.entities import Token, LoginRequest, UserResponse
from ..security.auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    user.last_login = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="LOGIN",
        object_type="User",
        object_id=user.id,
        details={"status": "SUCCESS", "username": user.username, "role": user.role_id},
        ip_address=request.client.host if request.client else "127.0.0.1"
    )
    db.add(audit)
    db.commit()

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role_id, "user_id": user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role_id
        }
    }

@router.post("/login/json", response_model=Token)
def login_json(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    user.last_login = datetime.utcnow()
    
    audit = AuditLog(
        user_id=user.id,
        action="LOGIN",
        object_type="User",
        object_id=user.id,
        details={"status": "SUCCESS", "username": user.username, "role": user.role_id},
        ip_address=request.client.host if request.client else "127.0.0.1"
    )
    db.add(audit)
    db.commit()

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role_id, "user_id": user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role_id
        }
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
