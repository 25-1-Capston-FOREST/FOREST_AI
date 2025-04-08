## 파이썬 서버 임시 파일
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import os
import mysql.connector
import logging
from recommendation.recommendation import RecommendationAlgorithm
from config.settings import get_database_config


# 환경변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 데이터베이스 연결 함수
def get_db_connection():
    try:
        config = get_database_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {str(e)}")
        raise

# 추천 알고리즘 인스턴스 생성
recommender = RecommendationAlgorithm()

@app.route('/health', methods=['GET'])
def health_check():
    """
    서버 상태 확인을 위한 헬스체크 엔드포인트
    """
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/recommendations', methods=['POST'])
def process_recommendations():
    """
    추천 알고리즘을 실행하고 결과를 반환하는 엔드포인트
    """
    try:
        # 요청 데이터 검증
        data = request.get_json()
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400

        # 필수 파라미터 확인
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id가 필요합니다.'}), 400

        # 데이터베이스 연결
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            # 필요한 데이터 조회
            cursor.execute("""
                SELECT u.*, p.purchase_history, r.rating_history
                FROM users u 
                LEFT JOIN purchases p ON u.user_id = p.user_id
                LEFT JOIN ratings r ON u.user_id = r.user_id
                WHERE u.user_id = %s
            """, (user_id,))
            
            user_data = cursor.fetchone()

            if not user_data:
                return jsonify({'error': '사용자 데이터를 찾을 수 없습니다.'}), 404

            # 추천 알고리즘 실행
            recommended_items = recommender.generate_recommendations(user_data)

            # 추천 결과 형식화
            response_data = {
                'user_id': user_id,
                'recommended_items': recommended_items,
                'timestamp': datetime.now().isoformat(),
                'algorithm_version': recommender.get_version()
            }

            return jsonify(response_data), 200

        finally:
            cursor.close()
            connection.close()

    except Exception as e:
        logger.error(f"추천 처리 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

# 에러 핸들러
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': '요청한 리소스를 찾을 수 없습니다.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
