import json
import requests
 
def embedding(sentences: list):
    headers = {'Content-Type': 'application/json'}
    prompt = {'instances' : sentences}
    with requests.post("http://sds-embed.serving.70-220-152-1.sslip.io/v1/models/embed:predict",
                        data=json.dumps(prompt),
                        headers=headers, stream=True) as response:
        # Embedding 객체에서 임베딩 벡터만 추출하여 리스트로 변환
        return response.json()['predictions']
 
if __name__ == '__main__':
    # 호출할 텍스트
    texts = [
        "하나 둘 추억이 떠오르면 많이 많이 그리워 할거야. 고마웠어요 그래도 이제는 사건의 지평선 너머로",
        "하루에 네 번 사랑을 말하고 여덟 번 웃고 여섯 번의 키스를 해줘."
    ]
 
 
    # Embedding 객체에서 임베딩 벡터만 추출하여 리스트로 변환
    embedding_list = [embed for embed in embedding(texts)]
    print(embedding_list)
    #print(len(embedding_list[0]))