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
import scipy.sparse as sp
from mysql.connector import Error as DatabaseError
from datetime import datetime

## surprise
# from surprise import Dataset, Reader, SVD
# from surprise.model_selection import train_test_split
# import pandas as pd
# from database.rating_queries import RatingQueries


class RecommendationAlgorithm:
    def __init__(self):

        self._item_queries = ItemQueries()
        self._user_queries = UserQueries()
        # self._rating_queries = RatingQueries()
        self.preprocessor = DataPreprocessor()

        self.item_data = {}
        self.user_data = {}
        
        self._logger = logging.getLogger(__name__)
        self._setup_logger()

    def _setup_logger(self) -> None:
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )


    def _prepare_item_data(self):
        """
        영화, 공연, 전시 데이터를 모두 가져오고 전처리하는 메서드
        
        Returns:
            Tuple[List[Dict], TfidfVectorizer]: 전처리된 모든 아이템 리스트와 vectorizer
        """
        try:
            self._logger.info(f"아이템 데이터 가져오기")
            # 1. ItemQueries를 통해 모든 데이터 가져오기
            movies = self._item_queries.get_movies_data(ContentType.MOVIE)
            performances = self._item_queries.get_performances_data()
            exhibitions = self._item_queries.get_exhibitions_data()

            # 데이터 검증
            item_count = len(movies) + len(performances) + len(exhibitions)
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
    
    def prepare_item_data(self):
        try:
            self._logger.info("아이템 데이터 가져오기")
            movies = self._item_queries.get_movies_data(ContentType.MOVIE)
            performances = self._item_queries.get_performances_data()
            exhibitions = self._item_queries.get_exhibitions_data()
            
            all_items = []
            for item in movies:
                item['content_type'] = ContentType.MOVIE.value
                all_items.append(item)
            for item in performances:
                item['content_type'] = ContentType.PERFORMANCE.value
                all_items.append(item)
            for item in exhibitions:
                item['content_type'] = ContentType.EXHIBITION.value
                all_items.append(item)
            
            self._logger.info(f"[DB 조회 성공] 총 {len(all_items)}개 아이템 통합")

            # 전처리
            processed = self.preprocessor.preprocess_items(all_items)
            if not processed:
                self._logger.error("전처리 결과 없음")
                raise ValueError("전처리 실패")
            
            processed_items = processed['items']
            vectors = processed['vector']
            vectorizer = processed['vectorizer']
            
            if len(all_items) != len(processed_items):
                self._logger.error(
                    f"전처리 결과 길이 불일치: all_items({len(all_items)}) vs processed_items({len(processed_items)})"
                )
                raise ValueError("전처리 결과와 아이템 개수가 일치하지 않습니다.")
            
            # 기존 all_items 대신 processed_items를 사용하거나,
            # 기존 동작과 맞추려면 vectors를 all_items의 해당 인덱스에 붙이기
            for idx, item in enumerate(processed_items):
                item['vector'] = vectors[idx]
            
            self._logger.info("전체 아이템 준비 및 벡터라이징 완료")
            return processed_items, vectorizer

        except Exception as e:
            self._logger.error(f"아이템 데이터 준비 중 오류 발생: {str(e)}")
            raise

    def prepare_user_data(self, user_id: int,vectorizer) -> bool:
        """
        데이터베이스에서 사용자 데이터를 가져와서 전처리
        """
        try:
            # 1. 데이터베이스에서 사용자 데이터 가져오기
            self._logger.info(f"사용자 ID {user_id}의 데이터 DB에서 가져오기")
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

    # def get_ratings_data(self):
    #     """
    #     Surprise 모델 학습에 사용할 데이터셋을 준비합니다.
    #     사용자-아이템-평점 데이터를 pandas.DataFrame 형태로 반환해야 합니다.
    #     """
    #     try:
    #         # 사용자의 평점 데이터를 가져옵니다.
    #         # 이 데이터는 반드시 [user_id, item_id, rating] 형식을 따릅니다.
    #         ratings = self._rating_queries.get_ratings_data()  # 사용자 평점 데이터 가져오는 함수
    #         if ratings is None or ratings.empty:
    #             raise ValueError("평점 데이터가 비어 있습니다.")

    #         self._logger.info(f"Surprise 데이터 준비 완료: {len(ratings)}개의 평점 데이터")
    #         return ratings
    #     except Exception as e:
    #         self._logger.error(f"Surprise 데이터 준비 중 오류: {str(e)}")
    #         return None



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
        사용자에게 추천 아이템을 반환하는 함수
        """
        try:
            self._logger.info(f"사용자 ID {user_id} 추천 시작")

            # 아이템 데이터 준비
            # 모든 컨텐츠 타입의 아이템을 하나의 리스트로 통합
            self._logger.info(f"아이템 데이터 준비")
            all_items,vectorizer = self.prepare_item_data()
            all_item_vectors = []
            if not all_items:
                self._logger.error("추천할 아이템 데이터가 없습니다.")
                return []

            self._logger.info(f"유저 데이터 전처리")
            processed_user_data = self.prepare_user_data(user_id, vectorizer)
            if processed_user_data is None:
                self._logger.warning("사용자 데이터 전처리 실패")
                return False

            self.user_data[user_id] = {
                'vector': processed_user_data[user_id]['vector'],
                'last_updated': datetime.now()
            }

            self._logger.info(f"사용자 ID {user_id}의 데이터 준비 완료1")

            self._logger.info(f"\n=== 전체 아이템 데이터 로드 완료 (총 {len(all_items)}개) ===")

            ## 협력 필터링 추천 알고리즘 코드
            # # SVD 모델 준비
            # self._logger.info("SVD 학습 데이터 준비")
            # ratings_data = self.get_ratings_data()
            # if ratings_data is None:
            #     self._logger.error("사용자-아이템 평점 데이터가 없습니다.")
            #     return []
            
            # reader = Reader(rating_scale=(1, 5))
            # surprise_dataset = Dataset.load_from_df(ratings_data[['user_id','activity_id','rating']], reader)
            # trainset, testset = train_test_split(surprise_dataset, test_size=0.2)

            # # SVD 모델 학습
            # self._logger.info("SVD 모델 학습 시작")
            # svd_model = SVD()
            # svd_model.fit(trainset)
            # self._logger.info("SVD 모델 학습 완료")

            # 아이템 유사도 검사 테스트 용 로그 코드            
            # self._logger.info(f"all_items 샘플 구조 체크 시작")
            # for idx, item in enumerate(all_items[:10]):
            #     self._logger.info(f"샘플 {idx} : {item}")

            # 컨텐츠 타입별 아이템 수 로깅
            type_counts = {}
            for item in all_items:
                if 'content_type' not in item:
                    self._logger.error(f"content_type이 누락된 아이템 발견: {item.get('activity_id', 'id없음')}")
                    continue
                type_counts[item['content_type']] = type_counts.get(item['content_type'], 0) + 1
            
            for content_type, count in type_counts.items():
                self._logger.info(f"{content_type}: {count}개 아이템")

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
                        
                        # # SVD 모델을 사용하여 예측 평점 계산
                        # activity_id = item['activity_id']
                        # predicted_rating = svd_model.predict(user_id, activity_id)

                        # 추천 아이템 정보 구성
                        recommendation = {
                           'activity_id': item['activity_id'],
                            'title': item['title'],
                            'content_type': item['content_type'],
                            'genre_nm': item.get('genre_nm', ''),
                            'keywords': item.get('keywords', ''),
                            'similarity': float(similarity),
                            # 'predicted_rating': predicted_rating  # 예측 평점
                        }
                            
                        recommendations.append(recommendation)
                            
                        if idx % 100 == 0:  # 처리 진행상황 로깅
                            self._logger.debug(f"진행 중: {idx}/{len(all_items)} 아이템 처리 완료")

                    except Exception as e:
                        self._logger.error(f"아이템 {idx} 처리 중 오류: {str(e)}")
                        continue

                # 유사도 기준 내림차순 정렬
                recommendations.sort(key=lambda x: (-x['similarity'], x['activity_id']))
        
                # # 유사도와 예측 평점 기준 내림차순 정렬 - 예측 평점 우선
                # recommendations.sort(key=lambda x: (-x['predicted_rating'], -x['similarity'], x['activity_id']))

                # 상위 추천 결과 로깅
                self._logger.info("=== 상위 추천 결과 ===")
                for idx, item in enumerate(recommendations[:50], 1):
                    self._logger.info(
                        f"{idx}. {item['title']} "
                        f"{item['activity_id']} "
                        f"(유사도: {item['similarity']:.4f}, "
                        f"장르: {item['genre_nm']})"
                    )

                # ID만 추출하여 리스트로 반환
                recommendations.sort(key=lambda x: x['similarity'], reverse=True)
                recommendation_list = [item['activity_id'] for item in recommendations[:50]]
                return recommendation_list

            except Exception as e:
                self._logger.error(f"추천 계산 중 오류 발생: {str(e)}")
                raise
        except Exception as e:
            self._logger.error(f"추천 생성 중 오류 발생: {str(e)}")
            return []

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
