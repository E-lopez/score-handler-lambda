import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from models.user_amortization_data import UserAmortizationData
from models.user_score import UserScore
from utils.table_generator import TableGenerator
from database import get_db_session, close_db_session

logger = logging.getLogger(__name__)

def get_user_risk(user_id):
    session = get_db_session()
    try:
        user_score = session.query(UserScore).filter_by(userId=user_id).first()
        if user_score:
            return float(user_score.risk_level) if user_score.risk_level else 0.0
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error getting user risk: {str(e)}")
        return None
    finally:
        close_db_session(session)

def save_amortization(user_id, user_risk, period_value, instalment_value, amount):
    session = get_db_session()
    try:
        data = UserAmortizationData(
            userId=user_id,
            userRisk=user_risk,
            instalment=instalment_value,
            period=period_value,
            amount=amount
        )
        session.add(data)
        session.commit()
        session.refresh(data)
        return data.to_dict()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error saving amortization data: {str(e)}")
        raise e
    finally:
        close_db_session(session)

def handle_amortization(user_id, user_risk, data):
    session = get_db_session()
    try:
        user_data = session.query(UserAmortizationData).filter_by(userId=user_id).first()
        period_value = 0 if data.get('period') == 'null' else data.get('period')
        instalment_value = 0 if data.get('instalment') == 'null' else data.get('instalment')
        amount = data['amount']
        
        logger.info(f"Values: period={period_value}, instalment={instalment_value}, amount={amount}")
        
        if user_data is None:
            logger.info("Creating new amortization record")
            # Create new record using the same session
            new_data = UserAmortizationData(
                userId=user_id,
                userRisk=user_risk,
                instalment=instalment_value,
                period=period_value,
                amount=amount
            )
            session.add(new_data)
        else:
            logger.info("Updating existing amortization record")
            user_data.userRisk = user_risk
            user_data.period = period_value
            user_data.instalment = instalment_value
            user_data.amount = amount
        
        session.commit()
        logger.info("Amortization data saved successfully")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"SQLAlchemy error in handle_amortization: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in handle_amortization: {str(e)}", exc_info=True)
        raise e
    finally:
        close_db_session(session)

def repayment_plan(data):
    try:
        payment_type = data.get('payment_type')
        user_id = data.get('userId')
        repayment_type = 'repayment_plan_period' if payment_type == 'period' else 'repayment_plan_instalment'
        
        # Use provided user_risk or get from database if userId provided
        if 'user_risk' in data:
            user_risk = float(data['user_risk'])
        elif user_id:
            user_risk = get_user_risk(user_id)
            if user_risk is None:
                return {'error': 'User not found or no risk level available'}
        else:
            return {'error': 'Either userId or user_risk must be provided'}
        
        # Prepare data for table generation (remove non-calculation fields)
        calc_data = data.copy()
        calc_data.pop('payment_type', None)
        calc_data.pop('userId', None)
        calc_data['user_risk'] = user_risk
        
        generator = TableGenerator(repayment_type)
        res = generator.use_method(**calc_data)
        
        # Only save to database if userId is provided and calculation succeeded
        if user_id and res and 'error' not in res:
            try:
                handle_amortization(str(user_id), user_risk, data)
            except Exception as db_error:
                logger.error(f"Database save failed: {str(db_error)}")
                # Don't fail the request if DB save fails
        
        return res
    except Exception as e:
        logger.error(f"Error in repayment_plan: {str(e)}", exc_info=True)
        return {'error': str(e)}

def get_user_amortization(user_id):
    session = get_db_session()
    try:
        user_data = session.query(UserAmortizationData).filter_by(userId=user_id).first()
        if user_data is None:
            return {'error': 'User not found'}, 404
        
        result = recalculate_plan(user_data)
        result['user_data'] = user_data.to_dict()
        return result, 200
    except Exception as e:
        logger.error(f"Error getting user amortization: {str(e)}")
        return {'error': str(e)}, 500
    finally:
        close_db_session(session)

def recalculate_plan(user_data):
    try:
        user_risk = float(user_data.userRisk) if user_data.userRisk else 0.0
        period_value = float(user_data.period) if user_data.period else 0.0
        instalment_value = float(user_data.instalment) if user_data.instalment else 0.0
        amount = float(user_data.amount) if user_data.amount else 0.0
        
        repayment_type = 'repayment_plan_period' if period_value != 0 else 'repayment_plan_instalment'
        data = {
            'user_risk': user_risk,
            'period': period_value,
            'instalment': instalment_value,
            'amount': amount
        }
        generator = TableGenerator(repayment_type)
        res = generator.use_method(**data)
        return res
    except Exception as e:
        logger.error(f"Error recalculating plan: {str(e)}")
        return {'error': str(e)}