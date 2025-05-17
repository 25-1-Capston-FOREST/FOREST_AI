import os
from dotenv import load_dotenv

# .env 파일을 현재 경로/상위에서 자동 로드
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")