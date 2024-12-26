from pydantic import BaseModel
 
 
class Query(BaseModel):
    inputs: str
    parameters: object
 
 
class Collection(BaseModel):
    name: str
    metadata: dict
    persist: bool
 
 
class Passages(BaseModel):
    indexname: str
    documents: list
 
 
class VectorData(BaseModel):
    indexname: str
    document: list
    embedding: list[list]
 
 
class VectorSearchRequest(BaseModel):
    index_name: str
    query_vector: list[float]
    k: int
    threshold : float
 
 
class IndexSchema(BaseModel):
    index_name: str
    mappings: dict
    settings: dict = None 