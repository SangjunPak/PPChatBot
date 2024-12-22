from dependency.elastic import get_all_index, make_index, delete_index
from dependency.elastic import search_by_filename, search_by_id
from dependency.elastic import delete_by_filename, delete_by_id

import streamlit as st

st.set_page_config(
    page_title="PP RAG Repo",
    layout="wide",
)
 
st.title(":file_folder: Repo")
st.write("Chatbot RAG 저장소")
st.write('Gen AI PP용 입니다.')
 
with st.sidebar:
    collection_names = []
 
    try:
        collection_info = get_all_index()
        # print(collection_info)
        if collection_info['response'].status_code == 200:
            for name in collection_info['message']['names']:
                if (name[0] != '.'): collection_names.append(name) # = collection_info['message']['names']
        else:
            st.error(collection_info['message'])
         
    except Exception as e:
        st.error(f"실행 중 오류가 발생했습니다. {e}")
 
    selected_option = st.selectbox('index를 선택하세요', collection_names, placeholder='index를 선택하세요.',
                                   label_visibility='visible')
 
with st.expander("Index 관리하기", expanded=False):
    with st.form("Get Indices", border=True):
        st.write("인덱스 조회하기")
        create_button = st.form_submit_button("조회하기", use_container_width=True)
        if create_button:
            try:
                collection_info = get_all_index()
                if collection_info['response'].status_code == 200:
                    st.json(collection_info['message'])
                else:
                    st.error(collection_info['message'])                
            except Exception as e:
                st.error(f"실행 중 오류가 발생했습니다. {e}")
 
    with st.form("Create index", border=True):
        st.write("인덱스 생성하기")
        name = st.text_input(label="name", placeholder="생성할 Index 이름을 입력하세요.")
         
        create_button = st.form_submit_button("create", use_container_width=True)
        if create_button:
            try:
                index_info = make_index(name)
                if index_info['response'].status_code == 200:
                    st.success(f"Index : {name} 등록이 성공적으로 완료됐습니다.")
                else:
                    st.error(index_info['message'])                
            except Exception as e:
                st.error(f"실행 중 오류가 발생했습니다. {e}")
 
    with st.form("Delete Index", border=True):
        st.write("인덱스 지우기")
        name = st.text_input(label="name", placeholder="지울 index 이름을 입력하세요.")
 
        create_button = st.form_submit_button("Delete", use_container_width=True)
        if create_button:
            try:
                index_info = delete_index(name)
                if index_info['response'].status_code == 200:
                    st.success(f"Index : {name}이 성공적으로 제거됐습니다.")
                else:
                    st.error(index_info['message'])                
                
            except Exception as e:
                st.error(f"실행 중 오류가 발생했습니다. {e}")

from dependency.preprocessing import store_file_from_uploader
 
col1 = st.container()
with col1.form("Upload File"):
    uploaded_file = st.file_uploader(
        "Upload files",
        ["txt", "html"],
        accept_multiple_files=False,
        label_visibility="hidden",
    )
    submit_button = st.form_submit_button("Submit", use_container_width=True)
 
    if submit_button and uploaded_file and selected_option:
        try:
            result = store_file_from_uploader(selected_option, uploaded_file)
            if result.status_code == 200:
                st.success(f"파일\n {uploaded_file}\n 업로드가 성공적으로 완료됐습니다.")
            else:
                st.warning(f"파일\n {uploaded_file}\n 업로드에 실패했습니다.")
        except Exception as e:
            st.warning(
                f"파일\n {uploaded_file}\n 파일 업로드 하는데 오류가 발생했습니다.{e}"
            )

from dependency.elastic import fetch_all
with st.expander("Search Tool", expanded=False):
    with st.form("Document", border=False):
        ids = st.text_input(label="id", placeholder="id를 입력하세요.")
        file_name = st.text_input(
            label="filename", placeholder="파일 이름을 입력하세요."
        )
  
        bt01, bt02, bt03, bt04, bt05 = st.columns([1, 1, 1, 1, 1])
        submit_button1 = bt01.form_submit_button("search all", use_container_width=True)
        submit_button2 = bt02.form_submit_button("search", use_container_width=True)
        submit_button3 = bt03.form_submit_button("delete", use_container_width=True)
        submit_button4 = bt04.form_submit_button("get filename", use_container_width=True)
        submit_button5 = bt05.form_submit_button("refresh", use_container_width=True)
  
        if submit_button5:
            st.empty()
  
        if submit_button1:
            try:
                passages_list = fetch_all(selected_option)
                if passages_list.status_code == 200:
                    if not passages_list:
                        st.warning(f"파일이 없습니다.")
                    else:
                        passages_data_list = passages_list.json()['data']
                        reference_text = ""

                        page = st.number_input('페이지 번호', min_value=1, max_value=1 if len(passages_data_list) < 10 else (
                                    len(passages_data_list) // 10),
                                               step=1)                          
                        # 실습
                        start = (page - 1) * 10
                        end = len(passages_data_list) if len(passages_data_list) < 10 else start + 10
                      
                        # # 페이지네이션 버튼 표시
                        st.write(f'현재 페이지: {page}')
  
                        # 데이터 10개씩 슬라이싱
                        for i in range(start, end):
                            id = passages_data_list[i]['id']
                            datas = passages_data_list[i]['source']
                      
                            sr_text = "-" * 50 + "\n"
                            sr_text += f"##### document {i + 1}\n"
                            sr_text += f"- **id** : {id}\n"
                      
                            for k, v in datas.items():
                                if k == 'content' or k == 'embedding':
                                    continue
                                sr_text += f"- **{k}**: {v}\n"
                            sr_text += f"```" + f"\n{datas['content']}\n" + f"```\n"
                            reference_text += sr_text
                        st.markdown(reference_text)
                else:
                    st.error(f"Error: {passages_list.status_code} - {passages_list.text}")
            except Exception as e:
                st.error(f"{file_name} 파일을 찾는데 오류가 발생했습니다. {e}")

        if submit_button2 and file_name:
            try:
                result = search_by_filename(selected_option, file_name)
                if result.status_code == 200:
                    result = result.json()
                    if not result['content']:
                        st.warning(f"파일이 없습니다.")
                    else:
                        passages_data_list = result['content']
            
                        # 페이지 번호 설정
                        page = st.number_input('페이지 번호', min_value=1,
                                            max_value=1 if len(passages_data_list) < 10 else (len(passages_data_list) // 10),
                                            step=1)
            
                        # 페이지네이션 버튼 표시
                        st.write(f'현재 페이지: {page}')
            
                        # 데이터 10개씩 슬라이싱
                        start_row = (page - 1) * 10
                        end_row = len(passages_data_list) if len(passages_data_list) < start_row + 10 else start_row + 10
            
                        reference_text = ""
            
                        for i in range(start_row, end_row):
                            sr_text = "-" * 50 + "\n"
                            sr_text += f"##### document {i + 1}\n"
            
                            for k, v in passages_data_list[i].items():
                                if k == 'content':
                                    continue
                                sr_text += f"- **{k}**: {v}\n"
                            sr_text += f"```" + f"\n{passages_data_list[i]['content']}\n" + f"```\n"
                            reference_text += sr_text
                        st.markdown(reference_text)
                else:
                    st.error(f"Error: {result.status_code} - {result.text}")
            except Exception as e:
                st.error(f"{file_name} 파일을 찾는데 오류가 발생했습니다. {e}")
            
        if submit_button2 and ids:
            try:
                result = search_by_id(selected_option, ids)
                if result.status_code == 200:
                    result = result.json()
                    if not result['content']:
                        st.warning(f"파일이 없습니다.")
                    else:
                        passages_data_list = result['content']
                        # 페이지 번호 설정
                        page = st.number_input('페이지 번호', min_value=1,
                                            max_value=1 if len(passages_data_list) < 10 else (
                                                        len(passages_data_list) // 10),
                                            step=1)
            
                        # 페이지네이션 버튼 표시
                        st.write(f'현재 페이지: {page}')
            
                        # 데이터 10개씩 슬라이싱
                        start_row = (page - 1) * 10
                        end_row = len(passages_data_list) if len(
                            passages_data_list) < start_row + 10 else start_row + 10
            
                        reference_text = ""
            
                        for i in range(start_row, end_row):
                            sr_text = "-" * 50 + "\n"
                            sr_text += f"##### document {i + 1}\n"
            
                            for k, v in passages_data_list[i].items():
                                if k == 'content':
                                    continue
                                sr_text += f"- **{k}**: {v}\n"
                            sr_text += f"```" + f"\n{passages_data_list[i]['content']}\n" + f"```\n"
                            reference_text += sr_text
                        st.markdown(reference_text)
                else:
                    st.error(f"Error: {result.status_code} - {result.text}")
            except Exception as e:
                st.error(f"{file_name} 파일을 찾는데 오류가 발생했습니다. {e}")

        if submit_button3 and ids:
            try:
                result = delete_by_id(selected_option, ids)
                if result.status_code == 200:
                    if not result:
                        st.warning(f"파일이 없습니다.")
                    else:
                        result = result.json()
                        st.success(f"{file_name} 파일을 모두 삭제했습니다.")
                else:
                    st.error(f"Error: {result.status_code} - {result.text}")
            except Exception as e:
                st.error(f"{ids} 파일을 삭제하는데 오류가 발생했습니다. {e}")

        if submit_button3 and file_name:
            try:
                result = delete_by_filename(selected_option, file_name)
                if result.status_code == 200:
                    if not result:
                        st.warning(f"파일이 없습니다.")
                    else:
                        result = result.json()
                        st.success(f"{file_name} 파일을 모두 삭제했습니다.")
                else:
                    st.error(f"Error: {result.status_code} - {result.text}")
            except Exception as e:
                st.error(f"{file_name} 파일을 삭제하는데 오류가 발생했습니다. {e}")

        from collections import Counter
        if submit_button4:
            try:
                passages_list = fetch_all(selected_option)
                if passages_list.status_code == 200:
                    if not passages_list:
                        st.warning(f"파일이 없습니다.")
                    else:
                        passages_data_list = passages_list.json()['data']
    
                        files = []
                        for passage in passages_data_list:
                            datas = passage['source']
                            files.append(datas.get('filename'))
    
                        counter = Counter(files)
                        file_info = {key: count for key, count in counter.items() if count > 1}
    
                        # 페이지 번호 설정
                        page = st.number_input('페이지 번호', min_value=1, max_value=1 if len(file_info) < 10 else (
                                len(file_info) // 10),
                                                step=1)
    
                        # # 페이지네이션 버튼 표시
                        st.write(f'현재 페이지: {page}')
    
                        # # 데이터 10개씩 슬라이싱
                        start_row = (page - 1) * 10
                        end_row = len(file_info) if len(
                            file_info) < start_row + 10 else start_row + 10

                        reference_text = ""
                    #     # 키를 추출하여 리스트에 저장
                    #     keys = list(file_info.keys())
                    #     # 값을 추출하여 리스트에 저장
                    #     values = list(file_info.values()) 
                    #    # 실습 코드 작성
                    #     for i in range(start_row, end_row):
                    #         reference_text += f"""
                    #         -----------------------------------
                    #             #####{keys[i]}
                    #             **{values[i]} pages***
                    #         """

                        for (key, value) in list(file_info.items())[start_row:end_row]:
                            sr_text = "-" * 50 + "\n"
                            sr_text += f"##### {key}\n"
                            sr_text += f"- **page**: {value}\n"
                            reference_text += sr_text
                        st.markdown(reference_text)
                else:
                    st.error(f"Error: {passages_list.status_code} - {passages_list.text}")
            except Exception as e:
                st.error(f"{file_name} 파일을 찾는데 오류가 발생했습니다. {e}")
