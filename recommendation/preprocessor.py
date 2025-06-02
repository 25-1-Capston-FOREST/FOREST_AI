from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from enum import Enum
import logging
from sklearn.feature_extraction.text import TfidfVectorizer

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
        self._logger = logging.getLogger(__name__)
        self._vectorizer = TfidfVectorizer(
            max_features=1000,  # 차원 수 제한
            lowercase=True,     # 소문자 변환
            ngram_range=(1, 2),  # 단일 단어와 두 단어 조합 모두 사용
            token_pattern=r"(?u)\b\w+\b"
        )
        self._is_fitted = False  # vectorizer의 학습 여부 체크
        
    def preprocess_items(self, items: List[Dict]) -> Optional[Dict]:
        """
        아이템 데이터 전처리

        Args:
            items: 전처리할 아이템 리스트
        """
        try:
            processed_items = []
            texts = []

            for item in items:
                processed_text = self._preprocess_text(item)
                if processed_text:
                    texts.append(processed_text)
                    processed_items.append({
                        'activity_id': item.get('activity_id'),
                        'title': item.get('title'),
                        'genre_nm':item.get('genre'),
                        'keywords':item.get('keywords'),
                        'text': processed_text,
                        'content_type': item.get('content_type'),  # 필수!
                        'original': item
                    })

            if not processed_items:
                return None

            # vectorizer 학습 및 변환
            if not self._is_fitted:
                self._vectorizer.fit(texts)
                self._is_fitted = True

            vector = self._vectorizer.transform(texts)
            
            return {
                'items': processed_items,
                'vector': vector,
                'vectorizer': self._vectorizer
            }

        except Exception as e:
            self._logger.error(f"아이템 전처리 중 오류 발생: {str(e)}")
            return None
            
    def preprocess_user_data(self, user_profile: UserProfile, vectorizer: TfidfVectorizer = None) -> Optional[np.ndarray]:
        try:
            # 모든 장르와 키워드를 하나의 리스트로 결합
            all_preferences = (
                user_profile['movie_genre_preference'] +
                user_profile['performance_genre_preference'] +
                user_profile['exhibition_genre_preference'] +
                user_profile['like_words']
            )
            

            # 리스트를 문자열로 변환
            text_to_vectorize = ' '.join(all_preferences)
            
            self._logger.info(f"user_profile: {user_profile}")
            self._logger.info(f"all_preferences: {all_preferences}")
            self._logger.info(f"text_to_vectorize: '{text_to_vectorize}'")
            # vectorizer로 변환
            vector = vectorizer.transform([text_to_vectorize])
                
            # 희소 행렬을 밀집 배열로 변환
            vector = vector.toarray().squeeze()
                
            self._logger.info(f"생성된 사용자 벡터 shape: {vector.shape}")
            self._logger.info(f"벡터 통계 - 평균: {vector.mean():.4f}, 표준편차: {vector.std():.4f}")
                
            # 원본 데이터 복사 후 vector 항목 추가
            processed_user_data = user_profile.copy()
            processed_user_data['vector'] = vector  
            return processed_user_data

        except Exception as e:
            self._logger.error(f"사용자 데이터 전처리 중 오류 발생: {str(e)}")
            raise

    def _preprocess_text(self, item: Dict) -> str:
        """아이템 텍스트 전처리"""
        try:
            text_parts = []
            
            # 제목 처리 (가중치 부여 예시)
            if 'title' in item and item['title']:
                text_parts.extend([item['title'].lower()] * 2)

            # 설명 처리
            if 'description' in item and item['description']:
                text_parts.append(item['description'].lower())
                
            # 장르 처리
            if 'genre' in item and item['genre']:
                genres = item['genre'].split(',') if isinstance(item['genre'], str) else item['genre']
                text_parts.extend([genre.lower().strip() for genre in genres if genre.strip()])
                
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
            self._logger.error(f"텍스트 전처리 중 오류 발생: {str(e)}")
            return ''

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
