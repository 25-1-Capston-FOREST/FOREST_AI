## 추천 알고리즘 메인 코드
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
import json
from enum import Enum
from dataclasses import dataclass
import re

file_path = "/data/demo_date.json"

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

    # 1. JSON 파일 로드
    def load_json_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    # 2. JSON 데이터를 텍스트로 변환
    def json_to_text(json_data):
        # 모든 키워드를 하나의 문자열로 합침
        if isinstance(json_data, dict):
            return ' '.join([str(v) for v in json_data.values()])
        elif isinstance(json_data, list):
            return ' '.join([str(item) for item in json_data])
        return str(json_data)

    def _data_preprocessing(self):
        ## movie - title, genre_nm, director, actors, keywords
        ## performance - title, cast, genre, keywords
        ## exhibition - title, exhibition_genre, keywords

        try:
            processed_data = 1
            return processed_data
        except Exception as e:
            self._logger.error(f"데이터 전처리 중 오류 발생: {str(e)}")
            return ""
        
        
        

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
        
    def api_test_recommendation(self, user_id):
        try:
            if user_id == "12345":
                items = [123, 1231, 121, 1222]
            else:
                items = []
            return items
        
        except Exception as e:
            print(f"api test error: {str(e)}")

def main():

    content_items = []

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