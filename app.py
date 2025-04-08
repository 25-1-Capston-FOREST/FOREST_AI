## Flask 기반의 API 서버 메인 파일
## 클라이언트 요청 수신 -> 추천 알고리즘 모듈과 연동해 서버로 추천 결과 반환

from flask import Flask, request, jsonify
import logging
from recommendation.recommendation import RecommendationAlgorithm

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 추천 알고리즘 인스턴스 생성
recommender = RecommendationAlgorithm()

@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    try:
        # 쿼리 파라미터에서 userId 추출
        user_id = request.args.get("userId")
        if not user_id:
            # user_id 없는 경우 400 에러 처리
            return jsonify({
                "status": "error",
                "message": "유효하지 않은 사용자 ID입니다."
            }), 400

        # 예시 로직: userId가 "12345"인 경우 추천 리스트가 있는 경우, 아닌 경우 빈 리스트 반환
        if user_id == "12345":
            recommendations = [13, 25, 38, 99, 102]
            message = "추천 상품 목록을 성공적으로 가져왔습니다."
        else:
            recommendations = []
            message = "추천 상품 목록이 없습니다."

        response = {
            "status": "success",
            "recommendations": recommendations,
            "message": message
        }
        return jsonify(response), 200
    
    except Exception as e:
        # 서버 내부 오류 발생 시 500 에러 처리
        return jsonify({
            "status" : "error",
            "message": "서버 내부 오류가 발생했습니다."
        }),500

if __name__ == '__main__':
    # 로컬 서버를 5000번 포트에서 디버그 모드로 실행
    app.run(debug=True)