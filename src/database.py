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
        
        # Import models to register them with Base
        from models.user_score import UserScore
        from models.user_amortization_data import UserAmortizationData
        from models.non_defaulter import NonDefaulter
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Ensure user_amortization_data table exists with correct schema
        from models.user_amortization_data import UserAmortizationData
        UserAmortizationData.__table__.create(bind=engine, checkfirst=True)
    
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