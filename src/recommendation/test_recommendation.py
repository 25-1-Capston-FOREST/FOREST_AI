import logging

# 예시용 dummy recommender 클래스
class DummyRecommender:
    def get_recommendations(self, user_id):
        # 테스트용 임의 결과 반환
        if user_id == "testuser":
            return ["item1", "item2", "item3"]
        else:
            return []

# 인스턴스 생성
recommender = DummyRecommender()

# 실제 Flask request 대신 데이터 직접 입력
def test_create_recommendations(input_data):
    try:
        logging.info("recommendations 엔드포인트 호출됨")
        data = input_data  # request.get_json()을 대신함
        logging.debug(f"수신된 데이터: {data}")

        # user_id 검증
        if not data or 'user_id' not in data:
            # user_id 없는 경우 400 에러 처리
            return {
                "status": "error",
                "message": "유효하지 않은 사용자 ID입니다.",
                "code": 400
            }
        
        user_id = data['user_id']
        logging.info(f"처리 중인 user_id: {user_id}")

        # 추천 목록 생성
        try:
            logging.info("추천 알고리즘 실행 시작")
            recommendation_list = recommender.get_recommendations(user_id)
            logging.info(f"추천 결과 생성됨: {recommendation_list}")

            if len(recommendation_list) > 0:
                return {
                    "status": "success",
                    "recommendations": recommendation_list,
                    "message": "추천 상품 목록을 성공적으로 가져왔습니다."
                }
            else:
                return {
                    "status": "fail",
                    "recommendations": [],
                    "message": "추천 상품 목록이 없습니다."
                }

        except Exception as e:
            logging.error(f"추천 생성 중 오류 발생: {str(e)}")
            return {
                "status": "error",
                "message": f"추천 생성 중 오류 발생: {str(e)}",
                "code": 500
            }

    except Exception as e:
        # 서버 내부 오류 발생 시 500 에러 처리
        return {
            "status": "error",
            "message": "서버 내부 오류가 발생했습니다.",
            "code": 500
        }

# ------ 코드 테스트 예시 -------
if __name__ == "__main__":
    # 정상 테스트 케이스
    test_input = {'user_id': 'testuser'}
    result = test_create_recommendations(test_input)
    print(result)

    # user_id 없음 테스트
    test_input2 = {'no_user': 'testuser'}
    result2 = test_create_recommendations(test_input2)
    print(result2)

    # 결과 없음 테스트
    test_input3 = {'user_id': 'etcuser'}
    result3 = test_create_recommendations(test_input3)
    print(result3)