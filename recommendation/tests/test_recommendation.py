import unittest
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from recommendation import RecommendationAlgorithm, ContentType, ContentTypeError
from tests.test_data.sample_data import TEST_ITEMS, TEST_USER, MOVIE_PREFERRED_USER

class TestContentTypeValidation(unittest.TestCase):
    """컨텐츠 타입 검증 테스트"""
    
    def setUp(self):
        self.recommender = RecommendationAlgorithm()

    def test_valid_content_type(self):
        """유효한 컨텐츠 타입 테스트"""
        valid_item = {"type": "movie", "title": "테스트"}
        content_type = self.recommender._get_content_type(valid_item)
        self.assertEqual(content_type, ContentType.MOVIE)

class TestSimilarityCalculation(unittest.TestCase):
    """유사도 계산 테스트"""
    
    def setUp(self):
        self.recommender = RecommendationAlgorithm()

    def test_movie_similarity(self):
        """영화 유사도 계산 테스트"""
        movie_item = TEST_ITEMS[0]  # 인셉션
        similarity = self.recommender.calculate_similarity(
            movie_item, 
            TEST_USER
        )
        self.assertGreater(similarity, 0.0)

    def test_performance_similarity(self):
        """공연 유사도 계산 테스트"""
        performance_item = TEST_ITEMS[1]  # 오페라의 유령
        similarity = self.recommender.calculate_similarity(
            performance_item, 
            TEST_USER
        )
        self.assertGreater(similarity, 0.0)

class TestRecommendationGeneration(unittest.TestCase):
    """추천 생성 테스트"""
    
    def setUp(self):
        self.recommender = RecommendationAlgorithm()

    def test_recommendation_count(self):
        """추천 수량 테스트"""
        recommendations = self.recommender.generate_recommendations(
            TEST_ITEMS,
            TEST_USER,
            total_count=3
        )
        self.assertEqual(len(recommendations), 3)

    def test_type_distribution(self):
        """타입 분포 테스트"""
        recommendations = self.recommender.generate_recommendations(
            TEST_ITEMS,
            TEST_USER,
            total_count=3
        )
        
        type_counts = {}
        for item in recommendations:
            item_type = item['type']
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
            
        self.assertGreaterEqual(type_counts.get('movie', 0), 1)

    def test_user_preferences(self):
        """사용자 선호도 반영 테스트"""
        recommendations = self.recommender.generate_recommendations(
            TEST_ITEMS,
            MOVIE_PREFERRED_USER,
            total_count=3
        )
        self.assertEqual(recommendations[0]['type'], 'movie')

def print_test_results(recommendations):
    """테스트 결과 출력"""
    print("\n=== 추천 결과 ===")
    for idx, item in enumerate(recommendations, 1):
        print(f"\n{idx}. {item['title']} ({item['type']})")
        print(f"   장르: {', '.join(item['genre'])}")
        print(f"   키워드: {', '.join(item['keywords'])}")

if __name__ == '__main__':
    unittest.main(verbosity=2)