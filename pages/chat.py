import json
import os
   
import requests
import streamlit as st
from dotenv import load_dotenv
from dependency.prompt import llm_query, system_prompt, base_prompt_rag, base_prompt, llm_query_rag

from dependency.elastic import get_all_index

load_dotenv(verbose=True)
LLM_ENDPOINT = os.getenv('LLM_ENDPONT')
USE_RAG = os.getenv('USE_RAG') == 'True'

st.set_page_config(
    page_title='PP chatbot',
    layout='wide',
)
st.title(':balloon: PP 챗봇')
st.write('Gen AI PP용 입니다.')
   
with st.sidebar:
    with st.form("clean", border=False, clear_on_submit=True):
        clear_submit_button = st.form_submit_button("refresh", use_container_width=True)
   
        if clear_submit_button:
            st.empty()
            st.session_state.messages = []

    collection_names = []

    if USE_RAG: 
        try:
            collection_info = get_all_index()
            if collection_info['response'].status_code == 200:
                for name in collection_info['message']['names']:
                    if (name[0] != '.'): collection_names.append(name) # = collection_info['message']['names']
            else:
                st.error(collection_info['message'])
    
        except Exception as e:
            st.error(f"실행 중 오류가 발생했습니다. {e}")
    
        selected_option = st.selectbox('index를 선택하세요', collection_names, placeholder='index를 선택하세요.',
                                    label_visibility='visible')

        rag_on = st.toggle("지식 기반 검색")
    else:
        selected_option = None
        rag_on = False
    
    expender_cont = st.container()
    with expender_cont.expander('Retrieve', expanded=False):
        search_range = st.slider("retrieve 개수", 1, 50, 3)
        rerank_range = st.slider("reranking 개수", 1, 10, 3)
        search_threshold = st.slider("retrieve threshold", 0.0, 1.0, 0.1, step=0.1)
        rerank_threshold = st.slider("reranking threshold", 0.0, 1.0, 0.1, step=0.1)

    expender_cont = st.container()
    with expender_cont.expander("Model", expanded=False):
        max_new_tokens = st.slider("Max new tokens", 512, 2048, 1024, step=1)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.5, step=0.1)
        top_k = st.slider("Top K", 1, 50, 10, step=1)
        top_p = st.slider("Top P", 0.0, 1.0, 0.95, step=0.01)
        repetition_penalty = st.slider("Repetition Penalty", 1.0, 2.0, 1.03, step=0.01)

    expender_cont = st.container()
    with expender_cont.expander("Prompt", expanded=False):
        _system_prompt = st.text_area(label="System Prompt",
                                        height=300,
                                        value=system_prompt)
        _base_prompt_rag = st.text_area(label="Base Prompt with RAG",
                                        height=300,
                                        value=base_prompt_rag)
        _base_prompt = st.text_area(label="Base Prompt",
                                    height=300,
                                    value=base_prompt)
            
if 'messages' not in st.session_state:
    st.session_state.messages = []
   
for message in st.session_state.messages:
    if message['role'] == 'user':
        with st.chat_message(message['role']):
            st.markdown(message['content'])
   
    elif message['role'] == 'assistant':
        with st.chat_message(message['role']):
            st.markdown(message['content'])
        
        if message['reference']:
            with st.expander('References'):
                st.markdown(message['reference'])   

if user_prompt := st.chat_input('챗봇에게 물어보세요.'):
    st.chat_message('user').markdown(user_prompt)
   
    headers = {'Content-Type': 'application/json'}
    full_response = ''
    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        
        prompt = ''
        
        from dependency.prompt import rag_query, llm_query_rag
        from dependency.elastic import retrieve
        
        prompt = ''
        docs = ''
        reference_text = ''
        if selected_option and rag_on:               
            retrieved_res = retrieve(selected_option, user_prompt, search_threshold, search_range)
  
            if retrieved_res.status_code == 200:
                retrieved_res = retrieved_res.json()['results']
            else:
                retrieved_res = []
            #print(retrieved_res)
            from dependency.rerank import reranking
            retrieved_res = reranking(user_prompt, retrieved_res, rerank_threshold, rerank_range)
 
            with st.expander("References"):
                if retrieved_res:
                    reference_text += "---\n\n"
                    for i in range(len(retrieved_res)):
                        sr_text = f"#### Reference {i + 1}\n"
                        sr_text += f"- **id**: {retrieved_res[i]['id']}\n"
                        sr_text += f"- **score** {retrieved_res[i]['score']}\n"
                        for k, v in retrieved_res[i]["source"].items():
                            if k == 'content' or k == 'embedding':
                                continue
                            sr_text += f"- **{k}**: {v}\n"
                        sr_text += f"```\n" + f"{retrieved_res[i]["source"]['content']}\n" + f"```\n"
                        reference_text += sr_text
                st.markdown(reference_text)
            # 실습코드 작성하여, prompt 생성하기
            rag_docs = rag_query(retrieved_res)
            prompt = llm_query_rag(st.session_state.messages, rag_docs, user_prompt, _system_prompt,  _base_prompt_rag)
        else:
            prompt = llm_query(st.session_state.messages, user_prompt, _system_prompt, _base_prompt)
        #prompt = {'inputs' : prompt}
        st.session_state.messages.append({'role': 'user', 'content': user_prompt})
        
        target_parameter = {
                        'max_tokens' : max_new_tokens,
                        'temperature' : temperature,
                        'top_k' : top_k,
                        'top_p' : top_p,
                        'repetition_penalty' : repetition_penalty
                    }
        #print(prompt)
        
        from dependency.class_def import Query
        query = Query(
                    inputs = prompt,
                    parameters = target_parameter,
                )
        with requests.post("http://localhost:8001/gen", data=json.dumps(query.model_dump(), ensure_ascii=False), headers=headers,
                            stream=True) as response:        
            for chunk_info in response.iter_content(chunk_size=None):
                # bytes 데이터를 문자열로 디코딩
                string_data = chunk_info.decode("utf-8")
                # 문자열을 JSON으로 변환
                #print(string_data)

                current_event = None
                line_str = string_data[6:]
                if line_str.startswith('event'):
                    current_event = line_str[7:]
                elif line_str.startswith('data'):
                    data_str = line_str[6:]
                    #print(data_str)
                    if data_str.strip() != '':
                        try:
                            data = json.loads(data_str)
                            #print(current_event, data['delta'])

                            if 'delta' in data and data['delta'].get('type') == 'text_delta':
                                text = data['delta'].get('text', '')
                                full_response += text
                                message_placeholder.markdown(full_response + '● ')
                            elif current_event == 'message_stop':
                                break
                        except json.JSONDecodeError:
                            continue
                else:
                    print(line_str, line_str.startswith('event'), line_str.startswith('data'))

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({'role': 'assistant', 'content': full_response, 'reference' : reference_text})
        #print(st.session_state.messages)
