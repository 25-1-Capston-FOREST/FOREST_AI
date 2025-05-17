# 테스트 파일 예시: test_chatbot_keyword.py

from chatbot import Chatbot
from keyword_extractor import KeywordExtractor

# 테스트용 입력 (실제 대화 시퀀스 예시)
test_dialogues = [
    ("", "최근에 감상한 영화나 공연, 전시가 있으신가요?"),
    ("네, 지난 주에 인생은 아름다워 뮤지컬을 봤어요.", ""),
    ("감동적이었나요, 아니면 밝고 유쾌한 분위기를 더 선호하시나요?", ""),
    ("저는 감동적이면서 성장하는 스토리를 좋아해요.", ""),
]

# 1. 키워드 추출기 & 챗봇 인스턴스 생성
chatbot = Chatbot()
extractor = KeywordExtractor()

# 2. 대화 진행 및 키워드 추출 시연
dialogue_history = []
print("=== [테스트] 챗봇&키워드 추출 모듈 ===\n")

for i, (user_input, bot_question) in enumerate(test_dialogues):
    if user_input:
        # 키워드 추출 (사용자 응답에 대해)
        keywords = extractor.extract(user_input)
        print(f"[사용자 입력] : {user_input}")
        print(f"[추출된 키워드] : {keywords}")
        dialogue_history.append((user_input, bot_question))
        # 챗봇의 후속질문 생성
        next_question = chatbot.generate_next_question(dialogue_history, keywords)
        print(f"[챗봇 후속 질문] : {next_question}\n")
        dialogue_history[-1] = (user_input, next_question)
    else:
        # 첫 챗봇 질문
        dialogue_history.append(("", bot_question))
        print(f"[챗봇 시작 질문] : {bot_question}\n")