from flask import Flask, jsonify, request
from flask_cors import CORS
from database import Config, execute_query
from datetime import datetime, timedelta

def create_app():
    app = Flask(__name__)
    config = Config()
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": [
                     "http://localhost:3000",
                     "https://expenses.halfskirmish.com"
                 ],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "expose_headers": ["Content-Type"],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })

    @app.route('/')
    def root():
        return {
            'message': 'Flask History Service is running',
            'service': 'flask-history',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/history/health',
                'balance': '/api/history/balance?user_id={user_id}',
                'income': '/api/history/income?user_id={user_id}',
                'expenses': '/api/history/expenses?user_id={user_id}',
                'transactions': '/api/history/transactions?user_id={user_id}&start_date={start_date}&end_date={end_date}'
            }
        }

    @app.route('/api/history/health', methods=['GET'])
    def health_check():
        return jsonify({
            "service": "flask-history",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        })

    @app.route('/api/history/balance', methods=['GET'])
    def get_balance():
        try:
            user_id = request.args.get('user_id')
            query = """
                SELECT COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END), 0) as balance 
                FROM transactions 
                WHERE user_id = %s
            """
            result = execute_query(query, (user_id,), fetch=True)
            return jsonify(result[0] if result else {'balance': 0})
        except Exception as e:
            return jsonify({"error": "Internal server error", "message": str(e)}), 500

    @app.route('/api/history/income', methods=['GET'])
    def get_income():
        try:
            user_id = request.args.get('user_id')
            query = """
                SELECT COALESCE(SUM(amount), 0) as total_income 
                FROM transactions 
                WHERE user_id = %s AND type = 'income'
            """
            result = execute_query(query, (user_id,), fetch=True)
            return jsonify(result[0] if result else {'total_income': 0})
        except Exception as e:
            return jsonify({"error": "Internal server error", "message": str(e)}), 500

    @app.route('/api/history/expenses', methods=['GET'])
    def get_expenses():
        try:
            user_id = request.args.get('user_id')
            query = """
                SELECT COALESCE(SUM(amount), 0) as total_expenses 
                FROM transactions 
                WHERE user_id = %s AND type = 'expense'
            """
            result = execute_query(query, (user_id,), fetch=True)
            return jsonify(result[0] if result else {'total_expenses': 0})
        except Exception as e:
            return jsonify({"error": "Internal server error", "message": str(e)}), 500

    @app.route('/api/history/transactions', methods=['GET'])
    def get_transactions():
        try:
            user_id = request.args.get('user_id')
            days = int(request.args.get('days', 30))
            limit = int(request.args.get('limit', 10))
            
            query = """
                SELECT transaction_id, name, amount, date, type, emoji
                FROM transactions 
                WHERE user_id = %s 
                AND date >= %s 
                ORDER BY date DESC 
                LIMIT %s
            """
            date_limit = datetime.now() - timedelta(days=days)
            result = execute_query(query, (user_id, date_limit, limit), fetch=True)
            
            # Format the results to ensure proper JSON serialization
            transactions = []
            for row in result:
                transactions.append({
                    'transaction_id': row['transaction_id'],
                    'name': row['name'],
                    'amount': int(row['amount']),  # Convert to int as per your schema
                    'date': row['date'].isoformat() if row['date'] else None,
                    'type': row['type'],
                    'emoji': row['emoji']
                })
            
            return jsonify({
                'transactions': transactions,
                'count': len(transactions),
                'user_id': int(user_id),
                'days': days,
                'limit': limit
            })
        except Exception as e:
            return jsonify({"error": "Internal server error", "message": str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    config = Config()
    
    print(f"Starting Flask History Service on port {config.PORT}")
    print(f"Debug mode: {config.DEBUG}")
    
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG
    )