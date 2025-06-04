import re
from konlpy.tag import Okt
import openai
from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from .stopwords import STOPWORDS
from .prompt_examples import PREFERENCE_KEYWORD_EXAMPLES

class KeywordExtractor:
    def __init__(self, 
                 openai_api_key=OPENAI_API_KEY, 
                 model=OPENAI_MODEL, 
                 stopwords=STOPWORDS, 
                 preference_examples=PREFERENCE_KEYWORD_EXAMPLES):
        # 최신 openai 패키지 방식
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        self.okt = Okt()
        self.stopwords = stopwords
        self.preference_examples = preference_examples

    def extract(self, text: str):
        """(a)-(b)-(c)-(d) 통합 프로세스"""
        # (a) 명사 추출+불용어 제거
        text_clean = self._clean_text(text)
        base_keywords = [w for w in self.okt.nouns(text_clean) 
                         if w not in self.stopwords and len(w) > 1]

        # (b) GPT 기반 "의미중심" 키워드 보조 추출
        gpt_keywords = self._extract_keywords_gpt(text)
        
        # (c) 통합, 중복 제거
        candidates = list(set(base_keywords + gpt_keywords))

        # (d) 감성 분석 통한 긍정 키워드만 추림
        result = [kw for kw in candidates if self._is_positive(kw, text)]

        return result

    def _clean_text(self, text):
        return re.sub(r"[^\uAC00-\uD7A3a-zA-Z0-9\s]", " ", text).strip()

    def _extract_keywords_gpt(self, text):
        ex_keywords = ', '.join(self.preference_examples)
        prompt = (
            "From the following Korean sentence, extract only 3 to 5 important and representative keywords in Korean related to taste, mood, or genre, specifically for movies, performances, or exhibitions. "
            "Exclude unnecessary nouns, pronouns, and personal names; focus only on tastes/preferences, mood, or genres. "
            "If there are no suitable keywords in the sentence, do not generate or add any keywords—just leave it blank. "
            "Provide only the keywords in Korean, separated by commas.\n\n"
            f"Example keywords: {ex_keywords}\n"
            f"Sentence: \"{text}\"\n"
            "Keywords:"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt}
                ],
                max_tokens=24,
                temperature=0
            )
            answer = response.choices[0].message.content
            keywords = [k.strip() for k in answer.replace('키워드:', '').replace('\n', '').split(',') if len(k.strip()) > 1]
            return keywords
        except Exception as e:
            print(f"[GPT 키워드 추출 오류] {e}")
            return []

    def _is_positive(self, kw, text):
        prompt = (
            f'In the following Korean sentence, is "{kw}" mentioned as a positive preference keyword? '
            f'If yes, answer only "예". If not, answer only "아니요". Provide your answer only in Korean, without any explanation.\n\n'
            f'Sentence: "{text}"'
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "긍정 취향 키워드만 판별하는 한국어 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3,
                temperature=0
            )
            result = response.choices[0].message.content.strip().replace('.', '')
            return '예' in result
        except Exception as e:
            print(f"[GPT 감성분석 오류] {kw}: {e}")
            return False