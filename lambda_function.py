import json
import logging
import os
from typing import Dict, Any

from config import Config
from database import init_db
from services.amortization_service import repayment_plan, get_user_amortization
from services.register_survey_service import register_survey_method

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection
db = init_db()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for score-handler service
    """
    try:
        # Parse the request (handle HTTP API v2 format)
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('path') or event.get('rawPath', '/')
        body = event.get('body')
        path_parameters = event.get('pathParameters') or {}
        
        logger.info(f"Request: {http_method} {path}")
        
        # Parse JSON body if present
        request_data = {}
        if body:
            try:
                request_data = json.loads(body)
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                    },
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }

        # Route handling
        if path == '/health' or path == '/':
            return create_response(200, {'status': 'healthy', 'service': 'score-handler'})
        
        elif path == '/survey' and http_method == 'POST':
            result = register_survey_method(request_data)
            return create_response(200, result)
        
        elif path == '/repayment-plan' and http_method == 'POST':
            result = repayment_plan(request_data)
            return create_response(200, result)
        
        elif path.startswith('/repayment-plan/') and http_method == 'GET':
            user_id = path_parameters.get('user_id') or path.split('/')[-1]
            result, status_code = get_user_amortization(user_id)
            return create_response(status_code, result)
        
        else:
            logger.warning(f"No route found for {http_method} {path}")
            return create_response(404, {'error': f'Endpoint not found: {http_method} {path}'})
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return create_response(500, {'error': 'Internal server error'})

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create a properly formatted API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body)
    }