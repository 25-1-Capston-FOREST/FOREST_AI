from .base import BaseDatabase
import logging
from typing import List
from mysql.connector import Error as DatabaseError

class PreferenceSaver(BaseDatabase):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)

    def save_user_keywords(self, user_id: int, keywords: List[str]) -> int:
        """
        사용자 선호 키워드를 user_keywords 테이블에 저장합니다.
        :param user_id: 사용자 ID (int)
        :param keywords: 키워드 리스트 (str 리스트)
        :return: 저장된 키워드 개수 (int)
        """
        if not user_id or not keywords:
            self._logger.warning("user_id나 keywords가 비어있습니다.")
            return 0
        
        query = """
            INSERT INTO DB_FOREST.user_keywords (user_id, keyword)
            VALUES (%s, %s)
        """
        saved_count = 0

        try:
            with self.db as conn:
                cursor = conn.cursor()
                for kw in keywords:
                    try:
                        cursor.execute(query, (user_id, kw))
                        saved_count += 1
                    except DatabaseError as e:
                        self._logger.error(f"키워드 저장 실패 (user_id={user_id}, keyword={kw}): {str(e)}")
                conn.commit()
            self._logger.info(f"{saved_count}개 키워드 저장 완료 (user_id={user_id})")
            return saved_count
        except DatabaseError as e:
            self._logger.error(f"키워드 저장 중 DB 오류 발생: {str(e)}")
            return 0
