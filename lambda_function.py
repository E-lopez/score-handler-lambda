import json
import logging
import os
from typing import Dict, Any

from config import Config
from database import init_db
from services.amortization_service import repayment_plan, get_user_amortization
from services.register_survey_service import register_survey_method
from services.non_defaulter_service import create_non_defaulter, get_all_non_defaulters
from services.clustered_survey_service import register_clustered_survey

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
        http_method, path, body, path_parameters, headers, origin = parse_event(event)
        logger.info(f"Request: {http_method} {path}")

        request_data = parse_json_body(body, origin)
        if isinstance(request_data, dict) and request_data.get('error'):
            return create_response(400, request_data, origin)

        if http_method == 'OPTIONS':
            return create_response(200, {}, origin)

        return handle_route(http_method, path, request_data, path_parameters, origin)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return create_response(500, {'error': 'Internal server error'}, None)

def parse_event(event: Dict[str, Any]):
    http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    path = event.get('path') or event.get('rawPath', '/')
    body = event.get('body')
    path_parameters = event.get('pathParameters') or {}
    headers = event.get('headers') or {}
    origin = headers.get('origin') or headers.get('Origin')
    return http_method, path, body, path_parameters, headers, origin

def parse_json_body(body, origin):
    if not body:
        return {}
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {'error': 'Invalid JSON in request body'}

def handle_route(http_method, path, request_data, path_parameters, origin):
    if path in ['/health', '/']:
        return create_response(200, {'status': 'healthy', 'service': 'score-handler'}, origin)

    if path == '/survey' and http_method == 'POST':
        result = register_survey_method(request_data)
        return create_response(200, result, origin)

    if path == '/clustered-score' and http_method == 'POST':
        result = register_clustered_survey(request_data)
        return create_response(200, result, origin)

    if path == '/non-defaulters':
        if http_method == 'POST':
            result = create_non_defaulter(request_data)
            return create_response(201, result, origin)
        if http_method == 'GET':
            result = get_all_non_defaulters()
            return create_response(200, result, origin)

    if path == '/repayment-plan' and http_method == 'POST':
        result = repayment_plan(request_data)
        return create_response(200, result, origin)

    if path.startswith('/repayment-plan/') and http_method == 'GET':
        user_id = path_parameters.get('user_id') or path.split('/')[-1]
        result, status_code = get_user_amortization(user_id)
        return create_response(status_code, result, origin)

    logger.warning(f"No route found for {http_method} {path}")
    return create_response(404, {'error': f'Endpoint not found: {http_method} {path}'}, origin)

def create_response(status_code: int, body: Dict[str, Any], origin: str = None) -> Dict[str, Any]:
    """Create a properly formatted API Gateway response"""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, Origin'
    }
    
    # Set CORS origin based on request origin
    if origin and origin in ['http://localhost:3000', 'http://localhost:5173', 'https://loan-client.onrender.com']:
        headers['Access-Control-Allow-Origin'] = origin
        headers['Access-Control-Allow-Credentials'] = 'true'
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body)
    }