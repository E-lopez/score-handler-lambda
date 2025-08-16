import logging
from sqlalchemy.exc import SQLAlchemyError
from models.user_score import UserScore
from utils.question_scoring import QuestionScoring
from database import get_db_session, close_db_session

logger = logging.getLogger(__name__)

def calc_score(section, values):
    res = {}
    scoring = QuestionScoring(section)
    scoring_res = scoring.use_scoring(values)
    weight = 1 if section == 'demographics' else values['weight']
    res[section] = scoring_res * weight
    print(f"Section: {section}, Values: {values}, Scoring Result: {scoring_res}, Weight: {weight}, Final Score: {res[section]}")
    return res

def register_survey_method(data):
    session = get_db_session()
    try:
        id_number = data['demographics']['idNumber']
        parsed_data = {'demographics': {**data['demographics']}, **data['sections']}
        t = list(map(lambda x: calc_score(x[0], x[1]), parsed_data.items()))
        scores = {k: v for dict in t for k, v in dict.items()}
        sum_scr = sum(scores.values())

        # Check if user already exists
        existing_user = session.query(UserScore).filter_by(userId=id_number).first()

        print(f"Registering survey for existing user {existing_user} with scores: {scores.values()}. Result: {sum_scr}")

        if existing_user:
            # Update existing user
            existing_user.demographics = scores.get('demographics', 0)
            existing_user.financialResponsibility = scores.get('financialKnowledge', 0)
            existing_user.riskAversion = scores.get('riskAversion', 0)
            existing_user.impulsivity = scores.get('impulsivity', 0)
            existing_user.futureOrientation = scores.get('futureOrientation', 0)
            existing_user.financialKnowledge = scores.get('financialKnowledge', 0)
            existing_user.locusOfControl = scores.get('locusOfControl', 0)
            existing_user.socialInfluence = scores.get('socialInfluence', 0)
            existing_user.resilience = scores.get('resilience', 0)
            existing_user.familismo = scores.get('familismo', 0)
            existing_user.respect = scores.get('respect', 0)
            existing_user.risk_level = sum_scr
            session.commit()
            session.refresh(existing_user)
            return existing_user.to_dict()
        else:
            # Create new user
            new_score = UserScore(
                userId=id_number,
                demographics=scores.get('demographics', 0),
                financialResponsibility=scores.get('financialKnowledge', 0),
                riskAversion=scores.get('riskAversion', 0),
                impulsivity=scores.get('impulsivity', 0),
                futureOrientation=scores.get('futureOrientation', 0),
                financialKnowledge=scores.get('financialKnowledge', 0),
                locusOfControl=scores.get('locusOfControl', 0),
                socialInfluence=scores.get('socialInfluence', 0),
                resilience=scores.get('resilience', 0),
                familismo=scores.get('familismo', 0),
                respect=scores.get('respect', 0),
                risk_level=sum_scr
            )
            session.add(new_score)
            session.commit()
            session.refresh(new_score)
            return new_score.to_dict()
            
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error in register_survey_method: {str(e)}")
        return {'error': f'Database error: {str(e)}'}
    except Exception as e:
        session.rollback()
        logger.error(f"Error in register_survey_method: {str(e)}")
        return {'error': str(e)}
    finally:
        close_db_session(session)