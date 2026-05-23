import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults

st.set_page_config(page_title="용마고 AI", page_icon="🇰🇷")
st.title("🚀 용마고 생산형 AI")

# [보안 및 자동화 조치] 금고(st.secrets)에서 키를 직접 안전하게 꺼내옵니다.
try:
    gemini_key = st.secrets["GOOGLE_API_KEY"]
    tavily_key = st.secrets["TAVILY_API_KEY"]
    
    # 꺼내온 키를 시스템 환경 변수에 강제로 주입합니다.
    os.environ["GOOGLE_API_KEY"] = gemini_key
    os.environ["TAVILY_API_KEY"] = tavily_key
except Exception as e:
    st.error("⚠️ 스트림릿 Secrets 금고에 API 키가 없거나 이름이 틀렸습니다! 설정을 확인해주세요.")
    st.stop() # 키가 없으면 아래 코드를 실행하지 않고 멈춥니다.

# 대화 기록 저장용 메모리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 화면에 그려주기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자가 질문을 입력했을 때
if prompt := st.chat_input("궁금한 것을 물어보세요!"):
    # 1. 사용자 질문 화면에 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI 답변 생성 영역
    with st.chat_message("assistant"):
        with st.spinner("인터넷 검색 및 답변 작성 중..."):
            try:
                # 오픈소스 도구들 연결 (검색기 + AI)
                search = TavilySearchResults(k=3)
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

                # 실시간 웹 검색 실행
                search_results = search.run(prompt)

                # AI가 참고할 프롬프트 구성
                full_prompt = f"""
                당신은 똑똑하고 친절한 AI 조수입니다. 
                아래의 웹 검색 결과를 바탕으로 사용자의 질문에 친절하게 답변해주세요.
                
                검색 결과: {search_results}
                사용자 질문: {prompt}
                """

                # 답변 생성 및 출력
                response = llm.invoke(full_prompt).content
                st.markdown(response)

                # 대화 기록에 AI 답변 저장
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
