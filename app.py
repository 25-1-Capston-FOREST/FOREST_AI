## Flask 기반의 API 서버 메인 파일
## 클라이언트 요청 수신 -> 추천 알고리즘 모듈과 연동해 서버로 추천 결과 반환

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from recommendation.recommendation import RecommendationAlgorithm
from database.user_queries import UserQueries
from database.item_queries import ItemQueries

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 인스턴스 생성&초기화
user_queries = UserQueries()
item_queries = ItemQueries()
recommender = RecommendationAlgorithm()
logging.info("RecommendationAlgorithm 인스턴스 생성 완료")

@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    try:
        logging.info("recommendations 엔드포인트 호출됨")
        data = request.get_json()   # Request body에서 JSON 데이터 가져오기
        logging.debug(f"수신된 데이터: {data}")
        
        # user_id 검증
        if not data or 'user_id' not in data:
            # user_id 없는 경우 400 에러 처리
            return jsonify({
                "status": "error",
                "message": "유효하지 않은 사용자 ID입니다."
            }), 400
        
        user_id = data['user_id']
        logging.info(f"처리 중인 user_id: {user_id}")

        # 추천 목록 생성
        try:
            logging.info("추천 알고리즘 실행 시작")
            recommendation_list = recommender.get_recommendations(user_id)
            logging.info(f"추천 결과 생성됨: {recommendation_list}")
            
            if len(recommendation_list) > 0:
                return jsonify({
                    "status": "success",
                    "recommendations": recommendation_list,
                    "message": "추천 상품 목록을 성공적으로 가져왔습니다."
                })
            else:
                return jsonify({
                    "status": "fail",
                    "recommendations": [],
                    "message": "추천 상품 목록이 없습니다."
                })

        except Exception as e:
            logging.error(f"추천 생성 중 오류 발생: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"추천 생성 중 오류 발생: {str(e)}"
            }),500

        # # 테스트 용 코드
        # if user_id == "1":
        #     logging.debug("테스트 사용자 ID 감지됨")
        #     try:
        #         logging.info("추천 알고리즘 실행 시작")
        #         recommendations = [13, 1234 ,125, 654]
        #         #recommendations = recommender.api_test_recommendation(user_id)
        #         logging.info(f"추천 결과 생성됨: {recommendations}")
        #         return jsonify({
        #             "status": "success",
        #             "recommendations": recommendations,
        #             "message": "추천 상품 목록을 성공적으로 가져왔습니다."
        #         })
        #     except Exception as e:
        #         logging.error(f"추천 생성 중 오류 발생: {str(e)}")
        #         return jsonify({
        #             "status": "error",
        #             "message": f"추천 생성 중 오류 발생: {str(e)}"
        #         }),500
        #     #message = "추천 상품 목록을 성공적으로 가져왔습니다."
        # else:
        #     recommendations = []
        #     return jsonify({
        #         "status": "success",
        #         "recommendations": recommendations,
        #         "message": "추천 상품 목록이 없습니다."
        #     })
    
    except Exception as e:
        # 서버 내부 오류 발생 시 500 에러 처리
        return jsonify({
            "status" : "error",
            "message": "서버 내부 오류가 발생했습니다."
        }),500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)