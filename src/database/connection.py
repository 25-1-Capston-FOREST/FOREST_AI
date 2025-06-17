import mysql.connector
from mysql.connector import Error
import logging
from config.settings import DB_CONFIG

class DatabaseConnection:
    @staticmethod
    def get_connection():
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            return connection
        except Error as e:
            logging.error(f"데이터베이스 연결 실패: {e}")
            raise
            
    def __enter__(self):
        self.connection = self.get_connection()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'connection'):
            self.connection.close()