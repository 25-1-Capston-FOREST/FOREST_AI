import json
from .base import BaseDatabase
import logging
from typing import List
from mysql.connector import Error as DatabaseError

class PreferenceQueries(BaseDatabase):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)

    def save_like_words(self, user_id: str, new_keywords: List[str]):
        """
        user_id에 맞춰 like_words(JSON) 컬럼에 키워드를 중복 없이 추가/업데이트합니다.
        """
        if not new_keywords:
            self._logger.info("추가할 키워드가 없습니다.")
            return

        try:
            with self.db as conn:
                cursor = conn.cursor()

                # 1. 기존 like_words 가져오기
                select_query = """
                    SELECT like_words FROM DB_FOREST.PREFERENCE
                    WHERE user_id = %s
                """
                cursor.execute(select_query, (user_id,))
                row = cursor.fetchone()

                if row:
                    # 기존 JSON 배열 불러오기 (빈 값이면 빈 리스트)
                    try:
                        existing_list = json.loads(row[0]) if row[0] else []
                    except Exception:
                        existing_list = []  # 혹시나 형식 문제가 있으면 빈 리스트

                    # 새 키워드와 합쳐서 중복 제거 (set 사용)
                    final_set = set(existing_list) | set(new_keywords)
                    final_list = list(final_set)
                    final_like_words = json.dumps(final_list)

                    update_query = """
                        UPDATE DB_FOREST.PREFERENCE
                        SET like_words = %s
                        WHERE user_id = %s
                    """
                    cursor.execute(update_query, (final_like_words, user_id))
                    self._logger.info(f"user_id={user_id}의 like_words가 성공적으로 업데이트되었습니다.")
                else:
                    # 기존 정보가 없으면 새로 INSERT
                    final_list = list(set(new_keywords))
                    final_like_words = json.dumps(final_list)
                    insert_query = """
                        INSERT INTO DB_FOREST.PREFERENCE (user_id, like_words)
                        VALUES (%s, %s)
                    """
                    cursor.execute(insert_query, (user_id, final_like_words))
                    self._logger.info(f"user_id={user_id}의 like_words가 신규로 저장되었습니다.")

                conn.commit()
        except DatabaseError as e:
            self._logger.error(f"like_words 저장 중 데이터베이스 오류 발생: {str(e)}")
        except Exception as ex:
            self._logger.error(f"like_words 저장 중 예외 발생: {str(ex)}")