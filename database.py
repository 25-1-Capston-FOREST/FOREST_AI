import mysql.connector
import logging
from typing import List, Dict, Any, Tuple

class DatabaseService:
    def __init__(self, config: Dict[str, str]):
        self.config = config
        logging.info("DatabaseService 초기화")

    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as e:
            logging.error(f"데이터베이스 연결 실패: {str(e)}")
            raise

    def get_all_users(self) -> List[Dict[str, Any]]:
        """모든 사용자 정보를 가져옴"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("""
                        SELECT user_id, user_name, age, gender 
                        FROM users
                    """)
                    return cursor.fetchall()
        except Exception as e:
            logging.error(f"사용자 데이터 조회 실패: {str(e)}")
            raise

    def get_user_preferences(self, user_id: int) -> List[Dict[str, Any]]:
        """특정 사용자의 선호도 정보를 가져옴"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("""
                        SELECT item_id, rating, timestamp
                        FROM user_ratings
                        WHERE user_id = %s
                    """, (user_id,))
                    return cursor.fetchall()
        except Exception as e:
            logging.error(f"사용자 {user_id}의 선호도 데이터 조회 실패: {str(e)}")
            raise

    def get_all_items(self) -> List[Dict[str, Any]]:
        """모든 아이템 정보를 가져옴"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("""
                        SELECT item_id, title, genre, release_date
                        FROM items
                    """)
                    return cursor.fetchall()
        except Exception as e:
            logging.error(f"아이템 데이터 조회 실패: {str(e)}")
            raise

    def get_item_details(self, item_id: int) -> Dict[str, Any]:
        """특정 아이템의 상세 정보를 가져옴"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("""
                        SELECT item_id, title, genre, release_date,
                               description, rating_average
                        FROM items
                        WHERE item_id = %s
                    """, (item_id,))
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError(f"Item ID {item_id} not found")
                    return result
        except Exception as e:
            logging.error(f"아이템 {item_id}의 상세 정보 조회 실패: {str(e)}")
            raise