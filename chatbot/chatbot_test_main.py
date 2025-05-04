from chatbot import ChatbotSession

def main():
    session = ChatbotSession()
    finished = False

    print(session.get_current_node()["message"])
    choices = session.get_current_node().get("choices")
    if choices:
        print("선택지: ", choices)

    while not finished:
        user_input = input("\n[나] ")
        
        # multi-choice 입력을 쉼표로 구분하여 입력 가능
        node_type = session.get_current_node()["type"]
        if node_type == "multi_choice" and ',' in user_input:
            user_input = [x.strip() for x in user_input.split(',')]
        
        res = session.process_input(user_input)
        print("\n[챗봇]", res["message"])
        if res.get("choices"):
            print("선택지:", res["choices"])
        if session.current_id == "end":
            finished = True

if __name__ == "__main__":
    main()