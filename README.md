# FOREST_AI

본 프로젝트는 **캡스톤디자인 및 창업프로젝트 29팀**의 졸업작품입니다. 그중에서도 AI 파트에 관련된 내용을 포함합니다.

---

## 프로젝트 소개

사용자의 취향을 분석하여 최적의 여가 활동을 제안하는 **1:1 맞춤형 영화/공연/전시 추천 서비스**입니다.
최신 영화, 공연, 전시의 다양한 정보를 한 곳에서 조회할 수 있는 기능을 제공합니다. 사용자와 챗봇 간의 대화를 통해 사용자의 취향 데이터를 수집하고, 추천 알고리즘을 통해 해당 서비스 내에서 핵심 기능인 사용자 맞춤형 여가 추천 기능을 수행합니다. 추천 알고리즘은 사용자들이 경험한 여가에 남긴 평점 데이터가 축적될수록 더욱 정교해집니다.

---

## 주요 기술 스택 및 오픈소스

| 기술        | 설명 |
|-------------|------|
| **AWS EC2** | 서비스 호스팅 및 배포 환경 |
| **Flask**   | 파이썬 기반 오픈 소스 웹 프레임워크 |
| **Surprise** | SVD 모델을 이용한 평점 예측, 추천 시스템 구현 |
| **scikit-learn** | 코사인 유사도 기반 추천 구현 |
| **MySQL** | 사용자 데이터 및 활동 데이터 저장/조회 |
| **KoNLPy** | 한국어 자연어 처리 도구로 키워드 분석에 활용 |

---

## 프로젝트 구조 (AI)
    ```
    FOREST_AI/
    ├── README.md
    ├── .env
    ├── requirements.txt
    ├── sample_data.sql
    ├── src/
    │ ├── app.py # Flask API 서버 실행 파일
    │ ├── chatbot/ # 챗봇 및 키워드 추출
    │ │ ├── init.py
    │ │ ├── chatbot_main.py # 챗봇 대화 생성
    │ │ ├── keyword_examples.py # 키워드 예시 데이터
    │ │ ├── keyword_extractor.py # 키워드 추출
    │ │ └── stopwords.py # 불용어
    │ ├── config/
    │ │ ├── init.py
    │ │ └── settings.py
    │ ├── database/ # 데이터 베이스 연동 및 쿼리
    │ │ ├── init.py
    │ │ ├── base.py # 쿼리 실행
    │ │ ├── connection.py # DB 연결
    │ │ ├── item_queries.py # 아이템 데이터 쿼리
    │ │ ├── rating_queries.py # 평점 데이터 쿼리
    │ │ ├── save_preference.py # 추출 키워드 저장
    │ │ └── user_queries.py # 사용자 데이터 쿼리 
    │ └── recommendation/ # 추천 알고리즘
    │ ├── init.py
    │ ├── preprocessor.py # 데이터 전처리
    │ ├── recommendation.py # 추천 알고리즘
    │ └── setup.py

---

## 실행 방법

1. **프로젝트 클론하기**
   ```bash
   git clone https://github.com/25-1-Capston-FOREST/FOREST_AI.git
   cd FOREST_AI/src

2. **파이썬 가상환경 생성 및 활성화**
    ```bash
    python3 -m venv myenv
    source myenv/bin/activate  # (Linux/Mac)
    venv\Scripts\activate      # (Windows)

3. **의존성 패키지 설치**
    ```bash
    pip install -r requirements.txt

4. **환경변수(.env) 설정**
    ```ini
    # 데이터베이스 환경 변수
    DB_HOST=
    DB_PORT=
    DB_USER=
    DB_PASSWORD=
    DB_NAME=
    # OpenAI API Key (GPT 3.5 turbo)
    OPENAI_API_KEY=your_openai_key

5. **Flask 서버 실행**
가상환경이 활성화된 상태에서 Flask 서버를 실행합니다.
    ```bash
    python3 app.py
서버가 실행되면 http://localhost:5000 또는 설정된 호스트에서 API를 사용할 수 있습니다.


## 테스트 방법 (How to Test)

1. **샘플 데이터 삽입 - sample_data.sql**
샘플 데이터를 로컬 MySQL 데이터베이스에 삽입해 테스트할 수 있습니다.
sample_data.sql에는 유저 선호 정보, 영화/공연/전시 정보가 담겨있습니다.
    ```bash
    mysql -u [user_name] -p FOREST_DB < sample_data.sql

2. **추천 API 테스트**
    ```bash
    curl -X POST http://localhost:5000/recommendations \
    -H "Content-Type: application/json" \
    -d '{"user_id": 1}'
성공 시, 사용자에게 추천된 영화/공연/전시의 activity_id 목록이 반환됩니다.


