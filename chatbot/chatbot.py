import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from prompting import FEWSHOT_EXAMPLES

class Chatbot:
    def __init__(self, openai_api_key=OPENAI_API_KEY, model=OPENAI_MODEL):
        self.model = model
        openai.api_key = openai_api_key

        self.few_shot_examples = FEWSHOT_EXAMPLES
        self.initial_questions = [
            "최근에 감상한 영화나 공연, 전시가 있으신가요?",
            "어떤 장르를 선호하시나요?",
            "특별히 기억에 남는 작품이 있으신가요?"
        ]

    def generate_next_question(self, dialogue_history, keywords):
        # 대화내역을 질문-답변 쌍 형태로 구성
        context = ""
        for user_input, bot_question in dialogue_history:
            if bot_question:
                context += f"챗봇: {bot_question}\n"
            if user_input:
                context += f"사용자: {user_input}\n"

        # Few-shot 예시 추가
        few_shot_str = ""
        for ex in self.few_shot_examples:
            few_shot_str += f"챗봇: {ex['user']}\n사용자: {ex['assistant']}\n"

        keyword_str = ", ".join(keywords) if keywords else "없음"

        prompt = (
            f"너는 영화/공연/전시 취향, 선호작품, 장르, 관람 방식 등을 심층적으로 알아보는 AI 챗봇이야.\n"
            f"아래는 예시 질문 및 답변이야. (참고만 하세요)\n"
            f"{few_shot_str}\n"
            f"아래는 지금까지의 실제 대화내역이야.\n{context}\n"
            f"■ 지금까지 파악된 키워드: {keyword_str}\n"
            "기존보다 더 구체적이고 자연스러운 맞춤형 질문을 한 가지만 생성해.\n"
            "- 사용자가 취향을 더 잘 드러낼 수 있도록 이끌어내는 질문일수록 좋아.\n"
            "- 인사말/키워드 언급/불필요한 서론 없이 ‘질문만’ 출력해."
        )

        # 첫 질문 처리
        if len(dialogue_history) <= 1 or (not keywords and len(dialogue_history) <= 2):
            return self.initial_questions[len(dialogue_history) % len(self.initial_questions)]

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "너는 맞춤 질문을 하는 영화/공연/전시 취향 챗봇이야."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=64,
                temperature=0.8
            )
            question = response['choices'][0]['message']['content'].strip()
            if not question.endswith('?'):
                question += "?"
            return question
        except Exception as e:
            print("[GPT ERROR]", e)
            return "최근 본 문화 예술 작품 중 기억에 남는 게 있으신가요?"