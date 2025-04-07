"""테스트에 사용할 샘플 데이터 정의"""
from recommendation import ContentType, UserProfile

# 테스트용 컨텐츠 아이템
TEST_ITEMS = [
    {
        "id": 1,
        "type": "movie",
        "title": "인셉션",
        "genre": ["액션", "SF"],
        "keywords": ["꿈", "도둑", "잠입"],
        "director": "크리스토퍼 놀란",
        "cast": ["레오나르도 디카프리오", "조셉 고든 레빗"]
    },
    {
        "id": 2,
        "type": "performance",
        "title": "오페라의 유령",
        "genre": ["뮤지컬", "로맨스"],
        "keywords": ["음악", "사랑", "미스터리"],
        "director": "앤드류 로이드 웨버",
        "cast": ["마이클 크로포드", "사라 브라이트만"]
    },
    {
        "id": 3,
        "type": "exhibition",
        "title": "반 고흐 전시",
        "genre": ["미술", "회화"],
        "keywords": ["인상주의", "명화", "예술"],
        "artist": "빈센트 반 고흐",
        "period": "2024.01-2024.12"
    }
]

# 테스트용 사용자 프로필
TEST_USER = UserProfile(
    keywords=["SF", "예술", "음악"],
    type_preferences={
        ContentType.MOVIE: 8,
        ContentType.PERFORMANCE: 6,
        ContentType.EXHIBITION: 7
    },
    genre_preferences={
        ContentType.MOVIE: ["액션", "SF"],
        ContentType.PERFORMANCE: ["뮤지컬"],
        ContentType.EXHIBITION: ["미술"]
    }
)

# 영화 선호 사용자 프로필
MOVIE_PREFERRED_USER = UserProfile(
    keywords=["SF", "액션"],
    type_preferences={
        ContentType.MOVIE: 10,
        ContentType.PERFORMANCE: 1,
        ContentType.EXHIBITION: 1
    },
    genre_preferences={
        ContentType.MOVIE: ["액션", "SF"],
        ContentType.PERFORMANCE: [],
        ContentType.EXHIBITION: []
    }
)