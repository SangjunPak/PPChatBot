import json
import os
 
import requests
import uvicorn
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
 
from dependency.class_def import Query, IndexSchema

import uuid
 
from elasticsearch import helpers
from starlette.responses import Response
 
from dependency.class_def import VectorData
 
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(verbose=True)
LLM_ENDPOINT = os.getenv('LLM_ENDPONT')
 
app = FastAPI()
 
user = os.getenv('user')
password = os.getenv('password')
 
es = Elasticsearch(hosts=['https://localhost:9200'],
                   basic_auth=(user, password),
                   verify_certs=False)

@app.get("/home")
async def home():
    return {"message": "Home"}
 
 
@app.post("/gen")
async def get_llm(prompt: Query):
    return StreamingResponse(llm_streaming(prompt), media_type='text/event-stream')
 

def llm_streaming(prompt: Query):
    headers = {"Content-Type": "application/json"}
    raw = {
        "inputs": prompt.inputs,
        "parameters": {
            "best_of": 1,
            "do_sample": True,
            "max_new_tokens": prompt.parameters['max_new_tokens'],
            "repetition_penalty": prompt.parameters['repetition_penalty'],
            "return_full_text": False,
            "stop": ['<|endoftext|>'],
            "temperature": prompt.parameters['temperature'],
            "top_k": prompt.parameters['top_k'],
            "top_p": prompt.parameters['top_p'],
            "watermark": False
        }
    }
 
    with requests.post(LLM_ENDPOINT, data=json.dumps(raw), headers=headers, stream=True) as response:
        for chunk_info in response.iter_content(chunk_size=None):
            if chunk_info:
                try:
                    yield chunk_info
                except:
                    yield ""

@app.get("/")
async def root():
    return {"message": es.cluster.health()}
 
 
@app.post('/create_index')
async def create_index(index: IndexSchema):
    if es.indices.exists(index=index.index_name):
        raise HTTPException(status_code=400, detail="Index already exists")
 
    try:
        es.indices.create(index=index.index_name, body={'mappings': index.mappings,
                                                        'settings': index.settings})
        return {"message": "Index created"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.delete('/delete_index/{index_name}')
async def delete_index(index_name: str):
    try:
        if es.indices.exists(index=index_name):
            response = es.indices.delete(index=index_name)
            return {"message": "Index deleted"}
        else:
            raise HTTPException(status_code=404, detail="Index not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.get('/indices')
async def get_all_indices():
    try:
        indices_info = es.indices.get(index='*')
        indices_names = [k for k in indices_info.keys()]
        return {'names': indices_names,
                'details': indices_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.get('/indices/{index_name}')
async def get_index_by_name(index_name: str):
    try:
        indices_info = es.indices.get(index=index_name)
        return {'index_name': index_name, 'details': indices_info[index_name]}
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@app.post('/add_vector_data')
async def add_vector_data(vector_data: VectorData):
    try:
        actions = []
 
        for doc, embed in zip(vector_data.document, vector_data.embedding):
            doc_id = str(uuid.uuid4())
            action = {
                "_op_type": "index",
                "_index": vector_data.indexname,
                "_id": doc_id,
                "_source": {
                    **doc,
                    "embedding": embed
                }
            }
            actions.append(action)
 
        res = helpers.bulk(es, actions, refresh='wait_for')
        response_data = {"message": f"{vector_data.indexname} - {res[0]} Document added successfully"}
        return Response(content=json.dumps(response_data).encode(), status_code=200, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/fetch_all')
async def fetch_all_data(index_name: str):
    try:
        if not es.indices.exists(index=index_name):
            raise HTTPException(status_code=400, detail="Index not found")
 
        response = es.search(index=index_name, scroll='1m', size =1000)
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']
        all_hits = hits.copy()
 
        while len(hits) > 0:
            response = es.scroll(scroll_id=scroll_id, scroll='1m')
            hits = response['hits']['hits']
            all_hits.extend(hits)
 
        return {
            'message' : f'fetched {len(all_hits)} document from index {index_name}.',
            'data' : [
                {'id' : hit['_id'], 'source' : hit['_source']} for hit in all_hits
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/search/{indexname}')
async def search_by_filename(indexname: str, filename: str = None):
    if not filename:
        raise HTTPException(status_code=400, detail="Query parameter 'filename' is required")
 
    try:
        params = {
            "query": {
                "match": {
                    "filename": filename
                }
            }
        }
 
        response = es.search(index=indexname, body=params, scroll='1m', size=1000)
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']
        all_hits = hits.copy()
 
        while len(hits) > 0:
            response = es.scroll(scroll_id=scroll_id, scroll='1m')
            hits = response['hits']['hits']
            all_hits.extend(hits)
 
        results = []
        for hit in all_hits:
            results.append({
                "id": hit["_id"],
                'filename': hit['_source']['filename'],
                'page': hit['_source']['page'],
                'content': hit['_source']['content']
            })
 
        response_data = {"message": "Document searched successfully",
                         "content": results}
        return Response(content=json.dumps(response_data).encode(), status_code=200, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.get('/search/{indexname}/{id}')
async def search_by_id(indexname: str, id: str):
    try:
        params = {
            "query": {
                "match": {
                    "_id": id
                }
            }
        }
 
        response = es.search(index=indexname, body=params)
 
        hits = response['hits']['hits']
        results = []
        for hit in hits:
            results.append({
                "id": hit["_id"],
                'filename': hit['_source']['filename'],
                'page': hit['_source']['page'],
                'content': hit['_source']['content']
            })
 
        response_data = {"message": "Document searched successfully",
                         "content": results}
        return Response(content=json.dumps(response_data).encode(), status_code=200, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete('/delete/{indexname}')
async def delete_by_filename(indexname: str, filename: str = None):
    if not filename:
        raise HTTPException(status_code=400, detail="Query parameter 'filename' is required")
 
    try:
        params = {
            "query": {
                "match": {
                    "filename": filename
                }
            }
        }
 
        response = es.search(index=indexname, body=params, scroll='1m', size=1000)
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']
        all_hits = hits.copy()
 
        while len(hits) > 0:
            response = es.scroll(scroll_id=scroll_id, scroll='1m')
            hits = response['hits']['hits']
            all_hits.extend(hits)
 
        deleted_id_list = []
        for hit in all_hits:
            deleted_id_list.append(hit["_id"])
 
        bulk_data = [{'_op_type': 'delete', '_index': indexname, '_id': doc_id} for doc_id in deleted_id_list]
        res = helpers.bulk(es, bulk_data, refresh='wait_for')
        response_data = {"message": f"{indexname} - {res[0]} Document deleted successfully",
                         "count": res[0]}
        return Response(content=json.dumps(response_data).encode(), status_code=200, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@app.delete('/delete/{indexname}/{id}')
async def delete_by_id(indexname: str, id:str):
    try:
        response = es.delete(index=indexname, id=id)
        results = {
            'index' : response['_index'],
            'id' : response['_id'],
            'result' : response['result']
        }
 
        response_data = {"message" : "Document deleted successfully",
                         "content" : results}
        return Response(content=json.dumps(response_data).encode(), status_code=200, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from dependency.class_def import VectorSearchRequest
 
@app.post('/search')
async def search_by_vector_data(vector_data: VectorSearchRequest):
    try:
        query = {
            'size' : vector_data.k,
            'query' : {
                'function_score' : {
                    'query' : {'match_all' : {}},
                    'functions': [
                        {
                            'script_score' : {
                                'script' : {
                                    'source' : "cosineSimilarity(params.query_vector, 'embedding')",
                                    'params' : {'query_vector' : vector_data.query_vector}
                                }
                            }
                        }
                    ],
                    'min_score' : vector_data.threshold
                }
            }
        }
  
        response = es.search(index=vector_data.index_name, body=query)
  
        hits = response.get('hits', {}).get('hits', [])
        results = [
            {'id' : hit['_id'], 'score': hit['_score'], 'source' : hit['_source']} for hit in hits
        ]
  
        return {'results' : results }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8001)