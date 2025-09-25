from flask import request, jsonify
from datetime import datetime
from functools import wraps

def validate_user_id():
    """
    Validate user_id parameter from request
    
    Returns:
        int: Valid user_id
        tuple: Error response if validation fails
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            'error': 'Missing required parameter',
            'message': 'user_id is required'
        }), 400
    
    try:
        user_id = int(user_id)
        return user_id
    except ValueError:
        return jsonify({
            'error': 'Invalid parameter',
            'message': 'user_id must be a valid integer'
        }), 400

def validate_date_range():
    """
    Validate date range parameters from request
    
    Returns:
        tuple: (start_date, end_date) or error response
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
        return start_date, end_date
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid date format',
            'message': 'Dates should be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)'
        }), 400

def handle_errors(f):
    """
    Decorator to handle common database and application errors
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            if 'Database connection failed' in error_message:
                return jsonify({
                    'error': 'Database connection failed',
                    'message': 'Unable to connect to database'
                }), 500
            else:
                return jsonify({
                    'error': 'Internal server error',
                    'message': error_message
                }), 500
    return decorated_function