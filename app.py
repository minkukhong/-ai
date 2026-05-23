import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults

st.set_page_config(page_title="용마고 AI", page_icon="🇰🇷")
st.title("용마고 생성형 AI")

# 사이드바에서 API 키 안전하게 입력받기
with st.sidebar:
    st.header("API 키 설정")
    gemini_key = st.text_input("Gemini API Key", type="password")
    tavily_key = st.text_input("Tavily API Key", type="password")
    st.caption("※ API 키가 없으면 AI가 작동하지 않습니다.")

# 대화 기록 저장용 메모리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 화면에 그려주기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자가 질문을 입력했을 때
if prompt := st.chat_input("궁금한 것을 물어보세요"):
    # 1. 사용자 질문 화면에 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI 답변 생성 영역
    with st.chat_message("assistant"):
        if not gemini_key or not tavily_key:
            st.error("왼쪽 사이드바에 Gemini 키와 Tavily 키를 모두 입력해주세요")
        else:
            # 로딩 스피너(애니메이션) 보여주기
            with st.spinner("인터넷 검색 및 답변 작성 중..."):
                try:
                    # 환경 변수에 키 세팅
                    os.environ["GOOGLE_API_KEY"] = gemini_key
                    os.environ["TAVILY_API_KEY"] = tavily_key

                    # 오픈소스 도구들 연결 (검색기 + AI)
                    search = TavilySearchResults(k=3)
                    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

                    # 실시간 웹 검색 실행
                    search_results = search.run(prompt)

                    # AI가 참고할 프롬프트 구성
                    full_prompt = f"""
                    당신은 AI 조수입니다. 
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
