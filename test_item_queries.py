from database.item_queries import ItemQueries
from database.user_queries import UserQueries

def print_item_data(item):
    """각 아이템의 데이터를 보기 좋게 출력하는 함수"""
    if isinstance(item, dict):
        for key, value in item.items():
            print(f"{key}: {value}")
    else:
        print("데이터 형식이 올바르지 않습니다.")

def test_database_queries():
    """데이터베이스 쿼리 테스트 함수"""
    
    # ItemQueries 인스턴스 생성
    item_queries = ItemQueries()
    
    try:
        # 영화 데이터 테스트
        print("\n=== 영화 데이터 테스트 ===")
        movies = item_queries.get_movies_data()
        print(f"조회된 영화 수: {len(movies)}")
        if movies:
            print("\n첫 번째 영화 데이터 샘플:")
            print("--------------------------------")
            print_item_data(movies[0])
            
            # 전체 데이터 구조 확인
            print("\n데이터 구조 확인:")
            print(f"데이터 타입: {type(movies)}")
            print(f"첫 번째 항목 타입: {type(movies[0])}")
            print("\n실제 데이터 값:")
            print(movies[0])
        
        else:
            print("조회된 영화 데이터가 없습니다.")

        # # 공연 데이터 테스트
        # print("\n=== 공연 데이터 테스트 ===")
        # performances = item_queries.get_performance_data()
        # print(f"조회된 공연 수: {len(performances)}")
        # if performances:
        #     print("첫 번째 공연 데이터 샘플:")
        #     for key, value in zip(['activity_id', 'title', 'genre_nm', 'director', 'actors', 'keywords'], performances[0]):
        #         print(f"{key}: {value}")

        # # 전시 데이터 테스트
        # print("\n=== 전시 데이터 테스트 ===")
        # exhibitions = item_queries.get_exhibition_data()
        # print(f"조회된 전시 수: {len(exhibitions)}")
        # if exhibitions:
        #     print("첫 번째 전시 데이터 샘플:")
        #     for key, value in zip(['activity_id', 'title', 'genre_nm', 'director', 'actors', 'keywords'], exhibitions[0]):
        #         print(f"{key}: {value}")

    except Exception as e:
        print(f"테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_database_queries()