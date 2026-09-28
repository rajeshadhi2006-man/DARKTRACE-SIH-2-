import os
import logging
from typing import Generator, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("darktrace.database")

# Read database URL
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_FILE = os.path.join(BACKEND_ROOT, "data", "darktrace.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_FILE.replace(os.sep, '/')}")

# Ensure data directory exists for SQLite
if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

try:
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
    # Test connection
    with engine.connect() as conn:
        pass
    logger.info(f"Database connected using: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
except Exception as e:
    logger.warning(f"Primary database connection failed: {e}. Falling back to SQLite local database.")
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_FILE.replace(os.sep, '/')}"
    os.makedirs(os.path.dirname(DEFAULT_DB_FILE), exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Any, None, None]:
    """Dependency for obtaining database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------- Neo4j Connection & Fallback -----------------
neo4j_driver = None
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "darktrace_neo4j_password")

try:
    from neo4j import GraphDatabase
    neo4j_driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        connection_timeout=1.0,
        max_connection_lifetime=30
    )
    neo4j_driver.verify_connectivity()
    logger.info("Neo4j graph database connected successfully.")
except Exception as e:
    logger.info(f"Neo4j not active locally ({e}). Operating with resilient in-memory NetworkX graph engine.")
    neo4j_driver = None

def get_neo4j_session():
    if neo4j_driver:
        return neo4j_driver.session()
    return None

# ----------------- Redis Connection & Fallback -----------------
redis_client = None
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class InMemoryCache:
    """In-memory cache fallback when Redis is offline."""
    def __init__(self):
        self._store = {}

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value: Any, ex: int = None):
        self._store[key] = value

    def delete(self, key: str):
        self._store.pop(key, None)

    def ping(self):
        return True

try:
    import redis
    client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1.0)
    client.ping()
    redis_client = client
    logger.info("Redis cache connected successfully.")
except Exception as e:
    logger.info(f"Redis not available locally ({e}). Using in-memory cache fallback.")
    redis_client = InMemoryCache()

# ----------------- Health Check Functions -----------------
def check_db_health() -> dict:
    try:
        with engine.connect() as conn:
            return {"status": "HEALTHY", "engine": engine.name, "url": engine.url.render_as_string(hide_password=True)}
    except Exception as e:
        return {"status": "UNHEALTHY", "error": str(e)}

def check_neo4j_health() -> dict:
    if neo4j_driver:
        try:
            neo4j_driver.verify_connectivity()
            return {"status": "HEALTHY", "type": "Neo4j Cluster"}
        except Exception as e:
            return {"status": "DEGRADED", "fallback": "In-Memory Graph Engine", "error": str(e)}
    return {"status": "STANDBY", "mode": "Embedded In-Memory NetworkX Graph Engine"}

def check_redis_health() -> dict:
    try:
        redis_client.ping()
        is_in_memory = isinstance(redis_client, InMemoryCache)
        return {
            "status": "HEALTHY",
            "type": "In-Memory Cache" if is_in_memory else "Redis Server"
        }
    except Exception as e:
        return {"status": "UNHEALTHY", "error": str(e)}
