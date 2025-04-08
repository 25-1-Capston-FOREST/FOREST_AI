# test_user_queries.py
from database.user_queries import UserQueries
import logging
import json
from pprint import pprint

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_user_preferences(preferences):
    """사용자 선호도 정보를 보기 좋게 출력하는 함수"""
    if not preferences:
        print("사용자 선호도 정보가 없습니다.")
        return

    print("\n=== 사용자 선호도 정보 ===")
    print("----------------------------------------")
    
    # 선호도 점수 출력
    print("활동 선호도:")
    print(f"- 영화 선호도: {preferences.get('movie_preference', 'N/A')}")
    print(f"- 공연 선호도: {preferences.get('performance_preference', 'N/A')}")
    print(f"- 전시 선호도: {preferences.get('exhibition_preference', 'N/A')}")
    
    # 장르 선호도 출력
    print("\n장르 선호도:")
    print("- 영화 장르:")
    pprint(preferences.get('movie_genre_preference', {}))
    print("\n- 공연 장르:")
    pprint(preferences.get('performance_genre_preference', {}))
    print("\n- 전시 장르:")
    pprint(preferences.get('exhibition_genre_preference', {}))
    
    # 선호 키워드 출력
    print("\n선호 키워드:")
    pprint(preferences.get('like_words', []))

def validate_preference_data(preferences):
    """선호도 데이터 유효성 검사 함수"""
    if not preferences:
        return False
        
    required_fields = [
        'movie_preference',
        'performance_preference',
        'exhibition_preference',
        'movie_genre_preference',
        'performance_genre_preference',
        'exhibition_genre_preference',
        'like_words'
    ]
    
    # 필수 필드 존재 확인
    for field in required_fields:
        if field not in preferences:
            logging.error(f"필수 필드 누락: {field}")
            return False
    
    # 장르 선호도가 딕셔너리인지 확인
    genre_fields = [
        'movie_genre_preference',
        'performance_genre_preference',
        'exhibition_genre_preference'
    ]
    for field in genre_fields:
        if not isinstance(preferences[field], dict):
            logging.error(f"{field}가 딕셔너리 형식이 아닙니다.")
            return False
    
    # like_words가 리스트인지 확인
    if not isinstance(preferences['like_words'], list):
        logging.error("like_words가 리스트 형식이 아닙니다.")
        return False
    
    return True

def test_user_preferences():
    """사용자 선호도 조회 테스트 함수"""
    
    try:
        user_queries = UserQueries()
        
        # 테스트할 사용자 ID
        test_user_id = "test_user_1"  # 실제 존재하는 사용자 ID로 변경
        
        print(f"\n=== 사용자 선호도 테스트 (User ID: {test_user_id}) ===")
        preferences = user_queries.get_user_preferences(test_user_id)
        
        if preferences:
            # 데이터 유효성 검사
            if validate_preference_data(preferences):
                print("데이터 유효성 검사 통과")
                print_user_preferences(preferences)
                
                # 데이터 타입 확인
                print("\n데이터 타입 확인:")
                print(f"전체 데이터 타입: {type(preferences)}")
                print(f"장르 선호도 타입: {type(preferences['movie_genre_preference'])}")
                print(f"키워드 타입: {type(preferences['like_words'])}")
            else:
                print("데이터 유효성 검사 실패")
        else:
            print(f"사용자 ID {test_user_id}에 대한 선호도 정보를 찾을 수 없습니다.")

    except Exception as e:
        logging.error(f"테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_user_preferences()