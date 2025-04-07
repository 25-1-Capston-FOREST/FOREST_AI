## 추천 알고리즘 메인 코드
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
from enum import Enum
from dataclasses import dataclass
import re


class ContentTypeError(Exception):
    """컨텐츠 타입 관련 예외"""
    pass

class ContentType(Enum):
    MOVIE = "movie"
    PERFORMANCE = "performance"
    EXHIBITION = "exhibition"
    
    @classmethod
    def get_valid_types(cls):
        """유효한 컨텐츠 타입 목록을 반환합니다."""
        return [member.value for member in cls]


@dataclass
class UserProfile:
    keywords: List[str]  # 선호 키워드
    type_preferences: Dict[ContentType, int]  # 각 타입별 선호도
    genre_preferences: Dict[ContentType, List[str]]  # 각 타입별 선호 장르

class RecommendationAlgorithm:
    def __init__(self):
        self._vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2)
        )
        
        # 타입별 목표 비율 설정 (전체 합 1)
        self._type_ratios = {
            ContentType.MOVIE: 0.4,
            ContentType.PERFORMANCE: 0.3,
            ContentType.EXHIBITION: 0.3
        }
        
        # 최종 점수 계산을 위한 가중치
        self._similarity_weight = 0.7  # 유사도 점수 가중치
        self._preference_weight = 0.3  # 선호도 점수 가중치
        
        self._logger = logging.getLogger(__name__)
        self._setup_logger()

    def _setup_logger(self) -> None:
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def _normalize_text(self, text: str) -> str:
        """텍스트 정규화"""
        try:
            text = text.lower()
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\d+', '', text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception as e:
            self._logger.error(f"텍스트 정규화 중 오류 발생: {str(e)}")
            return text

    def _extract_item_text(self, item_data: Dict[str, Any]) -> str:
        """아이템 데이터에서 관련 텍스트 추출"""
        try:
            text_parts = []
            
            # 제목 추가
            if 'title' in item_data:
                text_parts.append(str(item_data['title']))
            
            # 장르 추가
            if 'genre' in item_data:
                if isinstance(item_data['genre'], list):
                    text_parts.extend(item_data['genre'])
                else:
                    text_parts.append(str(item_data['genre']))
            
            # 키워드/태그 추가
            for field in ['keywords', 'tags']:
                if field in item_data:
                    if isinstance(item_data[field], list):
                        text_parts.extend(item_data[field])
                    else:
                        text_parts.append(str(item_data[field]))
            
            return ' '.join(text_parts)
        except Exception as e:
            self._logger.error(f"텍스트 추출 중 오류 발생: {str(e)}")
            return ""

    def _get_content_type(self, item_data: Dict[str, Any]) -> ContentType:
        """
        아이템 데이터에서 컨텐츠 타입을 추출하고 검증
        
        Args:
            item_data: 아이템 데이터 딕셔너리
            
        Returns:
            ContentType: 검증된 컨텐츠 타입
            
        Raises:
            ContentTypeError: 컨텐츠 타입이 없거나 유효하지 않은 경우
        """
        try:
            if 'type' not in item_data:
                raise ContentTypeError(
                    "컨텐츠 타입이 지정되지 않았습니다. "
                    f"유효한 타입: {ContentType.get_valid_types()}"
                )

            type_str = item_data['type']
            if not isinstance(type_str, str):
                raise ContentTypeError(
                    f"컨텐츠 타입은 문자열이어야 합니다. "
                    f"입력된 타입: {type(type_str)}"
                )

            if type_str not in ContentType.get_valid_types():
                raise ContentTypeError(
                    f"유효하지 않은 컨텐츠 타입입니다: {type_str}. "
                    f"유효한 타입: {ContentType.get_valid_types()}"
                )

            return ContentType(type_str)

        except ContentTypeError as e:
            self._logger.error(f"컨텐츠 타입 오류: {str(e)}")
            raise
        except Exception as e:
            self._logger.error(f"예상치 못한 오류 발생: {str(e)}")
            raise ContentTypeError(f"컨텐츠 타입 처리 중 오류 발생: {str(e)}")

    def calculate_similarity(self, 
                          item_data: Dict[str, Any], 
                          user_profile: UserProfile) -> float:
        """
        아이템과 사용자 프로필 간의 코사인 유사도 계산
        """
        try:
            # 아이템 텍스트 추출 및 전처리
            item_text = self._extract_item_text(item_data)
            item_text = self._normalize_text(item_text)
            
            # 사용자 프로필 텍스트 생성
            content_type = self._get_content_type(item_data)
            user_text_parts = (
                user_profile.keywords +  # 선호 키워드
                user_profile.genre_preferences.get(content_type, [])  # 해당 타입의 선호 장르
            )
            user_text = self._normalize_text(' '.join(user_text_parts))
            
            if not item_text or not user_text:
                return 0.0
            
            # 코사인 유사도 계산
            tfidf_matrix = self._vectorizer.fit_transform([item_text, user_text])
            similarity_score = cosine_similarity(
                tfidf_matrix[0:1], 
                tfidf_matrix[1:2]
            )[0][0]
            
            return float(similarity_score)
            
        except Exception as e:
            self._logger.error(f"유사도 계산 중 오류 발생: {str(e)}")
            return 0.0

    def _calculate_final_score(self, 
                             similarity_score: float, 
                             content_type: ContentType,
                             user_profile: UserProfile) -> float:
        """
        최종 추천 점수 계산
        유사도 점수와 사용자 선호도를 결합
        """
        try:
            # 해당 타입에 대한 사용자 선호도 (0-10 스케일을 0-1로 정규화)
            type_preference = user_profile.type_preferences.get(content_type, 0) / 10.0
            
            # 최종 점수 계산
            final_score = (
                similarity_score * self._similarity_weight +
                type_preference * self._preference_weight
            )
            
            return final_score
            
        except Exception as e:
            self._logger.error(f"최종 점수 계산 중 오류 발생: {str(e)}")
            return 0.0

    def generate_recommendations(self, 
                              content_items: List[Dict[str, Any]],
                              user_profile: UserProfile,
                              total_count: int = 10) -> List[Dict[str, Any]]:
        """
        추천 리스트 생성
        컨텐츠 타입 간의 균형을 맞추어 추천
        """
        try:
            # 각 아이템의 점수 계산
            scored_items = []
            for item in content_items:
                similarity_score = self.calculate_similarity(item, user_profile)
                content_type = self._get_content_type(item)
                final_score = self._calculate_final_score(
                    similarity_score, 
                    content_type,
                    user_profile
                )
                
                scored_items.append({
                    'item': item,
                    'score': final_score,
                    'type': content_type
                })
            
            # 타입별로 아이템 분류
            items_by_type = {
                content_type: [
                    item for item in scored_items 
                    if item['type'] == content_type
                ]
                for content_type in ContentType
            }
            
            # 각 타입별로 정렬
            for items in items_by_type.values():
                items.sort(key=lambda x: x['score'], reverse=True)
            
            # 목표 비율에 따라 각 타입별 아이템 수 계산
            type_counts = {
                content_type: max(1, int(total_count * ratio))
                for content_type, ratio in self._type_ratios.items()
            }
            
            # 비율에 맞게 각 타입별 상위 아이템 선정
            recommendations = []
            for content_type, count in type_counts.items():
                recommendations.extend([
                    item['item'] 
                    for item in items_by_type[content_type][:count]
                ])
            
            # 최종 개수 조정
            recommendations = recommendations[:total_count]
            
            self._logger.info(
                f"추천 리스트 생성 완료: {len(recommendations)}개 항목"
            )
            return recommendations

        except Exception as e:
            self._logger.error(f"추천 리스트 생성 중 오류 발생: {str(e)}")
            return []

def main():
    # 테스트용 데이터
    content_items = [
        # 영화 데이터 (20개)
        {
            "id": 1,
            "type": "movie",
            "title": "인셉션",
            "genre": ["액션", "SF"],
            "keywords": ["꿈", "도둑", "잠입"],
        },
        {
            "id": 2,
            "type": "movie",
            "title": "기생충",
            "genre": ["드라마", "스릴러"],
            "keywords": ["빈부격차", "블랙코미디", "사회비판"],
        },
        {
            "id": 3,
            "type": "movie",
            "title": "어벤져스: 엔드게임",
            "genre": ["액션", "SF"],
            "keywords": ["영웅", "우주", "전쟁"],
        },
        {
            "id": 4,
            "type": "movie",
            "title": "겨울왕국",
            "genre": ["애니메이션", "뮤지컬"],
            "keywords": ["눈", "자매", "마법"],
        },
        {
            "id": 5,
            "type": "movie",
            "title": "인터스텔라",
            "genre": ["SF", "드라마"],
            "keywords": ["우주", "시간", "구원"],
        },
        {
            "id": 6,
            "type": "movie",
            "title": "라라랜드",
            "genre": ["뮤지컬", "로맨스"],
            "keywords": ["음악", "꿈", "사랑"],
        },
        {
            "id": 7,
            "type": "movie",
            "title": "타이타닉",
            "genre": ["로맨스", "드라마"],
            "keywords": ["사랑", "배", "비극"],
        },
        {
            "id": 8,
            "type": "movie",
            "title": "해리포터와 마법사의 돌",
            "genre": ["판타지", "어드벤처"],
            "keywords": ["마법", "호그와트", "우정"],
        },
        {
            "id": 9,
            "type": "movie",
            "title": "다크 나이트",
            "genre": ["액션", "스릴러"],
            "keywords": ["배트맨", "조커", "정의"],
        },
        {
            "id": 10,
            "type": "movie",
            "title": "알라딘",
            "genre": ["애니메이션", "뮤지컬"],
            "keywords": ["램프", "마법", "사랑"],
        },
        {
            "id": 11,
            "type": "movie",
            "title": "007 스카이폴",
            "genre": ["액션", "스릴러"],
            "keywords": ["첩보", "임무", "스파이"],
        },
        {
            "id": 12,
            "type": "movie",
            "title": "라이온 킹",
            "genre": ["애니메이션", "드라마"],
            "keywords": ["왕", "자연", "성장"],
        },
        {
            "id": 13,
            "type": "movie",
            "title": "반지의 제왕: 두 개의 탑",
            "genre": ["판타지", "어드벤처"],
            "keywords": ["중간계", "여정", "전쟁"],
        },
        {
            "id": 14,
            "type": "movie",
            "title": "범죄도시",
            "genre": ["액션", "범죄"],
            "keywords": ["형사", "소탕", "조직"],
        },
        {
            "id": 15,
            "type": "movie",
            "title": "포레스트 검프",
            "genre": ["드라마", "로맨스"],
            "keywords": ["성장", "삶", "사랑"],
        },
        {
            "id": 16,
            "type": "movie",
            "title": "스타워즈: 새로운 희망",
            "genre": ["SF", "어드벤처"],
            "keywords": ["은하", "영웅", "전쟁"],
        },
        {
            "id": 17,
            "type": "movie",
            "title": "아바타",
            "genre": ["SF", "어드벤처"],
            "keywords": ["외계", "에너지", "자연"],
        },
        {
            "id": 18,
            "type": "movie",
            "title": "매트릭스",
            "genre": ["액션", "SF"],
            "keywords": ["가상현실", "구원자", "미래"],
        },
        {
            "id": 19,
            "type": "movie",
            "title": "쇼생크 탈출",
            "genre": ["드라마", "범죄"],
            "keywords": ["희망", "자유", "우정"],
        },
        {
            "id": 20,
            "type": "movie",
            "title": "토이스토리",
            "genre": ["애니메이션", "코미디"],
            "keywords": ["장난감", "우정", "모험"],
        },

        # 공연 데이터 (15개)
        {
            "id": 21,
            "type": "performance",
            "title": "오페라의 유령",
            "genre": ["뮤지컬", "로맨스"],
            "keywords": ["음악", "사랑", "미스터리"],
        },
        {
            "id": 22,
            "type": "performance",
            "title": "캣츠",
            "genre": ["뮤지컬", "드라마"],
            "keywords": ["고양이", "뮤지컬", "삶"],
        },
        {
            "id": 23,
            "type": "performance",
            "title": "노트르담 드 파리",
            "genre": ["뮤지컬", "드라마"],
            "keywords": ["파리", "사랑", "비극"],
        },
        {
            "id": 24,
            "type": "performance",
            "title": "레미제라블",
            "genre": ["뮤지컬", "역사"],
            "keywords": ["혁명", "희생", "운명"],
        },
        {
            "id": 25,
            "type": "performance",
            "title": "맘마미아",
            "genre": ["뮤지컬", "코미디"],
            "keywords": ["음악", "가족", "결혼"],
        },
        {
            "id": 26,
            "type": "performance",
            "title": "지킬 앤 하이드",
            "genre": ["뮤지컬", "스릴러"],
            "keywords": ["이중성", "비극", "사랑"],
        },
        {
            "id": 27,
            "type": "performance",
            "title": "호두까기 인형",
            "genre": ["발레", "클래식"],
            "keywords": ["음악", "춤", "동화"],
        },
        {
            "id": 28,
            "type": "performance",
            "title": "라 트라비아타",
            "genre": ["오페라", "드라마"],
            "keywords": ["희생", "사랑", "비극"],
        },
        {
            "id": 29,
            "type": "performance",
            "title": "모차르트",
            "genre": ["뮤지컬", "역사"],
            "keywords": ["음악", "천재", "비극"],
        },
        {
            "id": 30,
            "type": "performance",
            "title": "베토벤 바이러스",
            "genre": ["클래식", "음악"],
            "keywords": ["오케스트라", "천재", "갈등"],
        },
        {
            "id": 31,
            "type": "performance",
            "title": "국립국악단 공연",
            "genre": ["전통음악", "국악"],
            "keywords": ["민속", "한국음악", "전통"],
        },
        {
            "id": 32,
            "type": "performance",
            "title": "백조의 호수",
            "genre": ["발레", "클래식"],
            "keywords": ["춤", "희생", "순수"],
        },
        {
            "id": 33,
            "type": "performance",
            "title": "카르멘",
            "genre": ["오페라", "드라마"],
            "keywords": ["열정", "운명", "사랑"],
        },
        {
            "id": 34,
            "type": "performance",
            "title": "누구를 위하여 종은 울리나",
            "genre": ["연극", "드라마"],
            "keywords": ["정의", "갈등", "역사"],
        },
        {
            "id": 35,
            "type": "performance",
            "title": "브람스 교향곡",
            "genre": ["클래식", "음악"],
            "keywords": ["교향곡", "감정", "깊이"],
        },

        # 전시 데이터 (15개)
        {
            "id": 36,
            "type": "exhibition",
            "title": "반 고흐: 영원한 여행자",
            "genre": ["미술", "회화"],
            "keywords": ["인상주의", "명화", "예술"],
        },
        {
            "id": 37,
            "type": "exhibition",
            "title": "모네와 지베르니",
            "genre": ["미술", "회화"],
            "keywords": ["인상주의", "풍경", "빛"],
        },
        {
            "id": 38,
            "type": "exhibition",
            "title": "르네상스 작품 특별전",
            "genre": ["미술", "고전"],
            "keywords": ["고전주의", "걸작", "역사"],
        },
        {
            "id": 39,
            "type": "exhibition",
            "title": "팀랩 디지털 아트전",
            "genre": ["미디어아트"],
            "keywords": ["디지털", "기술", "예술"],
        },
        {
            "id": 40,
            "type": "exhibition",
            "title": "이중섭 특별전",
            "genre": ["미술"],
            "keywords": ["한국화", "소외", "감성"],
        },
        {
            "id": 41,
            "type": "exhibition",
            "title": "한국 현대 사진전",
            "genre": ["사진"],
            "keywords": ["현대", "다큐", "감각"],
        },
        {
            "id": 42,
            "type": "exhibition",
            "title": "피카소와 큐비즘",
            "genre": ["미술", "큐비즘"],
            "keywords": ["큐비즘", "추상", "혁신"],
        },
        {
            "id": 43,
            "type": "exhibition",
            "title": "국립 박물관 특별전",
            "genre": ["역사", "고고학"],
            "keywords": ["유물", "역사", "발견"],
        },
        {
            "id": 44,
            "type": "exhibition",
            "title": "미래 디자인 전시회",
            "genre": ["디자인"],
            "keywords": ["미래", "창의", "산업"],
        },
        {
            "id": 45,
            "type": "exhibition",
            "title": "전통 공예 특별전",
            "genre": ["미술", "공예"],
            "keywords": ["전통", "수공예", "문화"],
        },
        {
            "id": 46,
            "type": "exhibition",
            "title": "건축의 미래",
            "genre": ["건축"],
            "keywords": ["건축", "공간", "지속가능"],
        },
        {
            "id": 47,
            "type": "exhibition",
            "title": "현대 설치미술의 세계",
            "genre": ["설치미술"],
            "keywords": ["공간", "예술", "현대"],
        },
        {
            "id": 48,
            "type": "exhibition",
            "title": "로댕과 조각 예술",
            "genre": ["조각"],
            "keywords": ["조각", "고전", "감정"],
        },
        {
            "id": 49,
            "type": "exhibition",
            "title": "미디어아트 스펙트럼",
            "genre": ["미디어아트"],
            "keywords": ["디지털", "미래", "경험"],
        },
        {
            "id": 50,
            "type": "exhibition",
            "title": "다빈치의 발명",
            "genre": ["과학", "미술"],
            "keywords": ["발명", "다빈치", "혁신"],
        },
    ]

    # 테스트용 사용자 프로필
    user_profile = UserProfile(
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
    
    
    # 알고리즘 실행
    recommender = RecommendationAlgorithm()
    recommendations = recommender.generate_recommendations(
        content_items, 
        user_profile
    )
    
    # 결과 출력
    for item in recommendations:
        print(f"추천 {item['type']}: {item['title']}")

if __name__ == "__main__":
    main()