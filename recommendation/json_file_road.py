import json
import os


    # 1. JSON 파일 로드
def load_json_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    # 2. JSON 데이터를 텍스트로 변환
def json_to_text(json_data):
        # 모든 키워드를 하나의 문자열로 합침
        if isinstance(json_data, dict):
            return ' '.join([str(v) for v in json_data.values()])
        elif isinstance(json_data, list):
            return ' '.join([str(item) for item in json_data])
        return str(json_data)

def preprocessing(json_data):
     
    keyword_lists = []
    titles = []
    
    for movie in json_data['movies']:
        if movie['keywords']:
            keyword_text = ' '.join(movie['keywords'])
            keyword_lists.append(keyword_text)
            titles.append(movie['title'])
    
    return keyword_lists, titles

def main():
    file_path = "C:/Users/gpwl1/OneDrive/바탕 화면/25-1-Capston-FOREST/FOREST_AI/recommendation/data/demo_data.json"
    
    data = load_json_file(file_path)
    txt_data = json_to_text(data)
    print(txt_data)

if __name__ == "__main__":
    main()