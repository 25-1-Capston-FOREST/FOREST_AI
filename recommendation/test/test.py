import unittest
from typing import List, Dict, Any
from recommendation import RecommendationAlgorithm, UserProfile, ContentType, ContentTypeError

class TestRecommendationSystem(unittest.TestCase):
    def setUp(self):
        """테스트에 필요한 객체와 데이터 초기화"""
        self.recommender = RecommendationAlgorithm()
        
        # 테스트용 컨텐츠 아이템
        self.test_items = [
            {
                "id": 1,
                "type": "movie",
                "title": "인셉션",
                "genre": ["액션", "SF"],
                "keywords": ["꿈", "도둑", "잠입"],
                "director": "크리스토퍼 놀란",
                "cast": ["레오나르도 디카프리오", "조셉 고든 레빗"]
            },
            {
                "id": 2,
                "type": "performance",
                "title": "오페라의 유령",
                "genre": ["뮤지컬", "로맨스"],
                "keywords": ["음악", "사랑", "미스터리"],
                "director": "앤드류 로이드 웨버",
                "cast": ["마이클 크로포드", "사라 브라이트만"]
            },
            {
                "id": 3,
                "type": "exhibition",
                "title": "반 고흐 전시",
                "genre": ["미술", "회화"],
                "keywords": ["인상주의", "명화", "예술"],
                "artist": "빈센트 반 고흐",
                "period": "2024.01-2024.12"
            },
            {
                "id": 4,
                "type": "movie",
                "title": "어벤져스",
                "genre": ["액션", "SF"],
                "keywords": ["히어로", "액션", "팀워크"],
                "director": "조스 웨던",
                "cast": ["로버트 다우니 주니어", "크리스 에반스"]
            },
            {
                "id": 5,
                "type": "performance",
                "title": "캣츠",
                "genre": ["뮤지컬", "판타지"],
                "keywords": ["음악", "댄스", "고양이"],
                "director": "트레버 넌",
                "cast": ["엘레인 페이지", "브라이언 블레섹"]
            }
        ]
        
        # 테스트용 사용자 프로필
        self.test_user = UserProfile(
            keywords=["SF", "예술", "음악"],
            type_preferences={
                ContentType.MOVIE: 8,
                ContentType.PERFORMANCE: 6,
                ContentType.EXHIBITION: 7
            },
            genre_preferences={
                ContentType.MOVIE: ["액션", "SF"],
                ContentType.PERFORMANCE: ["뮤지컬"],
                ContentType.EXHIBITION: ["미술"]
            }
        )

    def test_content_type_validation(self):
        """컨텐츠 타입 검증 테스트"""
        # 유효한 타입 테스트
        valid_item = {"type": "movie", "title": "테스트"}
        self.assertEqual(
            self.recommender._get_content_type(valid_item),
            ContentType.MOVIE
        )
        
        # 타입이 없는 경우 테스트
        invalid_item = {"title": "테스트"}
        with self.assertRaises(ContentTypeError):
            self.recommender._get_content_type(invalid_item)
        
        # 잘못된 타입 테스트
        wrong_item = {"type": "invalid_type", "title": "테스트"}
        with self.assertRaises(ContentTypeError):
            self.recommender._get_content_type(wrong_item)

    def test_similarity_calculation(self):
        """유사도 계산 테스트"""
        # SF 영화에 대한 유사도 테스트
        movie_item = self.test_items[0]  # 인셉션
        similarity = self.recommender.calculate_similarity(movie_item, self.test_user)
        self.assertGreater(similarity, 0.0)
        
        # 뮤지컬에 대한 유사도 테스트
        performance_item = self.test_items[1]  # 오페라의 유령
        similarity = self.recommender.calculate_similarity(performance_item, self.test_user)
        self.assertGreater(similarity, 0.0)

    def test_recommendation_generation(self):
        """추천 리스트 생성 테스트"""
        # 추천 리스트 생성
        recommendations = self.recommender.generate_recommendations(
            self.test_items,
            self.test_user,
            total_count=3
        )
        
        # 추천 수 확인
        self.assertEqual(len(recommendations), 3)
        
        # 타입 분포 확인
        type_counts = {}
        for item in recommendations:
            item_type = item['type']
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        # 최소 하나의 영화가 포함되어 있는지 확인
        self.assertGreaterEqual(type_counts.get('movie', 0), 1)

    def test_user_preferences_impact(self):
        """사용자 선호도 영향 테스트"""
        # 영화 선호도를 최대로 설정
        movie_preferred_user = UserProfile(
            keywords=["SF", "액션"],
            type_preferences={
                ContentType.MOVIE: 10,
                ContentType.PERFORMANCE: 1,
                ContentType.EXHIBITION: 1
            },
            genre_preferences={
                ContentType.MOVIE: ["액션", "SF"],
                ContentType.PERFORMANCE: [],
                ContentType.EXHIBITION: []
            }
        )
        
        recommendations = self.recommender.generate_recommendations(
            self.test_items,
            movie_preferred_user,
            total_count=3
        )
        
        # 영화가 우선적으로 추천되는지 확인
        self.assertEqual(recommendations[0]['type'], 'movie')

def print_test_results(recommendations: List[Dict[str, Any]]) -> None:
    """테스트 결과 출력"""
    print("\n=== 추천 결과 ===")
    for idx, item in enumerate(recommendations, 1):
        print(f"\n{idx}. {item['title']} ({item['type']})")
        print(f"   장르: {', '.join(item['genre'])}")
        print(f"   키워드: {', '.join(item['keywords'])}")

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)