import logging
from sqlalchemy.exc import SQLAlchemyError
from models.user_score import UserScore
from utils.question_scoring import QuestionScoring
from database import get_db_session, close_db_session

logger = logging.getLogger(__name__)

def calc_score(section, values, gender=None):
    res = {}
    
    # Skip sections with zero weight or consent sections
    if section == 'consent' or (isinstance(values, dict) and values.get('metadata', {}).get('weight') == 0):
        return {}
    
    scoring = QuestionScoring(section)
    scoring_res = scoring.use_scoring(values)
    
    # Handle weight - demographics uses 1, others use metadata weight
    if section == 'demographics':
        weight = 1
    else:
        weight = values.get('metadata', {}).get('weight', 1) or 1
    
    # Apply gender-based enhancement to all sections except demographics
    if section != 'demographics' and gender == 'F':
        gender_boost = 1.5  # 75% boost for females in all sections
        scoring_res *= gender_boost
        print(f"Applied female gender boost of {gender_boost} to section {section}")
    
    res[section] = scoring_res * weight
    print(f"Section: {section}, Scoring Result: {scoring_res}, Weight: {weight}, Final Score: {res[section]}")
    return res

def register_survey_method(data):
    session = get_db_session()
    try:
        print(f"Input data keys: {list(data.keys())}")
        
        # Handle different input structures
        if 'demographics' in data:
            demographics_data = data['demographics']
        elif 'sections' in data and 'demographics' in data['sections']:
            demographics_data = data['sections']['demographics']
        else:
            raise ValueError("No demographics section found in input data")
        
        id_number = demographics_data.get('idNumber')
        gender = demographics_data.get('gender')
        
        if not id_number:
            raise ValueError("idNumber is required in demographics")
        
        # Prepare data for scoring - include demographics and all sections
        all_sections = {'demographics': demographics_data}
        if 'sections' in data:
            all_sections.update(data['sections'])
        
        # Calculate scores with gender consideration, filtering out empty results
        score_results = [calc_score(section, values, gender) for section, values in all_sections.items()]
        scores = {k: v for result in score_results for k, v in result.items() if result}
        
        # Apply variance enhancement to prevent clustering
        if scores:
            score_values = list(scores.values())
            mean_score = sum(score_values) / len(score_values)
            enhanced_scores = {}
            for section, score in scores.items():
                # Amplify deviations from mean to increase differentiation
                deviation = score - mean_score
                enhanced_score = score + (deviation * 0.3)  # 30% amplification
                enhanced_scores[section] = max(0.1, enhanced_score)  # Ensure positive scores
            
            raw_sum = sum(enhanced_scores.values())
            
            # Normalize to 0-100 scale based on theoretical min/max
            # Min: all 1s, male, unemployed ≈ 8.5
            # Max: all 5s, female, employed ≈ 95 (with 1.5x boost)
            min_possible = 8.5
            max_possible = 95.0
            
            # Normalize to 0-100
            sum_scr = max(0, min(100, ((raw_sum - min_possible) / (max_possible - min_possible)) * 100))
            scores = enhanced_scores  # Use enhanced scores
        else:
            sum_scr = 0

        # Check if user already exists
        existing_user = session.query(UserScore).filter_by(userId=id_number).first()

        print(f"Registering survey for user {id_number} (gender: {gender}) with enhanced scores: {list(scores.values())}. Raw total: {raw_sum if scores else 0}, Normalized (0-100): {sum_scr}")

        # Map dynamic section names to database fields
        field_mapping = {
            'demographics': 'demographics',
            'financialResponsibility': 'financialResponsibility',
            'riskAversion': 'riskAversion', 
            'impulsivity': 'impulsivity',
            'futureOrientation': 'futureOrientation',
            'financialKnowledge': 'financialKnowledge',
            'locusOfControl': 'locusOfControl',
            'socialInfluence': 'socialInfluence',
            'resilience': 'resilience',
            'familismo': 'familismo',
            'respect': 'respect'
        }

        if existing_user:
            # Update existing user dynamically
            for section, score in scores.items():
                field_name = field_mapping.get(section)
                if field_name and hasattr(existing_user, field_name):
                    setattr(existing_user, field_name, score)
            existing_user.risk_level = sum_scr
            session.commit()
            session.refresh(existing_user)
            return existing_user.to_dict()
        else:
            # Create new user dynamically
            user_data = {'userId': id_number, 'risk_level': sum_scr}
            for section, score in scores.items():
                field_name = field_mapping.get(section)
                if field_name:
                    user_data[field_name] = score
            
            new_score = UserScore(**user_data)
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