# preprocessor.py
from dataclasses import dataclass
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
from enum import Enum

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

class DataPreprocessor:
    def __init__(self):
        self._vectorizer = TfidfVectorizer(
            analyzer='word',
            token_pattern=r'\w+',
            max_features=5000,
            ngram_range=(1, 2)
        )

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

    def preprocess_items(self, items: List[Dict], content_type: ContentType):
        """아이템 데이터 전처리 및 벡터화"""
        try:
            # 아이템 데이터 전처리
            processed_items = []
            for item in items:
                processed_text = self._preprocess_item(item)
                if processed_text:
                    processed_items.append({
                        'id': item['activity_id'],
                        'text': processed_text,
                        'original': item
                    })

            if not processed_items:
                logging.warning(f"No valid item data for type: {content_type.value}")
                return None

            # 텍스트 데이터 벡터화
            texts = [item['text'] for item in processed_items]
            vectors = self._vectorizer.fit_transform(texts)

            return {
                'vectors': vectors,
                'items': processed_items,
                'vectorizer': self._vectorizer
            }

        except Exception as e:
            logging.error(f"Error preprocessing items: {str(e)}")
            return None

    def _preprocess_item(self, item: Dict) -> str:
        """개별 아이템 데이터 전처리"""
        try:
            text_parts = []

            # 장르 처리
            if 'genre_nm' in item and item['genre_nm']:
                text_parts.append(item['genre_nm'].lower())

            # 감독/작가 처리
            if 'director' in item and item['director']:
                text_parts.append(item['director'].lower())

            # 배우/참여자 처리
            if 'actors' in item and item['actors']:
                actors = item['actors'].split(',') if isinstance(item['actors'], str) else item['actors']
                text_parts.extend([actor.lower().strip() for actor in actors if actor.strip()])

            # 키워드 처리
            if 'keywords' in item and item['keywords']:
                keywords = item['keywords'].split(',') if isinstance(item['keywords'], str) else item['keywords']
                text_parts.extend([keyword.lower().strip() for keyword in keywords if keyword.strip()])

            return ' '.join(text_parts)

        except Exception as e:
            logging.error(f"Error preprocessing item: {str(e)}")
            return ''

    def preprocess_user_profile(self, user_profile: UserProfile, content_type: ContentType, vectorizer: TfidfVectorizer):
        """사용자 프로필 전처리 및 벡터화"""
        try:
            # 사용자 키워드 및 장르 결합
            user_terms = []
            
            # 키워드 처리
            user_terms.extend([keyword.lower() for keyword in user_profile.keywords])
            
            # 해당 컨텐츠 타입의 장르 선호도 처리
            if content_type in user_profile.genre_preferences:
                for genre in user_profile.genre_preferences[content_type]:
                    user_terms.extend([genre.lower()])

            user_text = ' '.join(user_terms)
            user_vector = vectorizer.transform([user_text])

            return user_vector

        except Exception as e:
            logging.error(f"Error preprocessing user profile: {str(e)}")
            return None