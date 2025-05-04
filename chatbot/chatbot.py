import json, os
from keyword_extractor import KeywordExtractor

# chatflow.json 위치를 data 폴더 하위로 지정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOW_PATH = os.path.join(BASE_DIR, "data", "chatflow.json")

with open("chatbot_flow.json", encoding='utf-8') as f:
    CHAT_FLOW = json.load(f)["chatbot_flow"]

def get_node_by_id(node_id):
    return next((node for node in CHAT_FLOW if node["id"] == node_id), None)

class ChatbotSession:
    def __init__(self):
        self.current_id = "start"
        self.extractor = KeywordExtractor()
        self.summary = {
            "content_type": [],
            "genre": [],
            "mood": [],
            "style": []
        }

    def get_current_node(self):
        return get_node_by_id(self.current_id)

    def process_input(self, user_input):
        node = self.get_current_node()
        input_choice = None

        # 선택지 타입 처리
        if node["type"] in ["choice", "multi_choice"]:
            if isinstance(user_input, list):
                input_choice = [c for c in user_input if c in node.get("choices", [])]
                # 자유 입력 있으면 키워드 추출 혼합
                non_choices = [c for c in user_input if c not in node.get("choices",[])]
                for txt in non_choices:
                    input_choice += self.extractor.extract(txt)
            elif user_input in node.get("choices", []):
                input_choice = user_input
            else: # 자유 입력 → 키워드 추출
                kw = self.extractor.extract(user_input)
                input_choice = kw if node["type"] == "multi_choice" else (kw[0] if kw else "")

        else: # 자유 양식 (예: 요약 확인 등)
            input_choice = user_input

        # 플로우/응답 갱신
        if node["id"] == "start":
            self.summary["content_type"] = input_choice if isinstance(input_choice, list) else [input_choice]
            if isinstance(input_choice, list):
                main = [c for c in input_choice if c in node["next"]]
                next_id = node["next"][main[0]] if main else node["next"]["잘 모르겠어요"]
            else:
                next_id = node["next"].get(input_choice, node["next"]["잘 모르겠어요"])
        elif node["id"] in ["movie_genre", "performance_genre", "exhibition_genre"]:
            self.summary["genre"] = input_choice if isinstance(input_choice, list) else [input_choice]
            next_id = node["next"]
        elif node["id"] in ["mood_question", "help_decide_content"]:
            self.summary["mood"] = input_choice if isinstance(input_choice, list) else [input_choice]
            next_id = node["next"]
        elif node["id"] == "style_question":
            self.summary["style"] = input_choice if isinstance(input_choice, list) else [input_choice]
            next_id = node["next"]
        elif node["id"] == "summary_check":
            if isinstance(input_choice, str) and input_choice.strip():
                self.summary["other"] = input_choice.strip()
            next_id = node["next"]
        else:
            next_id = node.get("next", "end")

        self.current_id = next_id

        # summary_check 시 응답 메시지에 요약 템플릿 적용
        reply_node = get_node_by_id(self.current_id)
        msg = reply_node["message"]
        if self.current_id == "summary_check":
            msg = msg.replace("{{content_type}}", ', '.join(self.summary.get("content_type", [])))
            msg = msg.replace("{{genre}}", ', '.join(self.summary.get("genre", [])))
            msg = msg.replace("{{mood}}", ', '.join(self.summary.get("mood", [])))
            msg = msg.replace("{{style}}", ', '.join(self.summary.get("style", [])))
        return {
            "message": msg,
            "choices": reply_node.get("choices", None),
            "type": reply_node["type"],
            "summary": self.summary if self.current_id == "summary_check" else None
        }