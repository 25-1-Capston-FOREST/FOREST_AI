from .base import BaseDatabase
import logging

class ItemQueries(BaseDatabase):
    def get_movies_data(self):
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
            logging.error(f"영화 정보 조회 중 오류 발생: {str(e)}")
            return []

    def get_performance_data(self):
        """모든 공연 정보를 가져오는 메서드"""
        query = """
            SELECT 
                activity_id,
                title,
                genre,
                story,
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

    def get_exhibition_data(self):
        """모든 전시 정보를 가져오는 메서드"""
        query = """
            SELECT 
                activity_id,
                title,
                contents,
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