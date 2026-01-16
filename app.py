import streamlit as st
import google.generativeai as genai
import datetime
from dateutil.relativedelta import relativedelta

# --------------------------------------------------------------------------
# 1. 기본 설정 및 Gemini 모델 초기화
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="초등 학생자치회 알리미",
    page_icon="🏫",
    layout="wide"
)

# 보안 설정: st.secrets에서 API Key 로드 (Streamlit Cloud 배포용)
try:
    GENAI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_API_KEY)
except FileNotFoundError:
    # 로컬 실행 시 secrets.toml이 없으면 안내 메시지
    st.error("보안 키 설정이 필요합니다. .streamlit/secrets.toml 파일이나 Streamlit Cloud의 Secrets에 GEMINI_API_KEY를 입력해주세요.")
    st.stop()
except KeyError:
    st.error("보안 키 설정 오류: secrets에 'GEMINI_API_KEY'가 올바르게 설정되었는지 확인해주세요.")
    st.stop()

# 모델 설정 (엄격한 버전 준수: gemini-2.5-flash)
MODEL_NAME = "gemini-2.5-flash"

def get_gemini_response(prompt):
    """Gemini 2.5 Flash 모델을 사용하여 응답을 생성하는 함수"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 연결 중 오류가 발생했습니다: {str(e)}"

# --------------------------------------------------------------------------
# 2. 세션 상태 초기화 (데이터 임시 저장용)
# --------------------------------------------------------------------------
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "wishlist" not in st.session_state:
    st.session_state.wishlist = []

# --------------------------------------------------------------------------
# 3. 사이드바 메뉴 구성
# --------------------------------------------------------------------------
st.sidebar.title("🏫 학생자치회 메뉴")
menu = st.sidebar.radio(
    "이동할 메뉴를 선택하세요",
    ["📅 이번 달 행사 안내", "🌱 다음 달 행사 희망", "📮 건의사항", "📢 공지사항", "📊 설문조사"]
)

# 날짜 계산
now = datetime.datetime.now()
current_month_str = now.strftime("%Y년 %m월")
next_month_date = now + relativedelta(months=1)
next_month_str = next_month_date.strftime("%Y년 %m월")

# --------------------------------------------------------------------------
# 4. 메뉴별 기능 구현
# --------------------------------------------------------------------------

# [섹션 1] 이번 달 행사 안내
if menu == "📅 이번 달 행사 안내":
    st.title(f"🎉 {current_month_str}의 우리 학교 행사")
    st.markdown("---")
    
    # 예시 데이터
    events = [
        {"date": "10월 9일", "name": "한글사랑 캠페인", "desc": "우리말 겨루기 대회 및 예쁜 말 쓰기 서약"},
        {"date": "10월 25일", "name": "독도의 날 행사", "desc": "독도 관련 퀴즈 풀기 및 플래시몹"}
    ]

    for event in events:
        with st.expander(f"📌 [{event['date']}] {event['name']}", expanded=True):
            st.write(f"**행사 내용:** {event['desc']}")
            st.info("💡 안내 사항: 많은 참여 부탁드립니다!")

# [섹션 2] 다음 달 행사 희망 (Gemini AI 활용)
elif menu == "🌱 다음 달 행사 희망":
    st.title(f"🚀 {next_month_str} 행사 아이디어 공모")
    st.markdown("다음 달 행사를 우리가 직접 만들어봐요!")
    
    st.subheader("🤖 AI가 알려주는 다음 달 기념일")
    
    if st.button("✨ 기념일 검색하기 (AI)"):
        with st.spinner(f"{next_month_str}의 기념일을 찾는 중..."):
            prompt = f"""
            {next_month_str}에 대한민국 초등학생들이 알면 좋은 교육적인 기념일이나 국경일을 
            3개 정도 뽑아서 날짜와 의미를 간단히 목록으로 보여줘.
            """
            holidays = get_gemini_response(prompt)
            st.success("참고해보세요!")
            st.markdown(holidays)

    st.markdown("---")
    st.subheader("📝 내가 만들고 싶은 행사")
    
    with st.form("wishlist_form"):
        w_name = st.text_input("희망 행사 이름")
        w_content = st.text_area("어떤 활동을 하고 싶나요?")
        submitted = st.form_submit_button("아이디어 제출하기")
        
        if submitted and w_name:
            st.session_state.wishlist.append({"name": w_name, "content": w_content})
            st.toast("멋진 아이디어가 접수되었습니다!", icon="✅")

    if st.session_state.wishlist:
        st.write("### 👇 친구들의 아이디어")
        for item in st.session_state.wishlist:
            st.info(f"**{item['name']}**: {item['content']}")

# [섹션 3] 건의사항
elif menu == "📮 건의사항":
    st.title("📮 학생자치회 소리함")
    st.info("비방이나 나쁜 말은 사용하지 말아주세요.")
    
    with st.form("suggestion_form"):
        s_category = st.selectbox("분류", ["시설", "급식", "친구", "기타"])
        s_text = st.text_area("건의 내용")
        s_submit = st.form_submit_button("보내기")
        
        if s_submit and s_text:
            st.session_state.suggestions.append({"cat": s_category, "text": s_text})
            st.success("학생자치회에 전달되었습니다.")

# [섹션 4] 공지사항
elif menu == "📢 공지사항":
    st.title("📢 알립니다")
    st.warning("⚠️ 복도에서 뛰지 맙시다! 안전이 제일 중요해요.")
    st.markdown("""
    ### 🏫 이번 주 목표
    * **고운 말 쓰기**
    * **급식 남기지 않기**
    """)

# [섹션 5] 설문조사
elif menu == "📊 설문조사":
    st.title("📊 이달의 설문")
    st.markdown("### 점심시간 신청곡 장르 투표")
    
    genre = st.radio("하나만 골라주세요", ["K-POP", "클래식", "OST", "팝송"])
    
    if st.button("투표하기"):
        st.balloons()
        st.success(f"'{genre}'에 소중한 한 표를 던졌습니다!")
