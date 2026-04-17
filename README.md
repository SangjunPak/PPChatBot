# PPChatBot
교육용 RAG베이스의 챗봇

## 실행환경
lmstudio 설치 후에, gemma4-e4b 등 언어모델을 다운로드받아 설치한다. (코드내에 .env 에서 model과 endpoint수정가능)
Delevoper탭에서 Local Server에서 Status를 Running 으로 돌려서 서버를 실행시켜 놓는다.
<img width="1114" height="179" alt="image" src="https://github.com/user-attachments/assets/1f972f37-04d8-4690-8905-954ced949e6b" />

코드는 Developer Docs에서 Anthropic Compatible Endpoints를 사용했다.
<img width="958" height="321" alt="image" src="https://github.com/user-attachments/assets/369dae85-a549-476e-bf92-7442f5abfc9b" />

## RAG 실행환경
현재 코드는 ElasticSearch 로컬 설치버젼으로 구성되어있는데, 테스트가 더 필요한 상황이다. 
.env의 USE_RAG 으로 Renanking 모델 및 Vector DB를 사용가능하게 만든 뒤 최적화 코딩을 해야한다. 

## 실행방법
개발유연성을 위해 stream api 와 streamlit 을 분리했기 때문에
한 터미널에서 a.bat 로 fastapi 서버를 실행시켜준 다음에
다른 터미널에서 s.bat 로 streamlit 을 실행해주면 된다. 

## 실행화면

<img width="1482" height="1034" alt="image" src="https://github.com/user-attachments/assets/ddbf8c15-6bae-40bc-887f-7b0e5ffaa83f" />
