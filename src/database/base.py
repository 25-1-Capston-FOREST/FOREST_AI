from abc import ABC
from .connection import DatabaseConnection
from mysql.connector import Error

class DatabaseError(Exception):
    pass

class BaseDatabase(ABC):
    def __init__(self):
        self.db = DatabaseConnection()

    def execute_query(self, query, params=None):
        with self.db as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = {'affected_rows': cursor.rowcount}
                return result
            except Error as e:
                conn.rollback()
                raise DatabaseError(f"쿼리 실행 중 오류 발생: {str(e)}")
            finally:
                cursor.close()