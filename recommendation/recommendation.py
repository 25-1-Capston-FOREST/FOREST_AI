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
import sys
sys.path.append('/home/ubuntu/FOREST_AI')
from database.user_queries import UserQueries
from database.item_queries import ItemQueries
from recommendation.preprocessor import DataPreprocessor, ContentType, UserProfile
#from preprocessor import DataPreprocessor, ContentType, UserProfile
import scipy.sparse as sp
from mysql.connector import Error as DatabaseError
from datetime import datetime


class RecommendationAlgorithm:
    def __init__(self):
        self._item_queries = ItemQueries()
        self._user_queries = UserQueries()
        self.preprocessor = DataPreprocessor()
        self.item_data = {}
        self.user_data = {}
        
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

    def prepare_item_data(self):
        """
        영화, 공연, 전시 데이터를 모두 가져오고 전처리하는 메서드
        
        Returns:
            Tuple[List[Dict], TfidfVectorizer]: 전처리된 모든 아이템 리스트와 vectorizer
        """
        try:
            # 1. ItemQueries를 통해 모든 데이터 가져오기
            movies = self._item_queries.get_movies_data(ContentType.MOVIE)
            performances = self._item_queries.get_performances_data()
            exhibitions = self._item_queries.get_exhibitions_data()

            # 데이터 검증
            item_count = len(movies)
            self._logger.info(f"[DB 조회 성공] 총 {item_count}개 아이템 조회됨")
            
            # 2. ItemPreprocessor를 통해 각각 전처리
            preprocessed_movies = self.preprocessor.preprocess_items(movies)
            preprocessed_performances = self.preprocessor.preprocess_items(performances)
            preprocessed_exhibitions = self.preprocessor.preprocess_items(exhibitions)

            # 전처리된 데이터 저장
            self.item_data[ContentType.MOVIE] = {
                'items': movies,
                'vector': preprocessed_movies['vector'],
                'vectorizer': preprocessed_movies['vectorizer'],
                'last_updated': datetime.now()
            }
            
            self.item_data[ContentType.PERFORMANCE] = {
                'items': performances,
                'vector': preprocessed_performances['vector'],
                'vectorizer': preprocessed_performances['vectorizer'],
                'last_updated': datetime.now()
            }
            
            self.item_data[ContentType.EXHIBITION] = {
                'items': exhibitions,
                'vector': preprocessed_exhibitions['vector'],
                'vectorizer': preprocessed_exhibitions['vectorizer'],
                'last_updated': datetime.now()
            }

            self._logger.info(f"전체 아이템 준비 완료 (영화: {len(movies)}개, 공연: {len(performances)}개, 전시: {len(exhibitions)}개)")
            
            # 모든 아이템을 하나의 리스트로 통합
            all_items = []
            for content_type, data in self.item_data.items():
                items = data['items']
                vector = data['vector']
                for item, vector in zip(items, vector):
                    all_items.append({
                        'title': item['title'],
                        'content_type': content_type.value,
                        'vector': vector,
                        **item  # 기존 아이템의 다른 속성들도 포함
                    }) 

            # vectorizer는 어떤 컨텐츠 타입의 것을 사용해도 동일하므로, 
            # 예를 들어 영화 데이터의 vectorizer를 반환
            return all_items, self.item_data[ContentType.MOVIE]['vectorizer']
        
        except DatabaseError as db_err:
            self._logger.error(f"데이터베이스 오류 발생: {str(db_err)}")
            return False
        except Exception as e:
            self._logger.error(f"아이템 데이터 준비 중 오류 발생: {str(e)}")
            raise

    def prepare_user_data(self, user_id: int,vectorizer) -> bool:
        """
        데이터베이스에서 사용자 데이터를 가져와서 전처리
        """
        try:
            # 1. 데이터베이스에서 사용자 데이터 가져오기
            raw_user_data = self._user_queries.get_user_preferences(user_id)
            if not raw_user_data:
                self._logger.warning(f"사용자 ID {user_id}에 대한 데이터를 찾을 수 없습니다.")
                return False

            # 2. 사용자 데이터 전처리
            processed_user_data = self.preprocessor.preprocess_user_data(raw_user_data,vectorizer)
            if processed_user_data is None:
                self._logger.warning("사용자 데이터 전처리 실패")
                return False

            # 3. 처리된 사용자 데이터 저장
            self.user_data[user_id] = {
                #'profile': processed_user_data['profile'],
                'vector': processed_user_data['vector'],
                'last_updated': datetime.now()
            }

            self._logger.info(f"사용자 ID {user_id}의 데이터 준비 완료")
            return self.user_data

        except Exception as e:
            self._logger.error(f"사용자 데이터 준비 중 오류 발생: {str(e)}")
            return False



    def calculate_similarity(self, user_vector, item_vectors):
        """
        사용자 벡터와 아이템 벡터들 간의 코사인 유사도 계산
        
        Args:
            user_vector: 사용자 벡터 (sparse 또는 dense)
            item_vectors: 아이템 벡터들 (sparse 또는 dense)
        
        Returns:
            np.ndarray: 유사도 점수 배열
        """
        try:
            # 입력 데이터 로깅
            self._logger.debug("=== 입력 데이터 정보 ===")
            self._logger.debug(f"user_vector 타입: {type(user_vector)}")
            self._logger.debug(f"item_vectors 타입: {type(item_vectors)}")

            # Sparse matrix 처리
            if sp.issparse(user_vector):
                self._logger.debug("user_vector를 dense matrix로 변환")
                user_vector = user_vector.toarray()
            if sp.issparse(item_vectors):
                self._logger.debug("item_vectors를 dense matrix로 변환")
                item_vectors = item_vectors.toarray()

            # numpy 배열로 변환
            try:
                user_vector = np.array(user_vector, dtype=np.float32)
                item_vectors = np.array(item_vectors, dtype=np.float32)
            except Exception as e:
                self._logger.error(f"벡터 변환 중 오류: {str(e)}")
                raise ValueError(f"벡터 변환 실패: {str(e)}")

            # 변환 후 데이터 확인
            self._logger.debug("=== 변환 후 데이터 정보 ===")
            self._logger.debug(f"user_vector shape: {user_vector.shape}")
            self._logger.debug(f"item_vectors shape: {item_vectors.shape}")

            # 1차원 벡터의 경우 2D로 reshape
            if len(user_vector.shape) == 1:
                user_vector = user_vector.reshape(1, -1)
            
            # 차원 확인
            if len(user_vector.shape) != 2:
                raise ValueError(f"잘못된 user_vector 차원: {user_vector.shape}")
            if len(item_vectors.shape) != 2:
                raise ValueError(f"잘못된 item_vectors 차원: {item_vectors.shape}")

            # nan/inf 체크
            if np.any(np.isnan(user_vector)) or np.any(np.isinf(user_vector)):
                raise ValueError("user_vector에 nan/inf 값이 있습니다")
            if np.any(np.isnan(item_vectors)) or np.any(np.isinf(item_vectors)):
                raise ValueError("item_vectors에 nan/inf 값이 있습니다")

            # 코사인 유사도 계산
            similarities = cosine_similarity(user_vector, item_vectors)
            
            self._logger.debug(f"계산된 유사도 shape: {similarities.shape}")
            self._logger.info("유사도 계산 완료")
            
            return similarities.ravel()
            
        except ValueError as ve:
            error_msg = f"벡터 처리 중 오류 발생: {str(ve)}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"유사도 계산 중 오류 발생: {str(e)}"
            self._logger.error(error_msg)
            raise Exception(error_msg)
                
        except ValueError as ve:
            error_msg = f"벡터 처리 중 오류 발생: {str(ve)}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"유사도 계산 중 오류 발생: {str(e)}"
            self._logger.error(error_msg)
            raise Exception(error_msg)
    
    
    def _calculate_final_scores(self, 
                              similarities: np.ndarray, 
                              content_type: ContentType,
                              user_profile: UserProfile) -> np.ndarray:
        """최종 추천 점수 계산"""
        try:
            # 해당 타입에 대한 사용자 선호도 (0-10 스케일을 0-1로 정규화)
            type_preference = user_profile.type_preferences.get(content_type, 0) / 10.0
            
            # 최종 점수 계산
            final_scores = (
                similarities * self._similarity_weight +
                type_preference * self._preference_weight
            )
            
            return final_scores
            
        except Exception as e:
            self._logger.error(f"최종 점수 계산 중 오류 발생: {str(e)}")
            return np.zeros_like(similarities)

    def get_recommendations(self, user_id: int) -> Dict[str, List[Dict]]:
        """
        사용자에게 컨텐츠 타입별 추천 아이템을 반환하는 함수
        """
        try:
            # 테스트용 사용자 데이터
            user_profile = {
                'user_id': user_id,
                'movie_preference': 7,
                'performance_preference': 5,
                'exhibition_preference': 3,
                'movie_genre_preference': [
                    '액션', '드라마', '로맨스', '코미디', '스릴러'
                ],
                'performance_genre_preference': [
                    '뮤지컬', '연극', '콘서트', '클래식'
                ],
                'exhibition_genre_preference': [
                    '미술', '사진', '설치미술', '현대미술'
                ],
                'like_words': [
                    '감동', '재미', '스릴', '로맨틱', '예술', '생존'
                ],
                'vector':[
                    '액션', '드라마', '로맨스', '코미디', '스릴러',
                    '뮤지컬', '연극', '콘서트', '클래식',
                    '미술', '사진', '설치미술', '현대미술',
                    '감동적인', '재미있는', '스릴있는', '로맨틱한', '예술적인'
                ]

            }

            # 아이템 데이터 준비
            # 모든 컨텐츠 타입의 아이템을 하나의 리스트로 통합
            all_items,vectorizer = self.prepare_item_data()
            all_item_vectors = []
            #print(all_items)
            if not all_items:
                self._logger.error("추천할 아이템 데이터가 없습니다.")
                return []

            #processed_user_data = self.preprocessor.preprocess_user_data(user_profile,vectorizer)
            processed_user_data = self.prepare_user_data(user_id, vectorizer)


            if processed_user_data is None:
                self._logger.warning("사용자 데이터 전처리 실패")
                return False

            self.user_data[user_id] = {
                'vector': processed_user_data[user_id]['vector'],
                'last_updated': datetime.now()
            }
            self._logger.info(f"사용자 ID {user_id}의 데이터 준비 완료1")
            
            # for content_type in ContentType:
            #     items = self.item_data.get(content_type, [])
            #     for item in items:
            #         all_items.append({
            #             'id': item['id'],
            #             'title': item['title'],
            #             'content_type': content_type.value,
            #             'vector': item['vector']  # 전처리된 아이템 벡터
            #         })
            #         all_item_vectors.append(item['vector'])


            self._logger.info(f"\n=== 전체 아이템 데이터 로드 완료 (총 {len(all_items)}개) ===")
            
            # 컨텐츠 타입별 아이템 수 로깅
            type_counts = {}
            for item in all_items:
                type_counts[item['content_type']] = type_counts.get(item['content_type'], 0) + 1
            
            for content_type, count in type_counts.items():
                self._logger.info(f"{content_type}: {count}개 아이템")

            # try:
                # # NumPy 배열로 변환
                # user_vector = self.user_data[user_id]['vector']  # 전처리된 사용자 벡터
                # # item_vector = np.array([item['vector'] for item in all_items])
                
                # # 모든 아이템의 벡터를 하나의 행렬로 구성 (n_items x 310)
                # item_vectors = item['vector']
                
                # # 벡터 shape 로깅
                # self._logger.debug(f"User vector shape: {user_vector.shape}")
                # self._logger.debug(f"Combined item vectors shape: {item_vectors.shape}")
                
                # # 차원 확인
                # if user_vector.shape[0] != item_vectors.shape[1]:
                #     raise ValueError(
                #         f"벡터 차원 불일치: user_vector({user_vector.shape}) vs "
                #         f"item_vectors({item_vectors.shape})"
                #     )

                # # 코사인 유사도 계산
                # similarities = self.calculate_similarity(user_vector, item_vectors)
                
                # # 유사도 점수로 정렬된 아이템 리스트 생성
                # scored_items = []
                # for idx, score in enumerate(similarities):
                #     item_copy = all_items[idx].copy()
                #     item_copy['similarity_score'] = float(score)
                #     scored_items.append(item_copy)

                # # 점수 기준 내림차순 정렬
                # sorted_items = sorted(scored_items, key=lambda x: x['similarity_score'], reverse=True)

                # # 로그 출력 (상위 10개 아이템)
                # self._logger.info("\n=== 추천 결과 (상위 10개) ===")
                # for idx, item in enumerate(sorted_items[:10], 1):
                #     self._logger.info(
                #         f"{idx}. [{item['content_type']}] {item['title']} "
                #         f"(유사도: {item['similarity_score']:.3f})"
                #     )

                # return sorted_items

            try:
                self._logger.info(f"전체 아이템 수: {len(all_items)}")
                recommendations = []
                user_vector = self.user_data[user_id]['vector']  # 전처리된 사용자 벡터
                # 사용자 벡터 전처리
                if sp.issparse(user_vector):
                    user_vector = user_vector.toarray()
                if len(user_vector.shape) == 1:
                    user_vector = user_vector.reshape(1, -1)

                # 각 아이템별 유사도 계산
                for idx, item in enumerate(all_items, 1):
                    try:
                        item_vector = item['vector']
                        if sp.issparse(item_vector):
                            item_vector = item_vector.toarray()

                        # 유사도 계산
                        similarity = cosine_similarity(user_vector, item_vector)[0][0]

                        # 추천 아이템 정보 구성
                        recommendation = {
                           'activity_id': item['activity_id'],
                            'title': item['title'],
                            'content_type': item['content_type'],
                            'genre_nm': item.get('genre_nm', ''),
                            'director': item.get('director', ''),
                            'actors': item.get('actors', ''),
                            'keywords': item.get('keywords', ''),
                            'similarity': float(similarity)
                        }
                            
                        recommendations.append(recommendation)
                            
                        if idx % 100 == 0:  # 처리 진행상황 로깅
                            self._logger.debug(f"진행 중: {idx}/{len(all_items)} 아이템 처리 완료")

                    except Exception as e:
                        self._logger.error(f"아이템 {idx} 처리 중 오류: {str(e)}")
                        continue

                # 유사도 기준 내림차순 정렬
                recommendations.sort(key=lambda x: x['similarity'], reverse=True)

                # 상위 추천 결과 로깅
                self._logger.info("=== 상위 추천 결과 ===")
                for idx, item in enumerate(recommendations[:50], 1):
                    self._logger.info(
                        f"{idx}. {item['title']} "
                        f"(유사도: {item['similarity']:.4f}, "
                        f"장르: {item['genre_nm']})"
                    )

                # ID만 추출하여 리스트로 반환
                recommendations.sort(key=lambda x: x['similarity'], reverse=False)
                recommendation_list = [item['activity_id'] for item in recommendations[:50]]

                return recommendation_list

            except Exception as e:
                self._logger.error(f"추천 계산 중 오류 발생: {str(e)}")
                raise
        except Exception as e:
            self._logger.error(f"추천 생성 중 오류 발생: {str(e)}")
            return []


    # def _get_recommendations(self, user_id: int) -> Dict[str, List[Dict]]:
    #     """
    #     사용자에게 컨텐츠 타입별 추천 아이템을 반환하는 함수
        
    #     Args:
    #         user_id (int): 사용자 ID
        
    #     Returns:
    #         Dict[str, List[Dict]]: 컨텐츠 타입별 추천 아이템 리스트
    #     """
    #     try:
    #         # 사용자 데이터 준비
    #         #user_data = self.prepare_user_data(user_id)
    #         #if not user_data:
    #         #    print(f"사용자 ID {user_id}에 대한 데이터를 찾을 수 없습니다.")
    #         #    return {}
    #         user_data = {
    #             'user_id': user_id,
    #             'movie_preference': 7,  # 각 컨텐츠 타입에 대한 선호도
    #             'performance_preference': 5,
    #             'exhibition_preference': 3,
    #             'movie_genre_preference': [
    #                 '액션',
    #                 '드라마', 
    #                 '로맨스',
    #                 '코미디',
    #                 '스릴러'
    #             ],
    #             'performance_genre_preference': [
    #                 '뮤지컬',
    #                 '연극',
    #                 '콘서트',
    #                 '클래식'
    #             ],
    #             'exhibition_genre_preference': [
    #                 '미술',
    #                 '사진',
    #                 '설치미술',
    #                 '현대미술'
    #             ],
    #             'like_words': [
    #                 '감동적인',
    #                 '재미있는',
    #                 '스릴있는',
    #                 '로맨틱한',
    #                 '예술적인'
    #             ]
    #         }

    #         recommendations = {}
    #         content_types = ["movie", "performance", "exhibition"]
    #         all_recommendations = []  # 모든 컨텐츠의 추천 아이템을 저장할 리스트

    #         for content_type in content_types:
    #             # 아이템 데이터 준비
    #             items = self.prepare_item_data()
    #             if not items:
    #                 print(f"{content_type}에 대한 아이템 데이터가 없습니다.")
    #                 recommendations[content_type] = []
    #                 continue

    #             # 유사도 계산
    #             similarities = self.calculate_similarity(user_data, items)
    #             if not similarities:
    #                 print(f"{content_type}에 대한 유사도 계산 실패")
    #                 recommendations[content_type] = []
    #                 continue

    #             # 최종 점수 계산
    #             final_scores = self._calculate_final_scores(items, similarities)
                
    #             # 모든 아이템에 대한 정보와 점수 저장
    #             scored_items = []
    #             for item_id, score in final_scores.items():
    #                 item = next((item for item in items if item['id'] == item_id), None)
    #                 if item:
    #                     item['recommendation_score'] = score
    #                     item['content_type'] = content_type
    #                     scored_items.append(item)
                
    #             # 컨텐츠 타입별로 저장
    #             recommendations[content_type] = scored_items
    #             all_recommendations.extend(scored_items)

    #         # 결과 출력
    #         print("\n=== 추천 결과 ===")
    #         print("-" * 50)
    #         for content_type, items in recommendations.items():
    #             print(f"\n[{content_type.upper()}]")
    #             if items:
    #                 sorted_items = sorted(items, key=lambda x: x['recommendation_score'], reverse=True)
    #                 for idx, item in enumerate(sorted_items, 1):
    #                     print(f"\n{idx}. 제목: {item['title']}")
    #                     print(f"타입: {item['content_type']}")
    #                     print(f"추천 점수: {item['recommendation_score']:.2f}")
    #             else:
    #                 print("추천 항목 없음")
    #             print("-" * 50)

    #         return recommendations

    #     except Exception as e:
    #         print(f"추천 생성 중 오류 발생: {str(e)}")
    #         return {}


    def api_test_recommendation(self, user_id):
        try:
            if user_id == "1":
                items = [12, 121, 31, 123]
            else:
                items = []
            return items
        
        except Exception as e:
            print(f"api test error: {str(e)}")

def main():
    user_id = 1
    recommender = RecommendationAlgorithm()
    recommender.get_recommendations(user_id)


if __name__ == "__main__":
    main()



# def test_recommendation_system():
#     """추천 시스템 테스트"""
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger(__name__)
    
#     try:
#         # 추천 시스템 초기화
#         recommender = RecommendationAlgorithm()

#         # 테스트 데이터
#         test_items = {
#             ContentType.MOVIE: [
#                 {
#                     'activity_id': 'mov1',
#                     'title': '인셉션',
#                     'genre_nm': '액션,SF',
#                     'director': '크리스토퍼 놀란',
#                     'actors': '레오나르도 디카프리오,조셉 고든 레빗',
#                     'keywords': '꿈,현실,시간'
#                 },
#                 {
#                     'activity_id': 'mov2',
#                     'title': '다크 나이트',
#                     'genre_nm': '액션,범죄,드라마',
#                     'director': '크리스토퍼 놀란',
#                     'actors': '크리스찬 베일,히스 레저',
#                     'keywords': '배트맨,범죄,액션'
#                 }
#             ],
#             ContentType.PERFORMANCE: [
#                 {
#                     'activity_id': 'perf1',
#                     'title': '오페라의 유령',
#                     'genre_nm': '뮤지컬',
#                     'director': '앤드류 로이드 웨버',
#                     'actors': '벤 크로포드,사라 브라이트만',
#                     'keywords': '뮤지컬,로맨스,드라마'
#                 }
#             ],
#             ContentType.EXHIBITION: [
#                 {
#                     'activity_id': 'ex1',
#                     'title': '반 고흐 전시회',
#                     'genre_nm': '미술,서양화',
#                     'director': '',
#                     'actors': '빈센트 반 고흐',
#                     'keywords': '인상주의,유화,미술사'
#                 }
#             ]
#         }

#         print("\n=== 데이터 전처리 테스트 ===")
#         # 각 컨텐츠 타입별 데이터 준비
#         for content_type, items in test_items.items():
#             print(f"\n{content_type.value} 데이터 처리 중...")
#             success = recommender.prepare_item_data(items, content_type)
#             if success:
#                 print(f"- {len(items)}개 아이템 처리 완료")
                
#                 # 벡터 정보 출력
#                 item_data = recommender.item_data[content_type]
#                 print(f"- 벡터 shape: {item_data['vectors'].shape}")
                
#                 # 전처리된 텍스트 출력
#                 print("\n처리된 텍스트 샘플:")
#                 for item in item_data['items'][:2]:  # 처음 2개만 출력
#                     print(f"제목: {item['original']['title']}")
#                     print(f"텍스트: {item['text']}\n")

#         # 테스트용 사용자 프로필
#         user_profile = UserProfile(
#             keywords=['액션', 'SF', '미술'],
#             type_preferences={
#                 ContentType.MOVIE: 8,
#                 ContentType.PERFORMANCE: 5,
#                 ContentType.EXHIBITION: 7
#             },
#             genre_preferences={
#                 ContentType.MOVIE: ['액션', 'SF', '드라마'],
#                 ContentType.PERFORMANCE: ['뮤지컬', '연극'],
#                 ContentType.EXHIBITION: ['미술', '서양화']
#             }
#         )

#         print("\n=== 추천 결과 테스트 ===")
#         recommendations = recommender.get_recommendations(user_profile, n_recommendations=5)
        
#         print("\n추천 아이템 목록:")
#         for i, rec in enumerate(recommendations, 1):
#             print(f"\n{i}. {rec['title']}")
#             print(f"- 컨텐츠 타입: {rec['content_type']}")
#             print(f"- 유사도 점수: {rec['similarity_score']:.4f}")
#             print(f"- 최종 점수: {rec['final_score']:.4f}")

#     except Exception as e:
#         logger.error(f"테스트 중 오류 발생: {str(e)}")
#         raise

# if __name__ == "__main__":
    # test_recommendation_system()