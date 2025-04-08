import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}

# 추가 설정들
RECOMMENDATION_SETTINGS = {
    'update_interval': 3600,  # 1시간
    'min_ratings': 10,
    'similarity_threshold': 0.5
}