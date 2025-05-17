import re
from konlpy.tag import Okt
import openai
from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from stopwords import STOPWORDS
from prompt_examples import PREFERENCE_KEYWORD_EXAMPLES

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
            f"아래 문장에서 영화/공연/전시의 취향, 분위기, 장르 등 중요한 대표 키워드 3~5개만 콤마로 알려줘.\n"
            f"예시: {ex_keywords}\n"
            f'문장: "{text}"\n'
            "불필요 명사·대명사·인칭 등은 제외, 반드시 취향/분위기/장르 중심\n"
            "키워드:"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "사용자 문화·취향 키워드만 엄선하는 한국어 전문가입니다."},
                    {"role": "user", "content": prompt}
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
            f'"{text}" 이 문장에서 "{kw}"는 긍정적인 취향 키워드입니까? 맞으면 "예", 아니면 "아니요"만 답하세요.'
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