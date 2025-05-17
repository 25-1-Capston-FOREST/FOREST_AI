import openai
import os

# 환경변수에 OPENAI_API_KEY를 반드시 등록!
openai.api_key = os.getenv("OPENAI_API_KEY")

# prompting.py에서 불러오거나 직접 선언
try:
    from prompting import get_few_shot
    FEW_SHOT = get_few_shot()
except ImportError:
    FEW_SHOT = [
        {
            "role": "system",
            "content": (
                "너는 영화, 공연, 전시 분야의 문화 추천을 도와주는 친절한 AI 챗봇이야. "
                "항상 존댓말과 공손한 어투를 사용하며, 사용자의 취향, 선호 장르, 최근 감상 경험 등 데이터를 자연스럽게 수집하길 원해. "
                "구체적으로, 영화·공연·전시와 관련된 취향, 감상 방식, 특별히 좋아하는 요소, 최근 감상한 작품 등에 대해 질문해. 감상한 작품에서 어떤 요소가 좋았는지나 기억에 남았는지 질문해."
                "친절하게 공감하며, 대답하기 어려울 때는 편하게 건너뛰라고 안내해도 좋아."
            )
        },
        # 아래 생략(앞서 안내 예시 참고)
    ]

def generate_chatbot_response(user_history):
    # FEW_SHOT + 유저 입력 합친 messages 생성
    messages = FEW_SHOT.copy()
    for ua in user_history:
        messages.append({"role": "user", "content": ua["user"]})
        if "assistant" in ua and ua["assistant"]:
            messages.append({"role": "assistant", "content": ua["assistant"]})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0.7,
        n=1,
        stop=None,
    )
    return response.choices[0].message.content.strip()