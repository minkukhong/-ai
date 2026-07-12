import streamlit as st
import os
import requests
from langchain_community.tools.tavily_search import TavilySearchResults

st.set_page_config(page_title="AI Assistant", page_icon="🇰🇷")
st.title("용마고 생성형 AI")

try:
    os.environ["GOOGLE_API_KEY"] = str(st.secrets["GOOGLE_API_KEY"]).strip()
    os.environ["TAVILY_API_KEY"] = str(st.secrets["TAVILY_API_KEY"]).strip()
except Exception as e:
    st.error("API Key Error. Please check Streamlit Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("궁금한 것을 물어보세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                search = TavilySearchResults(k=3)
                search_results = search.run(prompt)

                full_prompt = f"당신은 해당 교육 기관의 전용 AI 안내 시스템입니다. 다음은 사용자와 나눈 이전 대화 기록입니다:\n{st.session_state.messages}\n\n웹 검색 결과:\n{search_results}\n\n사용자의 최신 질문: {prompt}\n\n위의 대화 기록과 검색 결과를 바탕으로, 외부의 엉뚱한 주식 정보나 무관한 개념은 배제하고 오직 대상 학교의 정보에만 집중하여 친절하게 한국어로 답변해줘."

                api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={os.environ['GOOGLE_API_KEY']}"
                headers = {"Content-Type": "application/json"}
                payload = {"contents": [{"parts": [{"text": full_prompt}]}]}

                response = requests.post(api_url, json=payload, headers=headers)
                result_json = response.json()

                if response.status_code == 200:
                    answer = result_json["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error: {result_json['error']['message']}")

            except Exception as e:
                st.error(f"Error: {e}")
