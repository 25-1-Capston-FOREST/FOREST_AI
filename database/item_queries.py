from .base import BaseDatabase
import logging
from typing import List, Dict, Any
from mysql.connector import Error as DatabaseError


class ItemQueries(BaseDatabase):

    def __init__(self):
        super().__init__()  # BaseDatabase의 __init__ 호출
        self._logger = logging.getLogger(__name__)

    def get_movies_data(self, content_type: str) -> List[Dict]:
        """모든 영화 정보를 가져오는 메서드"""
        query = """
            SELECT 
                activity_id,
                title,
                genre_nm,
                director,
                actors,
                keywords
            FROM DB_FOREST.MOVIE
        """
        try:
            self._logger.info(f"영화 데이터 가져오기")

            with self.db as conn:
                cursor = conn.cursor()
                self._logger.info(f"쿼리 실행")
                cursor.execute(query)
                
                # 컬럼명 가져오기
                columns = [desc[0] for desc in cursor.description]
                self._logger.info("영화 정보 딕셔너리 리스트로 변환")
                # 결과를 딕셔너리 리스트로 변환
                result = []
                for row in cursor.fetchall():
                    result.append(dict(zip(columns, row)))
                    
                return result
                
        except DatabaseError as e:
            self._logger.error(f"영화 정보 조회 중 오류 발생: {str(e)}")
            return []

    def get_performances_data(self):
        """모든 공연 정보를 가져오는 메서드"""
        query = """
            SELECT 
                activity_id,
                title,
                genre,
                cast,
                keywords
            FROM DB_FOREST.PERFORMANCE
        """
        try:
            with self.db as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                # 컬럼명 가져오기
                columns = [desc[0] for desc in cursor.description]
                
                # 결과를 딕셔너리 리스트로 변환
                result = []
                for row in cursor.fetchall():
                    result.append(dict(zip(columns, row)))
                    
                return result
                
        except DatabaseError as e:
            logging.error(f"공연 정보 조회 중 오류 발생: {str(e)}")
            return []

    def get_exhibitions_data(self):
        """모든 전시 정보를 가져오는 메서드"""
        query = """
            SELECT 
                activity_id,
                title,
                keywords
            FROM DB_FOREST.EXHIBITION
        """
        try:
            with self.db as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                # 컬럼명 가져오기
                columns = [desc[0] for desc in cursor.description]
                
                # 결과를 딕셔너리 리스트로 변환
                result = []
                for row in cursor.fetchall():
                    result.append(dict(zip(columns, row)))
                    
                return result
                
        except DatabaseError as e:
            logging.error(f"전시 정보 조회 중 오류 발생: {str(e)}")
            return []