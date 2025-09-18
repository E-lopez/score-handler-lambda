import logging
from sqlalchemy.exc import SQLAlchemyError
from models.non_defaulter import NonDefaulter
from database import get_db_session, close_db_session

logger = logging.getLogger(__name__)

def create_non_defaulter(data):
    session = get_db_session()
    try:
        new_non_defaulter = NonDefaulter(
            userId=data['userId'],
            demographics=data.get('demographics', 0),
            financialResponsibility=data.get('financialResponsibility', 0),
            riskAversion=data.get('riskAversion', 0),
            impulsivity=data.get('impulsivity', 0),
            futureOrientation=data.get('futureOrientation', 0),
            financialKnowledge=data.get('financialKnowledge', 0),
            locusOfControl=data.get('locusOfControl', 0),
            socialInfluence=data.get('socialInfluence', 0),
            resilience=data.get('resilience', 0),
            familismo=data.get('familismo', 0),
            respect=data.get('respect', 0),
            risk_level=data.get('risk_level', 0)
        )
        session.add(new_non_defaulter)
        session.commit()
        session.refresh(new_non_defaulter)
        
        # Refresh risk calculator with new data
        refresh_risk_calculator()
        
        return new_non_defaulter.to_dict()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error in create_non_defaulter: {str(e)}")
        return {'error': f'Database error: {str(e)}'}
    finally:
        close_db_session(session)

def get_all_non_defaulters():
    session = get_db_session()
    try:
        non_defaulters = session.query(NonDefaulter).all()
        return [nd.to_dict() for nd in non_defaulters]
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_all_non_defaulters: {str(e)}")
        return {'error': f'Database error: {str(e)}'}
    finally:
        close_db_session(session)

def refresh_risk_calculator():
    """Refresh the risk calculator after adding new non-defaulters"""
    try:
        from utils.risk_distance_calculator import get_risk_calculator
        risk_calc = get_risk_calculator()
        risk_calc._initialize_model()
        logger.info("Risk calculator refreshed")
    except Exception as e:
        logger.error(f"Error refreshing risk calculator: {str(e)}")