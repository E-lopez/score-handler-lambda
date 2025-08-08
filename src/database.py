from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

Base = declarative_base()
engine = None
SessionLocal = None

def init_db():
    """Initialize database connection for Lambda"""
    global engine, SessionLocal
    
    if engine is None:
        config = Config()
        engine = create_engine(
            config.SQLALCHEMY_DATABASE_URI,
            **Config.SQLALCHEMY_ENGINE_OPTIONS
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal

def get_db_session():
    """Get database session"""
    if SessionLocal is None:
        init_db()
    return SessionLocal()

def close_db_session(session):
    """Close database session"""
    if session:
        session.close()