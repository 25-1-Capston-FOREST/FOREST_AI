from .base import BaseDatabase
import logging
from typing import List, Dict, Any
from mysql.connector import Error as DatabaseError
import json

class UserQueries(BaseDatabase):

    def __init__(self):
        super().__init__()  # BaseDatabase의 __init__ 호출
        self._logger = logging.getLogger(__name__)

    def get_user_preferences(self, user_id):
        query = """
        SELECT 
            movie_preference,
            performance_preference,
            exhibition_preference,
            movie_genre_preference,
            performance_genre_preference,
            exhibition_genre_preference,
            like_words
        FROM DB_FOREST.PREFERENCE 
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        try:
            self._logger.info(f"사용자 {user_id}의 선호도 조회를 시작합니다.")
            
            with self.db as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                
                if not result:
                    self._logger.error(f"사용자 {user_id}의 선호도 데이터가 없습니다.")
                    return None
                
                # JSON 문자열을 파이썬 객체로 변환
                movie_genres = self._parse_json(result['movie_genre_preference'])
                performance_genres = self._parse_json(result['performance_genre_preference'])
                exhibition_genres = self._parse_json(result['exhibition_genre_preference'])
                like_words = self._parse_json(result['like_words'])
                
                # 벡터 생성을 위한 모든 특성 결합
                vector = (
                    movie_genres +
                    performance_genres +
                    exhibition_genres +
                    like_words
                )
                
                user_profile = {
                    'user_id': user_id,
                    'movie_preference': result['movie_preference'],
                    'performance_preference': result['performance_preference'],
                    'exhibition_preference': result['exhibition_preference'],
                    'movie_genre_preference': movie_genres,
                    'performance_genre_preference': performance_genres,
                    'exhibition_genre_preference': exhibition_genres,
                    'like_words': like_words,
                    'vector': vector
                }
                
                self._logger.info(f"사용자 {user_id}의 선호도 데이터 조회 완료")
                return user_profile
                
        except Exception as e:
            self._logger.error(f"사용자 선호도 조회 중 오류 발생: {str(e)}")
            return None

    def _parse_json(self, data_str):
        """JSON 문자열을 파이썬 객체로 변환"""
        try:
            if isinstance(data_str, str):
                return json.loads(data_str)
            return [] if data_str is None else data_str
        except json.JSONDecodeError as e:
            self._logger.error(f"JSON 파싱 오류: {str(e)}")
            return []