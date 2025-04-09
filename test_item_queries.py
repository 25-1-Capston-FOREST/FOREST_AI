import unittest
import logging
from database.item_queries import ItemQueries
from mysql.connector import Error as DatabaseError

class TestItemQueries(unittest.TestCase):
    def setUp(self):
        """테스트 시작 전 ItemQueries 인스턴스 생성"""
        self.item_queries = ItemQueries()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def test_get_movies_data(self):
        """실제 데이터베이스에서 영화 데이터를 가져오는 테스트"""
        try:
            movies = self.item_queries.get_movies_data("MOVIE")
            
            # 결과가 리스트인지 확인
            self.assertIsInstance(movies, list)
            
            if movies:
                self.logger.info(f"총 {len(movies)}개의 영화 데이터를 가져왔습니다.")
                self.logger.info("첫 번째 영화 데이터:")
                self.logger.info(movies[0])
                
                # 필수 필드 확인
                first_movie = movies[0]
                required_fields = ['activity_id', 'title', 'genre_nm', 'director', 'actors', 'keywords']
                for field in required_fields:
                    self.assertIn(field, first_movie)
            else:
                self.logger.warning("영화 데이터가 없습니다.")

        except Exception as e:
            self.logger.error(f"테스트 중 오류 발생: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main()