import requests
import json
 
headers = {"Content-Type" : "application/json"}
prompt = {'inputs' : '안녕 반가워 네 이름이 뭐니?'}
with requests.post("http://localhost:8001/gen", data=json.dumps(prompt), headers=headers) as response:
    if response.ok:
        print(response.content)
    else:
        print('fail!')