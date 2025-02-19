import os
from dotenv import load_dotenv
import json
import time

import streamlit as st
import requests #fastapi와 streamlit을 합치기 위한 requests(내부에서 도는 fastapi에 요청을 보냄)

#음성인식라이브러리 추가
import speech_recognition as sr  # 음성 인식을 위한 라이브러리

FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://lang-backend-d0e71d3434e0.herokuapp.com/")

def main():
    st.set_page_config(page_title="MyGPT", layout="wide")
    
    # 탭 생성
    tab1, tab2 = st.tabs(["음성 챗", "일반 챗"])
    
    with tab1:
        st.header("🎙️ 음성 챗")
        st.write("여기에 음성 채팅 기능을 추가하세요.")

        if st.button("🎤 음성 입력 시작"):
            user_input = recognize_speech()  # 음성 인식W
    
            response = requests.post(url = f"{FASTAPI_URL}/voice", 
                                        data = json.dumps({'inputs':user_input}))       
            
            #print(response -> <200>)
            st.write(f"{response.json()}")
        
        else:
            user_input = ""
            st.write(f"음성 인식 버튼을 다시 누르고 말해보세요.")

    
    with tab2:
        # CSS 스타일 추가 (말풍선 디자인)
        st.markdown(
            """
            <style>
            .chat-container {
                max-width: 700px;
                margin: wide;
            }
            
            .user-message {
                background-color: #84c673;
                color: black;
                padding: 10px 15px;
                border-radius: 20px;
                max-width: 60%;
                text-align: right;
                margin-left: auto;
                margin-bottom: 10px;
                display: wide;
                justify-content: flex-end;
            }
            
            .bot-message {
                background-color: #73c2c6;
                color: black;
                padding: 10px 15px;
                border-radius: 20px;
                max-width: 60%;
                text-align: left;
                margin-right: wide;
                margin-bottom: 10px;
                display: wide;
                justify-content: flex-start;
            }

            .chat-box {
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 10px;
                background-color: #f9f9f9;
                margin-bottom: 20px;
                max-height: 400px;
                overflow-y: auto;
            }
            
            .chat-container div {
                display: flex;
                margin-bottom: 5px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # 채팅 기록 세션 상태 초기화
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        st.header("💬 일반 챗")
        st.write("텍스트 기반 챗 기능입니다. AI에게 어떤 말을 하고 싶으세요?")

        # 채팅 표시 영역
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)

        for chat in st.session_state.chat_history:
            if chat["sender"] == "user":
                st.markdown(f'<div class="chat-container"><div class="user-message">{chat["text"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-container"><div class="bot-message">{chat["text"]}</div></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # 사용자 입력 받기
        user_input = st.text_input("메시지를 입력하세요:", key="chat_input")

        if st.button("전송") and user_input.strip():
            response = requests.post(url=f"{FASTAPI_URL}/chat", 
                                    data=json.dumps({'inputs': user_input, 'history': []}))

            # 응답 받아오기
            st.write(response)
            bot_response = response.json()

            # 채팅 기록 저장
            st.session_state.chat_history.append({'sender': 'user', 'text': user_input})
            st.session_state.chat_history.append({'sender': 'bot', 'text': bot_response})

            # UI 업데이트
            st.rerun()

#클라우드 배포는 tab2까지..
    # with tab3:
    #     st.write('데이터베이스 기반의 챗봇 질의응답을 지원합니다.')
    #     user_input = st.text_input('자료를 업로드하고, 자료와 관련된 질문을 아래에 입력하세요.', key='db_input')
        
    #     radio_button = st.radio('답변에 DATABASE 활용 선택', ['사용함', '사용하지 않음'])

    #     disabled_status = radio_button == '사용하지 않음'

    #     options = st.selectbox("데이터베이스 테이블명을 선택하세요", 
    #                        ['finance', 'life', 'stocks'], 
    #                        disabled=disabled_status)

    #     if st.button("전송", key='senddbkey') and user_input.strip():
    #         response = requests.post(url = f"http://127.0.0.1:8000/db", 
    #                                 json = {'inputs':user_input, 'dbtable': str(options)})

    #         st.write(response.json())


def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 음성을 입력하세요...")
        recognizer.adjust_for_ambient_noise(source)  # 주변 소음 조정
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="ko-KR")  # 한국어 인식
        st.success(f"🗣 인식된 음성: {text}")
        return text
    
    except sr.UnknownValueError:
        st.error("음성을 인식할 수 없습니다. 다시 시도해 주세요.")
        return ""
    
    except sr.RequestError:
        st.error("음성 인식 서비스에 연결할 수 없습니다.")
        return ""

if __name__ == "__main__":
    main()
