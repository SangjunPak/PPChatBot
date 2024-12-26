import requests
import json
 
def reranking(user_prompt, passages, threshold, top_k):
    if not passages:
        return passages
    contents_list = [[user_prompt, passage['source']['content']] for passage in passages]
 
    headers = {'Content-Type': 'application/json'}
    prompt = {'instances' : contents_list}

    with requests.post("http://sds-rerank.serving.70-220-152-1.sslip.io/v1/models/rerank:predict",
                        data=json.dumps(prompt),
                        headers=headers) as response:
         
        reranking_scores = response.json()['predictions']
    #print(reranking_scores)
    for idx, reranking_score in enumerate(reranking_scores):
        passages[idx]['source']['rerank_score'] = reranking_score
     
    passages.sort(key=lambda x: x['source']["rerank_score"], reverse=True)
    passages_size = len(passages) if len(passages) < top_k else top_k
    passages = passages[:passages_size]
 
    threshold_idx = -1
    for idx, passage in enumerate(passages, start=0):
        if passage['source']['rerank_score'] < threshold:
            threshold_idx = idx
            break
     
    return passages if threshold_idx == -1 else passages[:threshold_idx]