import json
import os
import uuid
 
import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
 
load_dotenv()
IMAGE_DIFF_ENDPOINT = os.getenv('IMAGE_DIFF_ENDPOINT')
 
st.set_page_config(
    page_title='PP Make Image!',
    layout='wide',
)
st.title(':sparkles: PP Image Diffusion')
st.write('Gen AI PP용 입니다.')
 
with st.sidebar:
    with st.form("clean", border=False, clear_on_submit=True):
        clear_submit_button = st.form_submit_button("refresh", use_container_width=True)
 
        if clear_submit_button:
            st.empty()
            st.session_state.images = []
 
    expender_cont = st.container()
    with expender_cont.expander("n times 설정", expanded=False):
        _n_times = st.slider("n_times", 1, 10000, 40)
 
if 'images' not in st.session_state:
    st.session_state.images = []
 
with st.form("이미지 생성", border=True, clear_on_submit=False):
    diffusion_prompt = st.text_area('이미지 생성을 위한 프롬프트를 입력하세요.', height=70)
    headers = {'Content-Type': 'application/json'}
    prompt = {
        'inputs': f'당신은 한국어를 영어로 번역하는 전문가입니다.\n 한국어 문장을 받으면 한국어 문장의 의미를 최대한 살려서 영어로 번역해고, 영어로만 답변해야합니다.\n ### 문장 : {diffusion_prompt}\n ### 답변 :',
        "parameters": {
            "max_new_tokens": 4096,
            "stop": ['<|endoftext|>']
        }
    }
 
    make_button = st.form_submit_button("이미지 생성", use_container_width=True)
 
    if diffusion_prompt and make_button:
        with requests.post("http://sr-llm-65b-instruct.serving.70-220-152-1.sslip.io", data=json.dumps(prompt),
                           headers=headers) as response:
            eng_prompt = ''
            if response.ok:
                eng_prompt = json.loads(response.content.decode('utf-8'))[0]['generated_text']
 
            headers = {'Content-Type': 'application/json'}
            raw = {
                "inputs": eng_prompt,
                "parameters": {
                    "n_steps": _n_times
                }
            }
            prompt['inputs'] = f'make suitable short filename that describes {eng_prompt} within 20 bytes. Answer should be only a filename, not including any explanations, extensions, A: like answer marks'
            with requests.post("http://sr-llm-65b-instruct.serving.70-220-152-1.sslip.io", data=json.dumps(prompt),
                            headers=headers) as response:
                filename_prompt = ''  
                if response.ok:
                    filename_prompt = json.loads(response.content.decode('utf-8'))[0]['generated_text']

                with requests.post(IMAGE_DIFF_ENDPOINT, data=json.dumps(raw), headers=headers) as response:
                    if response.ok:
                        ori_name = filename_prompt
                        image_name = filename_prompt.replace('A: ','').replace('"','').replace('\n','').replace('.jpg','').replace(', etc.','') #uuid.uuid4()
                        print(f"image_name:{image_name}")
                        for data in st.session_state.images:
                            print(data['filename'])
                            if (data['filename'] == image_name):
                                image_name += "_1"
                        output_image = response.content
                        with open(f"./files/images/{image_name}.png", "wb") as f:
                            f.write(output_image)
                            st.session_state.images.append(
                                {'filename': image_name, 'prompt': diffusion_prompt, 'eng': eng_prompt,
                                'n_times': _n_times})
                            st.success('이미지 생성이 완료됐습니다!')
    
                            my_image = Image.open(f"./files/images/{st.session_state.images[-1]['filename']}.png")
                            st.image(my_image, use_container_width=True)
                    else:
                        st.error(f'{response.status_code} - 이미지 생성 에러가 발생했습니다.')
 
with st.expander('History', expanded=True):
    images_list = [st.session_state.images[i:i + 4] for i in range(0, len(st.session_state.images), 4)]
 
    # 이미지 파일 리스트를 순회하며 각각의 이미지를 화면에 표시
    for images in images_list:
        col1, col2, col3, col4 = st.columns(4)
        max_len = len(images)
        with col1:
            if 0 < max_len:
                img = Image.open(f'./files/images/{images[0]["filename"]}.png')
                st.image(img, caption=f'{images[0]["filename"]}')
                st.markdown(f'###### {images[0]["prompt"]} **```n_times : {images[0]["n_times"]}```**')
                st.write(f'{images[0]["eng"]}')
        with col2:
            if 1 < max_len:
                img = Image.open(f'./files/images/{images[1]["filename"]}.png')
                st.image(img, caption=f'{images[1]["filename"]}')
                st.markdown(f'###### {images[1]["prompt"]} **```n_times : {images[1]["n_times"]}```**')
                st.write(f'{images[1]["eng"]}')
        with col3:
            if 2 < max_len:
                img = Image.open(f'./files/images/{images[2]["filename"]}.png')
                st.image(img, caption=f'{images[2]["filename"]}')
                st.markdown(f'###### {images[2]["prompt"]} **```n_times : {images[2]["n_times"]}```**')
                st.write(f'{images[2]["eng"]}')
        with col4:
            if 3 < max_len:
                img = Image.open(f'./files/images/{images[3]["filename"]}.png')
                st.image(img, caption=f'{images[3]["filename"]}')
                st.markdown(f'###### {images[3]["prompt"]} **```n_times : {images[3]["n_times"]}```**')
                st.write(f'{images[3]["eng"]}')