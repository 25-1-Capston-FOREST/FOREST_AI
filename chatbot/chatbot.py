import openai
from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from .prompting import FEWSHOT_EXAMPLES
import random
import datetime

class Chatbot:
    def __init__(self, openai_api_key=OPENAI_API_KEY, model=OPENAI_MODEL):
        self.model = model
        # 최신 버전에서 클라이언트 인스턴스를 활용합니다.
        self.client = openai.OpenAI(api_key=openai_api_key)

        self.few_shot_examples = FEWSHOT_EXAMPLES

    def generate_next_question(self, dialogue_history, keywords):
        # 대화내역을 질문-답변 쌍 형태로 구성
        messages=[]
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

        # prompt = (
        #     "You are an AI chatbot specializing in in-depth discovery of users’ preferences for movies, performances, and exhibitions, "
        #     "including their tastes, favorite works, genres, and viewing habits.\n\n"
        #     "Below are example questions and answers (for your reference only):\n"
        #     f"{few_shot_str}\n\n"
        #     "Here is the actual conversation so far:\n"
        #     f"{context}\n\n"
        #     f"■ Keywords identified so far: {keyword_str}\n\n"
        #     "If the user's response does not mention any preferences, moods, or interests related to movies, performances, or exhibitions, "
        #     "and only contains greetings or unrelated topics, then always generate only one of the following fixed questions (exactly as follows):\n"
        #     "- \"요즘 본 영화나 공연, 전시가 있으신가요?\"\n"
        #     "- \"어떤 장르를 선호하시나요?\"\n"
        #     "Select one randomly from these fixed options.\n"
        #     "Under any circumstances, do not copy, reuse, or output the example questions or answers above as your response.\n"
        #     "Generate only one new, more specific and natural follow-up question to elicit the user's preferences even more effectively. "
        #     "The question should help the user express their tastes or experiences in greater detail. "
        #     "Do not include greetings, keyword mentions, or unnecessary introductions—output only the follow-up question. "
        #     "Output your question in Korean, using polite and formal language (jondaemal) with a complete sentence ending. "
        #     "Ensure the sentence ends properly with a complete and natural ending (어미) in Korean."
        # )\
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
            f"Here is the actual conversation so far:\n{context}\n\n"
        )

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

        messages = [
            {"role":"system","content":prompt},
        ]
        messages.extend(few_shot_examples)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=128,
                temperature=0.8
            )
            question = response.choices[0].message.content.strip()
            if not question.endswith('?'):
                question += "?"
            return question
        except Exception as e:
            print("[GPT ERROR]", e)
            return "최근 본 문화 예술 작품 중 기억에 남는 게 있으신가요?"