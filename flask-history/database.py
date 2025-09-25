import os
import psycopg2
from psycopg2.extras import RealDictCursor
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

# ----------------------------
# Database helper functions
# ----------------------------

def get_connection():
    """Return a new database connection."""
    config = Config()
    return psycopg2.connect(**config.DATABASE_CONFIG)

def execute_query(query, params=None, fetch=False):
    """
    Execute a SQL query.
    
    :param query: SQL query string
    :param params: Tuple of parameters (optional)
    :param fetch: True to return results, False for insert/update/delete
    :return: List of dicts if fetch=True, else None
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            result = None
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
