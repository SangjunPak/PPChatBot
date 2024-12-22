import json
import requests

from dependency.emb import embedding
from dependency.class_def import VectorData
 
headers = {'Content-Type': 'application/json'}

def make_index(name : str):
    data = {
        'index_name' : name,
        'mappings' : {
            'properties' : {
                'ids' : {'type': 'text'},
                'documents' : {'type': 'text'},
                'embedding' : {'type': 'dense_vector',
                                'dims': 1024}
            }
        },
        'settings' : {
            'number_of_shards': 1,
            'number_of_replicas': 1
        }
    }
    with requests.post("http://localhost:8001/create_index", data=json.dumps(data), headers=headers) as response:
        if response.ok:
            return {'message' : f'{name} index is created', 'response' : response}
        else:
            return {'message' : f'{name} index is not created : {response.status_code} - {response.text}', 'response' : response }
 
def delete_index(name : str):
    with requests.delete(f"http://localhost:8001/delete_index/{name}", headers=headers) as response:
        if response.ok:
            return {'message' : f'{name} index is deleted', 'response' : response}
        else:
            return {'message' : f'{name} index is not deleted : {response.status_code} - {response.text}', 'response' : response }
 
def get_all_index():
    with requests.get("http://localhost:8001/indices", headers=headers) as response:
        if response.ok:
            return {'message' : response.json(), 'response' : response }
        else:
            return {'message' : f'{response.status_code} - {response.text}', 'response' : response }
 
def get_index_by_name(name : str):
    with requests.get(f"http://localhost:8001/indices/{name}", headers=headers) as response:
        if response.ok:
            return {'message' : response.json(), 'response' : response }
        else:
            return {'message' : f'{response.status_code} - {response.text}', 'response' : response }


def add_data(index_name : str, document : list):
    headers = {'Content-Type': 'application/json'}
    # 실습 : content만 embedding 하고 싶은 경우
    contents = [item["content"] for item in document]
     
    # 실습 : embedding 함수를 호출하여 embedding_list 호출하는 경우
    embedding_list = embedding(contents)
    payload = VectorData(
        indexname = index_name,
        document= document,
        embedding= embedding_list
    )
 
    response = requests.post(f"http://localhost:8001/add_vector_data", data=json.dumps(payload.model_dump()), headers=headers)
    if response.status_code == 200:
        return response
    else:
        return response

def fetch_all(index_name : str):
    params = {
        'index_name' : index_name,
    }
    response = requests.get("http://localhost:8001/fetch_all", params=params)
    if response.status_code == 200:
        return response
    else:
        return response


def search_by_filename(indexname : str, filename :str):
     with requests.get(f"http://localhost:8001/search/{indexname}?filename={filename}") as response:
        if response.status_code == 200:
            return response
        else:
            return response
 
def search_by_id(indexname : str, id :str):
     with requests.get(f"http://localhost:8001/search/{indexname}/{id}") as response:
        if response.status_code == 200:
            return response
        else:
            return response
        
def delete_by_id(indexname : str, id :str):
     with requests.delete(f"http://localhost:8001/delete/{indexname}/{id}") as response:
        if response.status_code == 200:
            return response
        else:
            return response
 
def delete_by_filename(indexname : str, filename :str):
     with requests.delete(f"http://localhost:8001/delete/{indexname}?filename={filename}") as response:
        if response.status_code == 200:
            return response
        else:
            return response

def retrieve(index_name : str, query : str, threshold : float, top_k : int):
    headers = {'Content-Type': 'application/json'}
    embed_query = embedding([query])[0]
  
    payload = {
        'index_name' : index_name,
        'query_vector' : embed_query,
        'k' : top_k,
        'threshold' : threshold
    }
  
    response = requests.post(f"http://localhost:8001/search", data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        return response
    else:
        return response

if __name__ == '__main__':
    print(make_index('my_index'))
    print(get_all_index())
    print(get_index_by_name('my_index'))
    print(delete_index('my_index'))

    