from .base import BaseDatabase

class UserQueries(BaseDatabase):
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
        FROM PREFERENCE 
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        try:
            result = self.execute_query(query, (user_id,))
            if not result:
                return None
                
            preferences = result[0]
            
            # JSON 필드들이 문자열로 반환될 경우를 대비한 처리
            try:
                if isinstance(preferences['movie_genre_preference'], str):
                    preferences['movie_genre_preference'] = json.loads(preferences['movie_genre_preference'])
                if isinstance(preferences['performance_genre_preference'], str):
                    preferences['performance_genre_preference'] = json.loads(preferences['performance_genre_preference'])
                if isinstance(preferences['exhibition_genre_preference'], str):
                    preferences['exhibition_genre_preference'] = json.loads(preferences['exhibition_genre_preference'])
                if isinstance(preferences['like_words'], str):
                    preferences['like_words'] = json.loads(preferences['like_words'])
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {str(e)}")
            
            return preferences
            
        except Exception as e:
            print(f"사용자 선호도 조회 중 오류 발생: {str(e)}")
            return None