import os
 
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
 
load_dotenv(verbose=True)
 
user = os.getenv('user')
password = os.getenv('password')
 
es = Elasticsearch(hosts=['https://localhost:9200'],
                   http_auth=(user, password),
                   verify_certs=False)
 
print(es.cluster.health())