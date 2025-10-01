import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(dotenv_path='./.env')

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
    """Return a new database connection with schema search path set."""
    config = Config()
    conn = psycopg2.connect(**config.DATABASE_CONFIG)
    
    # Set the search path to include the expense schema
    with conn.cursor() as cursor:
        cursor.execute("SET search_path TO expense, public;")
    conn.commit()
    
    return conn

def execute_query(query, params=None, fetch=False, fetch_one=False, fetch_all=False):
    """
    Execute a SQL query.
    
    :param query: SQL query string
    :param params: Tuple of parameters (optional)
    :param fetch: Legacy parameter for backward compatibility (use fetch_all instead)
    :param fetch_one: True to return single result
    :param fetch_all: True to return all results
    :return: Single dict, list of dicts, or None
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all or fetch:  # fetch for backward compatibility
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