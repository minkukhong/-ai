import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults

st.set_page_config(page_title="용마고 AI", page_icon="🇰🇷")
st.title("🚀 용마고 생산형 AI")

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
                
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=os.environ["GOOGLE_API_KEY"]
                )

                search_results = search.run(prompt)

                full_prompt = f"""
                당신은 똑똑하고 친절한 AI 조수입니다. 
                아래의 웹 검색 결과를 바탕으로 사용자의 질문에 친절하게 답변해주세요.
                
                검색 결과: {search_results}
                사용자 질문: {prompt}
                """

                response = llm.invoke(full_prompt).content
                st.markdown(response)

                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Error: {e}")
