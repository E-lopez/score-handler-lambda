import logging
from services.register_survey_service import register_survey_method
from utils.risk_distance_calculator import get_risk_calculator

logger = logging.getLogger(__name__)

def register_clustered_survey(data):
    """Register survey and calculate risk distance classification"""
    try:
        # First, register the survey normally
        survey_result = register_survey_method(data)
        
        if 'error' in survey_result:
            return survey_result
        
        # Calculate risk distance using the survey scores
        risk_calc = get_risk_calculator()
        risk_result = risk_calc.calculate_risk_distance(survey_result)
        
        # Combine results
        clustered_result = {
            **survey_result,
            'risk_distance_analysis': risk_result
        }
        
        logger.info(f"Clustered survey registered for user {survey_result.get('userId')} with risk category: {risk_result.get('risk_category', 'Unknown')}")
        
        return clustered_result
        
    except Exception as e:
        logger.error(f"Error in register_clustered_survey: {str(e)}")
        return {'error': str(e)}