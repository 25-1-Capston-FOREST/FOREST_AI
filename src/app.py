## Flask 기반의 API 서버 메인 파일
## 클라이언트 요청 수신 -> 추천 알고리즘 모듈과 연동해 서버로 추천 결과 반환

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import time
import sys
from recommendation.recommendation import RecommendationAlgorithm
from database.user_queries import UserQueries
from database.item_queries import ItemQueries
from database.save_preference import PreferenceQueries
from chatbot.chatbot_main import Chatbot
from chatbot.keyword_extractor import KeywordExtractor
from config.settings import OPENAI_API_KEY, OPENAI_MODEL

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
save_preference = PreferenceQueries()
recommender = RecommendationAlgorithm()
logging.info("RecommendationAlgorithm 인스턴스 생성 완료")
chatbot = Chatbot(openai_api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
logging.info("Chatbot 인스턴스 생성 완료")
extractor = KeywordExtractor(openai_api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
logging.info("KeywordExtractor 인스턴스 생성 완료")
user_sessions = {}

# 챗봇
@app.route('/chatbot/answer', methods=['POST'])
def chatbot_answer():
    start_time = time.time()
    logging.info("/chatbot/answer 엔드포인트 호출됨")
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        question_id = data.get('question_id')
        message = data.get('message')
        logging.info(f"question_id: {question_id}, user_id: {user_id}, message: {message}")
        if not user_id or not question_id or not message:
            logging.warning(f'필수 데이터 누락 - user_id: {user_id}, question_id: {question_id} message: {message}')
            return jsonify({'status': 'error', 'message': '요청 데이터가 올바르지 않습니다.'}), 400

        # question_id가 1이면 세션 초기화
        if question_id == "1":
            logging.info(f"user_id: {user_id} - 대화 세션 초기화")
            user_sessions[user_id] = []

        # 대화 세션 관리(실제는 DB 등 추천)
        logging.info("챗봇 대화 세션 저장")
        dialogue = user_sessions.setdefault(user_id, [])
        # dialogue.append(message)
        last_bot_question = dialogue[-1][1] if dialogue else ""
        dialogue.append((message, ""))

        # 취향 키워드 추출 (질문 생성 용도)
        #logging.info("챗봇 키워드 추출")
        #keywords = extractor.extract(message)

        # 챗봇의 '후속 질문' 생성 (few-shot + 현재 내역 & 키워드 반영)
        logging.info("챗봇 후속 질문 생성")
        logging.info("dialogue 구조 확인: %s", repr(dialogue))
        #logging.info("keywords: %s", repr(keywords))
        next_question = chatbot.generate_next_question(dialogue)

        # dialogue 최신 발화 갱신
        logging.info("발화 갱신")
        dialogue[-1] = (message, next_question)

        logging.info("질문 반환")
        end_time = time.time()
        logging.info(f"챗봇 응답 소요 시간: {end_time - start_time:.2f}초")
        # **reply에는 오직 질문만 반환 (키워드 등은 절대 노출X)**
        return jsonify({'status': 'success', 'reply': next_question}), 200

    except Exception as e:
        logging.error(f"챗봇 처리 중 오류: {str(e)}")
        return jsonify({'status': 'error', 'message': '챗봇 처리 중 오류가 발생했습니다.'}), 500

@app.route('/chatbot/save', methods=['POST'])
def chatbot_save():
    logging.info("/chatbot/save 엔드포인트 호출됨")
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id가 필요합니다.'}), 400
        
        logging.info(f"{user_id} 대화 내역 불러오기")
        dialogue = user_sessions.get(user_id, [])
        logging.info("dialogue 구조 확인: %s", repr(dialogue))
        if not dialogue:
            return jsonify({'status': 'error', 'message': '대화 기록 없음'}), 404

        # 메시지 합치기
        logging.info("메시지 통합")
        logging.info("dialogue 구조 확인: %s", repr(dialogue))
        all_text = " ".join(ut[0] for ut in dialogue)
        logging.info(f"모든 발화 통합: {all_text}")
        logging.info("키워드 추출")
        keywords = extractor.extract(all_text)
        print("[전체 발화 기준 키워드 추출 결과]",keywords)
    
        logging.info("키워드 저장")
        # DB 저장 (preference)
        save_preference.save_like_words(user_id, keywords)

        # # 대화 세션 초기화
        # if user_id in user_sessions:
        #     del user_sessions[user_id]

        return jsonify({'status': 'success', 'message': '성공적으로 저장되었습니다.'}), 200

    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({'status': 'error', 'message': '키워드 저장 중 오류가 발생했습니다.'}), 500

# 추천 리스트
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    start_time = time.time()
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

            end_time = time.time()
            logging.info(f"추천 생성 완료, 소요 시간: {end_time - start_time:.2f}초")

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
    
    except Exception as e:
        # 서버 내부 오류 발생 시 500 에러 처리
        return jsonify({
            "status" : "error",
            "message": "서버 내부 오류가 발생했습니다."
        }),500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)