from db.base import BaseDatabase, DatabaseError  # 모듈 구조에 맞게 import 경로 수정
import logging

class PreferenceSaver(BaseDatabase):
    def save_keywords(self, user_id, keywords):
        """
        사용자의 선호 키워드를 데이터베이스에 저장합니다.

        :param user_id: 사용자 아이디 (str 또는 int)
        :param keywords: 키워드 리스트 (list)
        :return: 저장된 키워드 개수 (int)
        """
        if not user_id or not keywords:
            raise ValueError("user_id와 keywords는 필수입니다.")
        
        query = """
            INSERT INTO user_keywords (user_id, keyword)
            VALUES (%s, %s)
        """
        count = 0
        try:
            for kw in keywords:
                self.execute_query(query, (user_id, kw))
                count += 1
            return count
        except DatabaseError as e:
            logging.error(f"[PreferenceSaver] 키워드 저장 실패: {str(e)}")
            raise                      