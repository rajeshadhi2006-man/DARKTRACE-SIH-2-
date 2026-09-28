import os
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import User, Role

SECRET_KEY = os.getenv("SECRET_KEY", "darktrace_x_super_secret_jwt_hmac_sha256_key_2026_investigator")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

import bcrypt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8')[:72], hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8')[:72], salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")
    return user

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role_id not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

def seed_default_roles_and_users(db: Session):
    """Initializes RBAC roles and default investigation accounts if table is empty."""
    roles_def = [
        ("ADMIN", "Full platform administration, user management, and system configuration", ["*"]),
        ("SUPERVISOR", "Review findings, manage investigations, and authorize reports", ["review:findings", "export:reports", "view:intelligence"]),
        ("ANALYST", "Conduct threat actor investigation, stylometry, and graph correlation", ["investigate:actors", "view:evidence", "create:notes", "run:analytics"]),
        ("VIEWER", "Read-only analytical intelligence access", ["read:intelligence"])
    ]

    for role_id, desc, perms in roles_def:
        existing_role = db.query(Role).filter(Role.id == role_id).first()
        if not existing_role:
            db.add(Role(id=role_id, description=desc, permissions=perms))
    db.commit()

    # Seed default users
    users_def = [
        ("admin", "admin@darktrace.local", "DarktraceAdmin2026!", "Senior Threat Intel Architect", "ADMIN"),
        ("investigator", "investigator@darktrace.local", "Investigator2026!", "Lead CTI Investigator", "ANALYST"),
        ("supervisor", "supervisor@darktrace.local", "Supervisor2026!", "Case Review Supervisor", "SUPERVISOR"),
        ("viewer", "viewer@darktrace.local", "Viewer2026!", "Intelligence Observer", "VIEWER")
    ]

    for uname, email, plain_pw, fname, r_id in users_def:
        existing = db.query(User).filter(User.username == uname).first()
        if not existing:
            hashed = get_password_hash(plain_pw)
            db.add(User(
                username=uname,
                email=email,
                hashed_password=hashed,
                full_name=fname,
                role_id=r_id,
                is_active=True
            ))
    db.commit()
