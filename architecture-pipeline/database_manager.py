import os
import json
from datetime import datetime
# Assuming you use a library like mysql.connector or PyMySQL
import mysql.connector 

class DatabaseManager:
    """
    Manages all database connections and transactional operations 
    for the Architecture Pipeline.
    """
    def __init__(self):
        # Load connection details from environment variables
        self.config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'database': os.getenv('DB_NAME', 'arch_db')
        }
    
    def _get_connection(self):
        """Establishes a connection to the MySQL database."""
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            raise