from flask import Flask
from flask_cors import CORS
from config import Config
from routes.history import history_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config = Config()
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(history_bp, url_prefix='/api/history')
    
    # Root endpoint
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