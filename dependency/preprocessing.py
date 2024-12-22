from langchain_text_splitters import RecursiveCharacterTextSplitter
from dependency.elastic import add_data
     
def store_file_from_uploader(index_name, uploaded_file):
    file_name = uploaded_file.name
    with open(f"./files/{file_name}", "wb") as f:
        f.write(uploaded_file.read())
 
    passages = convert_file_to_passage(f"./files/{file_name}")
    documents = [
        {
            "filename": file_name,
            "page": page,
            "content" : passage
        }
        for page, passage in enumerate(passages, start=1)
    ]
 
    return add_data(index_name, documents)
 
def chunking(texts):
    results = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len,
    )
 
    for text in texts:
        for t in text_splitter.split_text(text):
            results.append(t)
 
    return results
 
from bs4 import BeautifulSoup
def convert_file_to_passage(file_path, file_type=None):
    result = ['']
    if file_type is None:
        file_type = file_path.strip().split(".")[-1]
    if file_type == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            paragraphs = f.read()
        result = [paragraphs]
    elif file_type == "html":
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, 'html.parser')
            all_text = soup.get_text(strip=True)
        result = [all_text]
    return chunking(result)