from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from database import execute_query
from utils.validators import validate_user_id, validate_date_range, handle_errors

history_bp = Blueprint('history', __name__)

@history_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'flask-history',
        'timestamp': datetime.now().isoformat()
    })

@history_bp.route('/balance', methods=['GET'])
@handle_errors
def get_total_balance():
    """Get total balance for a user (income - expenses)"""
    user_id = validate_user_id()
    if isinstance(user_id, tuple):  # Error response
        return user_id
    
    query = """
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expenses
        FROM transactions 
        WHERE user_id = %s
    """
    
    result = execute_query(query, (user_id,), fetch_one=True)
    
    total_income = float(result['total_income'])
    total_expenses = float(result['total_expenses'])
    balance = total_income - total_expenses
    
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'balance': balance,
            'total_income': total_income,
            'total_expenses': total_expenses
        },
        'timestamp': datetime.now().isoformat()
    })

@history_bp.route('/income', methods=['GET'])
@handle_errors
def get_total_income():
    """Get total income for a user"""
    user_id = validate_user_id()
    if isinstance(user_id, tuple):  # Error response
        return user_id
    
    query = """
        SELECT COALESCE(SUM(amount), 0) as total_income
        FROM transactions 
        WHERE user_id = %s AND type = 'income'
    """
    
    result = execute_query(query, (user_id,), fetch_one=True)
    total_income = float(result['total_income'])
    
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'total_income': total_income
        },
        'timestamp': datetime.now().isoformat()
    })

@history_bp.route('/expenses', methods=['GET'])
@handle_errors
def get_total_expenses():
    """Get total expenses for a user"""
    user_id = validate_user_id()
    if isinstance(user_id, tuple):  # Error response
        return user_id
    
    query = """
        SELECT COALESCE(SUM(amount), 0) as total_expenses
        FROM transactions 
        WHERE user_id = %s AND type = 'expense'
    """
    
    result = execute_query(query, (user_id,), fetch_one=True)
    total_expenses = float(result['total_expenses'])
    
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'total_expenses': total_expenses
        },
        'timestamp': datetime.now().isoformat()
    })

@history_bp.route('/transactions', methods=['GET'])
@handle_errors
def get_recent_transactions():
    """
    Get recent transactions with optional date range filtering
    
    Query parameters:
    - user_id (required): User ID
    - start_date (optional): Start date in ISO format
    - end_date (optional): End date in ISO format
    - days (optional): Number of recent days (default: 10)
    - limit (optional): Limit number of results (default: 100)
    """
    user_id = validate_user_id()
    if isinstance(user_id, tuple):  # Error response
        return user_id
    
    # Validate date range if provided
    date_validation = validate_date_range()
    if isinstance(date_validation, tuple) and len(date_validation) == 2 and hasattr(date_validation[0], 'status_code'):
        return date_validation
    
    start_date, end_date = date_validation
    
    # Get other optional parameters
    days = request.args.get('days', '10')
    limit = request.args.get('limit', '100')
    
    try:
        days = int(days)
        limit = int(limit)
    except ValueError:
        return jsonify({
            'error': 'Invalid parameter',
            'message': 'days and limit must be valid integers'
        }), 400
    
    # Build query based on date parameters
    if start_date and end_date:
        # Custom date range
        query = """
            SELECT transaction_id, name, amount, date, type, emoji
            FROM transactions 
            WHERE user_id = %s AND date >= %s AND date <= %s
            ORDER BY date DESC
            LIMIT %s
        """
        params = (user_id, start_date, end_date, limit)
    elif start_date:
        # From start_date to now
        query = """
            SELECT transaction_id, name, amount, date, type, emoji
            FROM transactions 
            WHERE user_id = %s AND date >= %s
            ORDER BY date DESC
            LIMIT %s
        """
        params = (user_id, start_date, limit)
    elif end_date:
        # From beginning to end_date
        query = """
            SELECT transaction_id, name, amount, date, type, emoji
            FROM transactions 
            WHERE user_id = %s AND date <= %s
            ORDER BY date DESC
            LIMIT %s
        """
        params = (user_id, end_date, limit)
    else:
        # Last N days (default behavior)
        start_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT transaction_id, name, amount, date, type, emoji
            FROM transactions 
            WHERE user_id = %s AND date >= %s
            ORDER BY date DESC
            LIMIT %s
        """
        params = (user_id, start_date, limit)
    
    results = execute_query(query, params, fetch_all=True)
    
    # Format results
    transactions = []
    for row in results:
        transactions.append({
            'transaction_id': row['transaction_id'],
            'name': row['name'],
            'amount': float(row['amount']),
            'date': row['date'].isoformat(),
            'type': row['type'],
            'emoji': row['emoji']
        })
    
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'transactions': transactions,
            'count': len(transactions),
            'filters': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'days': days if not start_date and not end_date else None,
                'limit': limit
            }
        },
        'timestamp': datetime.now().isoformat()
    })