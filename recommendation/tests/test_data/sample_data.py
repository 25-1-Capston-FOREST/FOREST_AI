"""테스트에 사용할 샘플 데이터 정의"""
from recommendation import ContentType, UserProfile

# 테스트용 컨텐츠 아이템
TEST_ITEMS = [
        # 영화 데이터 (20개)
        {
            "id": 1,
            "type": "movie",
            "title": "인셉션",
            "genre": ["액션", "SF"],
            "keywords": ["꿈", "도둑", "잠입"],
        },
        {
            "id": 2,
            "type": "movie",
            "title": "기생충",
            "genre": ["드라마", "스릴러"],
            "keywords": ["빈부격차", "블랙코미디", "사회비판"],
        },
        {
            "id": 3,
            "type": "movie",
            "title": "어벤져스: 엔드게임",
            "genre": ["액션", "SF"],
            "keywords": ["영웅", "우주", "전쟁"],
        },
        {
            "id": 4,
            "type": "movie",
            "title": "겨울왕국",
            "genre": ["애니메이션", "뮤지컬"],
            "keywords": ["눈", "자매", "마법"],
        },
        {
            "id": 5,
            "type": "movie",
            "title": "인터스텔라",
            "genre": ["SF", "드라마"],
            "keywords": ["우주", "시간", "구원"],
        },
        {
            "id": 6,
            "type": "movie",
            "title": "라라랜드",
            "genre": ["뮤지컬", "로맨스"],
            "keywords": ["음악", "꿈", "사랑"],
        },
        {
            "id": 7,
            "type": "movie",
            "title": "타이타닉",
            "genre": ["로맨스", "드라마"],
            "keywords": ["사랑", "배", "비극"],
        },
        {
            "id": 8,
            "type": "movie",
            "title": "해리포터와 마법사의 돌",
            "genre": ["판타지", "어드벤처"],
            "keywords": ["마법", "호그와트", "우정"],
        },
        {
            "id": 9,
            "type": "movie",
            "title": "다크 나이트",
            "genre": ["액션", "스릴러"],
            "keywords": ["배트맨", "조커", "정의"],
        },
        {
            "id": 10,
            "type": "movie",
            "title": "알라딘",
            "genre": ["애니메이션", "뮤지컬"],
            "keywords": ["램프", "마법", "사랑"],
        },
        {
            "id": 11,
            "type": "movie",
            "title": "007 스카이폴",
            "genre": ["액션", "스릴러"],
            "keywords": ["첩보", "임무", "스파이"],
        },
        {
            "id": 12,
            "type": "movie",
            "title": "라이온 킹",
            "genre": ["애니메이션", "드라마"],
            "keywords": ["왕", "자연", "성장"],
        },
        {
            "id": 13,
            "type": "movie",
            "title": "반지의 제왕: 두 개의 탑",
            "genre": ["판타지", "어드벤처"],
            "keywords": ["중간계", "여정", "전쟁"],
        },
        {
            "id": 14,
            "type": "movie",
            "title": "범죄도시",
            "genre": ["액션", "범죄"],
            "keywords": ["형사", "소탕", "조직"],
        },
        {
            "id": 15,
            "type": "movie",
            "title": "포레스트 검프",
            "genre": ["드라마", "로맨스"],
            "keywords": ["성장", "삶", "사랑"],
        },
        {
            "id": 16,
            "type": "movie",
            "title": "스타워즈: 새로운 희망",
            "genre": ["SF", "어드벤처"],
            "keywords": ["은하", "영웅", "전쟁"],
        },
        {
            "id": 17,
            "type": "movie",
            "title": "아바타",
            "genre": ["SF", "어드벤처"],
            "keywords": ["외계", "에너지", "자연"],
        },
        {
            "id": 18,
            "type": "movie",
            "title": "매트릭스",
            "genre": ["액션", "SF"],
            "keywords": ["가상현실", "구원자", "미래"],
        },
        {
            "id": 19,
            "type": "movie",
            "title": "쇼생크 탈출",
            "genre": ["드라마", "범죄"],
            "keywords": ["희망", "자유", "우정"],
        },
        {
            "id": 20,
            "type": "movie",
            "title": "토이스토리",
            "genre": ["애니메이션", "코미디"],
            "keywords": ["장난감", "우정", "모험"],
        },

        # 공연 데이터 (15개)
        {
            "id": 21,
            "type": "performance",
            "title": "오페라의 유령",
            "genre": ["뮤지컬", "로맨스"],
            "keywords": ["음악", "사랑", "미스터리"],
        },
        {
            "id": 22,
            "type": "performance",
            "title": "캣츠",
            "genre": ["뮤지컬", "드라마"],
            "keywords": ["고양이", "뮤지컬", "삶"],
        },
        {
            "id": 23,
            "type": "performance",
            "title": "노트르담 드 파리",
            "genre": ["뮤지컬", "드라마"],
            "keywords": ["파리", "사랑", "비극"],
        },
        {
            "id": 24,
            "type": "performance",
            "title": "레미제라블",
            "genre": ["뮤지컬", "역사"],
            "keywords": ["혁명", "희생", "운명"],
        },
        {
            "id": 25,
            "type": "performance",
            "title": "맘마미아",
            "genre": ["뮤지컬", "코미디"],
            "keywords": ["음악", "가족", "결혼"],
        },
        {
            "id": 26,
            "type": "performance",
            "title": "지킬 앤 하이드",
            "genre": ["뮤지컬", "스릴러"],
            "keywords": ["이중성", "비극", "사랑"],
        },
        {
            "id": 27,
            "type": "performance",
            "title": "호두까기 인형",
            "genre": ["발레", "클래식"],
            "keywords": ["음악", "춤", "동화"],
        },
        {
            "id": 28,
            "type": "performance",
            "title": "라 트라비아타",
            "genre": ["오페라", "드라마"],
            "keywords": ["희생", "사랑", "비극"],
        },
        {
            "id": 29,
            "type": "performance",
            "title": "모차르트",
            "genre": ["뮤지컬", "역사"],
            "keywords": ["음악", "천재", "비극"],
        },
        {
            "id": 30,
            "type": "performance",
            "title": "베토벤 바이러스",
            "genre": ["클래식", "음악"],
            "keywords": ["오케스트라", "천재", "갈등"],
        },
        {
            "id": 31,
            "type": "performance",
            "title": "국립국악단 공연",
            "genre": ["전통음악", "국악"],
            "keywords": ["민속", "한국음악", "전통"],
        },
        {
            "id": 32,
            "type": "performance",
            "title": "백조의 호수",
            "genre": ["발레", "클래식"],
            "keywords": ["춤", "희생", "순수"],
        },
        {
            "id": 33,
            "type": "performance",
            "title": "카르멘",
            "genre": ["오페라", "드라마"],
            "keywords": ["열정", "운명", "사랑"],
        },
        {
            "id": 34,
            "type": "performance",
            "title": "누구를 위하여 종은 울리나",
            "genre": ["연극", "드라마"],
            "keywords": ["정의", "갈등", "역사"],
        },
        {
            "id": 35,
            "type": "performance",
            "title": "브람스 교향곡",
            "genre": ["클래식", "음악"],
            "keywords": ["교향곡", "감정", "깊이"],
        },

        # 전시 데이터 (15개)
        {
            "id": 36,
            "type": "exhibition",
            "title": "반 고흐: 영원한 여행자",
            "genre": ["미술", "회화"],
            "keywords": ["인상주의", "명화", "예술"],
        },
        {
            "id": 37,
            "type": "exhibition",
            "title": "모네와 지베르니",
            "genre": ["미술", "회화"],
            "keywords": ["인상주의", "풍경", "빛"],
        },
        {
            "id": 38,
            "type": "exhibition",
            "title": "르네상스 작품 특별전",
            "genre": ["미술", "고전"],
            "keywords": ["고전주의", "걸작", "역사"],
        },
        {
            "id": 39,
            "type": "exhibition",
            "title": "팀랩 디지털 아트전",
            "genre": ["미디어아트"],
            "keywords": ["디지털", "기술", "예술"],
        },
        {
            "id": 40,
            "type": "exhibition",
            "title": "이중섭 특별전",
            "genre": ["미술"],
            "keywords": ["한국화", "소외", "감성"],
        },
        {
            "id": 41,
            "type": "exhibition",
            "title": "한국 현대 사진전",
            "genre": ["사진"],
            "keywords": ["현대", "다큐", "감각"],
        },
        {
            "id": 42,
            "type": "exhibition",
            "title": "피카소와 큐비즘",
            "genre": ["미술", "큐비즘"],
            "keywords": ["큐비즘", "추상", "혁신"],
        },
        {
            "id": 43,
            "type": "exhibition",
            "title": "국립 박물관 특별전",
            "genre": ["역사", "고고학"],
            "keywords": ["유물", "역사", "발견"],
        },
        {
            "id": 44,
            "type": "exhibition",
            "title": "미래 디자인 전시회",
            "genre": ["디자인"],
            "keywords": ["미래", "창의", "산업"],
        },
        {
            "id": 45,
            "type": "exhibition",
            "title": "전통 공예 특별전",
            "genre": ["미술", "공예"],
            "keywords": ["전통", "수공예", "문화"],
        },
        {
            "id": 46,
            "type": "exhibition",
            "title": "건축의 미래",
            "genre": ["건축"],
            "keywords": ["건축", "공간", "지속가능"],
        },
        {
            "id": 47,
            "type": "exhibition",
            "title": "현대 설치미술의 세계",
            "genre": ["설치미술"],
            "keywords": ["공간", "예술", "현대"],
        },
        {
            "id": 48,
            "type": "exhibition",
            "title": "로댕과 조각 예술",
            "genre": ["조각"],
            "keywords": ["조각", "고전", "감정"],
        },
        {
            "id": 49,
            "type": "exhibition",
            "title": "미디어아트 스펙트럼",
            "genre": ["미디어아트"],
            "keywords": ["디지털", "미래", "경험"],
        },
        {
            "id": 50,
            "type": "exhibition",
            "title": "다빈치의 발명",
            "genre": ["과학", "미술"],
            "keywords": ["발명", "다빈치", "혁신"],
        },
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