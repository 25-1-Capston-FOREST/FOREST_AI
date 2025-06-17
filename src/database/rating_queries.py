from .base import BaseDatabase
import logging
from typing import List, Dict, Any
from mysql.connector import Error as DatabaseError
import json

class RatingQueries(BaseDatabase):

    def __init__(self):
        super().__init__()  # BaseDatabase의 __init__ 호출
        self._logger = logging.getLogger(__name__)

    def get_ratings_data(self)-> List[Dict[str, Any]]:
        query = """
        SELECT 
            user_id,
            activity_id AS item_id,
            rate
        FROM DB_FOREST.REVIEW
        """
        
        try:
            self._logger.info("Surprise SVD 모델 학습용 평점 데이터를 조회합니다.")
            
            with self.db as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                
                if not result:
                    self._logger.error("Surprise SVD 모델 학습용 평점 데이터가 없습니다.")
                    return None
                
                self._logger.info(f"{len(results)}개의 Surprise 학습용 평점 데이터를 성공적으로 조회했습니다.")
                return results
                
        except Exception as e:
            self._logger.error(f"사용자-아이템-평점 데이터 조회 중 오류 발생: {str(e)}")
            return None

