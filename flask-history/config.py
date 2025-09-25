import os
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(dotenv_path='../.env')

class Config:
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'postgres')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'expense_db')
    DB_USER = os.getenv('DB_USER', 'expense_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'expense_pass')
    
    # Flask configuration
    PORT = int(os.getenv('PORT_FLASK', '6000'))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database connection parameters
    @property
    def DATABASE_CONFIG(self):
        return {
            'host': self.DB_HOST,
            'port': self.DB_PORT,
            'database': self.DB_NAME,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD
        }