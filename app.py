import streamlit as st
import requests
import json
from PIL import Image

# 1. 웹 브라우저 탭 및 레이아웃 설정
st.set_page_config(page_title="용마고 지능형 AI 안내 시스템", layout="centered")

# 2. 웹 표준 CSS 오버라이딩을 통한 UI 가시성 최적화
# 배경 이미지 위에 85% 투명도의 백색 레이어를 겹쳐 텍스트 가독성을 극대화합니다.
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
                    url("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=1920") no-repeat center center fixed;
        background-size: cover;
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("용마고 지능형 학사 어시스턴트")
st.caption("오픈소스 프레임워크와 초경량 LLM을 결합한 저비용 고효율 안내 플랫폼")

# 3. 가상 서버 런타임 환경 시스템 비밀 저장소에서 API 키 격리 로드
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("보안 경고: st.secrets에서 GEMINI_API_KEY를 찾을 수 없습니다.")
    st.stop()

# 4. 세션 상태 저장소(st.session_state) 초기화 (대화 문맥 보존성 확보)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존에 나눈 대화 기록을 화면에 순차적으로 렌더링
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 질의 입력부 제어
if prompt := st.chat_input("학교 생활이나 시설에 대해 무엇이든 물어보세요."):
    
    # 사용자가 입력한 질문을 화면에 표시하고 세션에 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI 답변 창을 미리 생성
    with st.chat_message("assistant"):
        
        # [우선순위 예외 처리 규칙 필터링 - 이스터 에그 매핑]
        if "가장 예쁜 선생님" in prompt or "젤 예쁜 선생님" in prompt:
            response_text = "용마고에서 가장 예쁜 선생님은 박미란 선생님입니다."
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        else:
            # 일반 질문일 경우 구글 Gemini 백엔드 엔진과 직접 HTTP 통신 수행
            with st.spinner("지능형 학사 데이터베이스를 탐색하는 중..."):
                try:
                    # 외부 중계 라이브러리 충돌을 우회하기 위한 구글 정식 API 게이트웨이 엔드포인트
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
                    
                    # 지식 주입 가이드라인 및 과거 문맥을 포함한 컨텍스트 조립
                    system_instruction = (
                        "당신은 마산용마고등학교의 전용 AI 행정 안내 시스템입니다. "
                        "반드시 예의 바르고 친절한 어조로 답변해야 하며, 정보가 확실하지 않거나 "
                        "제공되지 않은 엉뚱한 분야(주식 정보, 허구 소설 등)에 대해서는 할루시네이션(환각)을 방지하기 위해 "
                        "'정형화된 데이터셋 범위를 벗어난 질문입니다'라고 정중히 안내하십시오."
                    )
                    
                    headers = {'Content-Type': 'application/json'}
                    
                    # RESTful 통신 패킷 데이터 매핑
                    payload = {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": f"{system_instruction}\n\n이전 대화 기록:\n{st.session_state.messages}\n\n최신 질문: {prompt}"}]
                            }
                        ]
                    }
                    
                    # HTTP POST 패킷 다이렉트 송수신
                    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        # 응답 데이터에서 텍스트 추출 및 역직렬화
                        response_text = result['candidates'][0]['content']['parts'][0]['text']
                        
                        st.markdown(response_text)
                        # 생성된 답변을 대화 맥락 유지를 위해 배열에 실시간 누적 저장
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                    else:
                        st.error(f"백엔드 통신 에러 (코드: {response.status_code}) - HTTP 직접 전송 패킷 설정을 확인하세요.")
                        
                except requests.exceptions.Timeout:
                    st.error("네트워크 타임아웃: 구글 AI 백엔드 서버의 응답 시간이 초과되었습니다.")
                except Exception as e:
                    st.error(f"예외 처리 제어 블록 구동: 시스템 내부 오류가 발생했습니다. ({str(e)})")
