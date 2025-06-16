import openai
from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from .prompting import FEWSHOT_EXAMPLES
import random


class Chatbot:
    def __init__(self, openai_api_key=OPENAI_API_KEY, model=OPENAI_MODEL):
        self.model = model
        # 최신 버전에서 클라이언트 인스턴스를 활용합니다.
        self.client = openai.OpenAI(api_key=openai_api_key)

        self.few_shot_examples = FEWSHOT_EXAMPLES

    def generate_next_question(self, dialogue_history):
        # 대화내역을 질문-답변 쌍 형태로 구성
        messages=[]
        context = ""
        for user_input, bot_question in dialogue_history:
            if bot_question:
                context += f"챗봇: {bot_question}\n"
            if user_input:
                context += f"사용자: {user_input}\n"

        # Few-shot 예시 추가
        few_shot_examples = [
            # greeting ex
            {"role": "user", "content": "안녕하세요"},
            {"role": "assistant", "content": "안녕하세요! 최근 본 영화나 공연, 전시가 있으신가요?"},

            # Example 1
            {"role": "user", "content": "최근에는 친구와 함께 <웡카> 영화를 관람하였습니다."},
            {"role": "assistant", "content": "그 영화를 관람하시면서 가장 인상 깊었던 장면이나 느낌이 있으셨나요?"},
            
            # Example 2
            {"role": "user", "content": "저는 감동적인 드라마와 로맨스 장르를 특히 좋아합니다."},
            {"role": "assistant", "content": "그 중에서 최근 감동을 받으셨던 드라마나 로맨스 영화가 있으신가요?"},
            
            # Example 3
            {"role": "user", "content": "얼마 전 미술관에서 열린 현대미술 전시가 매우 인상적이었습니다."},
            {"role": "assistant", "content": "해당 전시에서 특별히 마음에 들었던 작품이나 테마가 있으셨는지 여쭤봐도 될까요?"},
            
            # Example 4
            {"role": "user", "content": "뮤지컬과 발레 공연을 자주 관람하는 편입니다."},
            {"role": "assistant", "content": "최근에 관람하신 뮤지컬이나 발레 공연 중에서 추천해주실 만한 작품이 있으신가요?"},
            
            # Example 5
            {"role": "user", "content": "영화 <라라랜드>를 보고 깊은 감동을 받은 기억이 있습니다."},
            {"role": "assistant", "content": "<라라랜드>에서 특별히 감동을 주었던 장면이나 음악이 무엇인지 말씀해주실 수 있으신가요?"},
        ]
        few_shot_str = (
            "아래 예시는 AI가 답변 형식과 존댓말 쓰임을 참고하기 위한 샘플 대화입니다. 실제 대화 내역은 아니며 참고용으로만 사용하십시오.\n\n"
        )
        for ex in few_shot_examples:
            role_kr = "사용자" if ex["role"] == "user" else "챗봇"
            few_shot_str += f"{role_kr}: {ex['content']}\n"
        few_shot_str += "\n"


        prompt = (
            "Role Assignment:"
            "- An AI chatbot specializing in in-depth discovery of users’ preferences for movies, performances, and exhibitions."
            "- The chatbot explores users’ tastes, favorite works, genres, and viewing habits. Conversation Context:"
            "- The user is sharing information or answering questions related to movies, performances, or exhibitions."
            "- The AI continues the conversation by asking appropriate follow-up questions based on user responses."
            "Rules:"
            "Always use polite and formal style (proper sentence endings, no informal or incomplete questions)."
            "Never use or output informal (incorrect) questions."
            " In all other cases, always generate a new, more specific follow-up question, in Korean (jondaemal), based on the user's previous answer. The question should help the user express their experiences, preferences, or tastes in more detail."
            "All responses must be output in Korean, using a polite and formal tone with a proper sentence ending."
            + few_shot_str +
            f"Here is the actual conversation so far:\n{context}\n\n"
        )


        messages = [
            {"role":"system","content":prompt},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=128,
                temperature=0.8
            )
            question = response.choices[0].message.content.strip()
            # '챗봇:'으로 시작하면 제거
            if question.startswith("챗봇:"):
                question = question[len("챗봇:"):].strip()
            if not question.endswith('?'):
                question += "?"
            return question
        except Exception as e:
            print("[GPT ERROR]", e)
            return "최근 본 문화 예술 작품 중 기억에 남는 게 있으신가요?"