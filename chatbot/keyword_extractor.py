import openai
import os
from konlpy.tag import Okt
import re

openai.api_key = os.getenv('OPENAI_API_KEY')

class KeywordExtractor:
    def __init__(self):
        self.okt = Okt()
        self.stopwords = {
            '은', '는', '이', '가', '를', '을', '에', '의', '도', '와',
            '과', '로', '으로', '부터', '까지', '에서', '입니다', '해요', '합니다'
        }

    def extract(self, text: str):
        # 1. NLP 명사 추출
        text_clean = re.sub(r'[^\w\s]', ' ', text)
        words = self.okt.nouns(text_clean)
        base_keywords = [w for w in words if w not in self.stopwords and len(w) > 1]

        # 2. GPT 키워드 보조 추출
        prompt = f"""다음 문장에서 문화취향이나 활동을 대표할 수 있는 키워드만 3~5개 콤마로 나열해 주세요:
문장: "{text}"
"""
        try:
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "당신은 문화취향 키워드 추출기입니다."},
                          {"role": "user", "content": prompt}],
                max_tokens=30, temperature=0)
            gpt_keywords = [k.strip() for k in gpt_response['choices'][0]['message']['content'].split(',') if len(k.strip()) > 1]
        except Exception:
            gpt_keywords = []

        # 3. 키워드 후보 병합
        candidate_keywords = list(set(base_keywords + gpt_keywords))

        # 4. 각 키워드별로 입력표현과 텍스트 내 감성분석 → 긍정인 것만
        positive_keywords = []
        for kw in candidate_keywords:
            sentiment = self.sentiment_of_phrase_in_context(kw, text)
            if sentiment == "긍정":
                positive_keywords.append(kw)
        return positive_keywords

    def sentiment_of_phrase_in_context(self, phrase: str, context: str):
        """
        phrase가 context(전체 문장)에서 어떤 감성(긍정/부정/중립)인지 GPT에게 판단시킵니다.
        """
        prompt = f"""다음 문장에서 '{phrase}'에 대한 화자의 감정(긍정/부정/중립)을 심플하게 한 단어(긍정, 부정, 중립)로만 답해주세요.
문장: "{context}"
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "감성 분석가입니다."},
                          {"role": "user", "content": prompt}],
                max_tokens=3, temperature=0
            )
            answer = response['choices'][0]['message']['content'].strip().replace('.', '')
            # 혹시 예외적 출력 보정
            if '긍정' in answer:
                return '긍정'
            elif '부정' in answer:
                return '부정'
            elif '중립' in answer:
                return '중립'
            else:
                return '중립'
        except Exception:
            return '중립'