import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------------------------------------
# [1] 기본 설정 및 데이터 연결
# -----------------------------------------------------------
st.set_page_config(page_title="나의 진로 내비게이션", page_icon="🧭", layout="wide")

# 선생님의 구글 시트 ID
sheet_id = "1ciZxapKzL5-hjDUXzIcOBybhjrfmBy5R8SV-5H5iL6Y"

# 시트별 GID
sheet_gids = {
    "Questions": "901188331",
    "Jobs": "1538922399",
    "Majors": "1936690584",
    "Subjects": "2140742626",
    "Balance": "457088843"
}

# 데이터 불러오기 함수
@st.cache_data(ttl=60)
def load_data(sheet_name):
    gid = sheet_gids[sheet_name]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# -----------------------------------------------------------
# [공통 함수] 로드맵(전공/과목) 보여주기 기능
# -----------------------------------------------------------
def display_roadmap(job_name):
    """직업 이름을 받아서 전공과 과목 정보를 화면에 그려주는 함수"""
    st.markdown(f"#### 📘 '{job_name}' 진로 로드맵")
    
    # 1. 전공 찾기
    df_majors = load_data("Majors")
    # 직업명이 정확하지 않을 수 있으므로 '포함(contains)'된 것을 찾음
    major_row = df_majors[df_majors['직업명'].astype(str).str.contains(job_name)]
    
    if not major_row.empty:
        # 추천 학과 리스트업
        row = major_row.iloc[0]
        m1 = row['추천 학과 1']
        m2 = row['추천 학과 2']
        m3 = row['추천 학과 3'] if '추천 학과 3' in row else None
        
        majors = [m for m in [m1, m2, m3] if pd.notna(m)]
        
        # 학과 선택 박스 (Key를 유니크하게 만들기 위해 직업명 추가)
        selected_major = st.selectbox(f"진학 희망 학과를 선택하세요 ({job_name}):", majors, key=f"sel_{job_name}")
        
        st.markdown("---")
        
        # 2. 과목 찾기
        st.write(f"**📚 '{selected_major}' 진학을 위한 고교 과목**")
        df_subjects = load_data("Subjects")
        
        # 컬럼 이름 찾기 (혹시 오타가 있을까봐)
        target_col = '학과(전공)' if '학과(전공)' in df_subjects.columns else df_subjects.columns[0]
        
        # 해당 전공이 포함된 행 찾기
        subject_row = df_subjects[df_subjects[target_col].astype(str).str.contains(selected_major)]
        
        if not subject_row.empty:
            subj_data = subject_row.iloc[0]
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**📘 일반 선택 과목**\n\n{subj_data['일반 선택 과목']}")
            with c2:
                st.success(f"**📙 진로 선택 과목 (심화)**\n\n{subj_data['진로 선택 과목 (심화)']}")
        else:
            st.warning(f"'{selected_major}'에 대한 과목 데이터가 시트에 없습니다. (Subjects 탭 확인 필요)")
    else:
        st.warning(f"'{job_name}'에 대한 전공 데이터가 [Majors] 탭에 없습니다.")
        st.caption("팁: Balance 탭의 직업 이름이 Majors 탭의 직업명과 비슷한지 확인해주세요.")


# -----------------------------------------------------------
# [3] 메인 화면 및 메뉴
# -----------------------------------------------------------
st.title("🧭 나의 진로 내비게이션")
st.markdown("나의 가치관(밸런스게임)과 적성(흥미검사)을 통해 꿈을 찾아보세요!")

tab1, tab2 = st.tabs(["⚖️ 가치관 밸런스 게임", "📝 흥미 유형 검사"])

# ===========================================================
# [TAB 1] 밸런스 게임
# ===========================================================
with tab1:
    st.header("⚖️ 직업 가치관 밸런스 게임")
    st.info("4가지 가치에 총 100점을 배분해주세요.")

    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.subheader("1️⃣ 점수 배분")
        money = st.slider("💰 돈 (연봉)", 0, 100, 25)
        wlb = st.slider("🏖️ 워라벨 (여가)", 0, 100, 25)
        culture = st.slider("🎨 문화 (재미)", 0, 100, 25)
        location = st.slider("📍 근무지 (위치)", 0, 100, 25)
        
        total = money + wlb + culture + location
        
        if total == 100:
            st.success("합계 100점! 완벽합니다. 😎")
            ready = True
        else:
            st.warning(f"현재 합계: {total}점 (100점을 맞춰주세요)")
            ready = False

    with c2:
        st.subheader("2️⃣ 추천 결과")
        if ready:
            if st.button("결과 보기 🔍", type="primary"):
                df_bal = load_data("Balance")
                if not df_bal.empty:
                    # 유클리드 거리 계산
                    df_bal['차이'] = np.sqrt(
                        (df_bal['돈(Money)'] - money)**2 +
                        (df_bal['워라벨(WLB)'] - wlb)**2 +
                        (df_bal['문화(Culture)'] - culture)**2 +
                        (df_bal['근무지(Location)'] - location)**2
                    )
                    # 상위 3개 추천
                    top3 = df_bal.sort_values(by='차이').head(3)
                    
                    st.write("당신의 가치관과 가장 딱 맞는 직업입니다!")
                    
                    for idx, row in top3.iterrows():
                        with st.expander(f"🥇 {row['직업군']} (자세히 보기)", expanded=True):
                            st.caption(f"💬 \"{row['한줄평']}\"")
                            st.write(f"🏢 **대표 위치:** {row['대표 기업/위치 (예시)']}")
                            
                            # 그래프
                            st.progress(row['돈(Money)']/100, text=f"돈 {row['돈(Money)']}")
                            st.progress(row['워라벨(WLB)']/100, text=f"워라벨 {row['워라벨(WLB)']}")
                            
                            st.markdown("---")
                            
                            # ★ 핵심 기능: 여기서 바로 로드맵 보여주기 ★
                            # 버튼을 누르면 아래에 로드맵이 펼쳐짐
                            if st.checkbox(f"👉 '{row['직업군']}' 과목 추천 보러가기", key=f"link_{idx}"):
                                display_roadmap(row['직업군'])
                else:
                    st.error("데이터 로드 실패")

# ===========================================================
# [TAB 2] 흥미 유형 검사
# ===========================================================
with tab2:
    if 'survey_step' not in st.session_state:
        st.session_state.survey_step = 1
    if 'user_scores' not in st.session_state:
        st.session_state.user_scores = {'R':0,'I':0,'A':0,'S':0,'E':0,'C':0}

    if st.session_state.survey_step == 1:
        st.header("📝 흥미 유형 찾기")
        df_q = load_data("Questions")
        if not df_q.empty:
            with st.form("survey"):
                scores = {'R':0,'I':0,'A':0,'S':0,'E':0,'C':0}
                cols = st.columns(2)
                for i, r in df_q.iterrows():
                    with cols[i%2]:
                        if st.checkbox(f"{r['질문 내용']}", key=f"q_{i}"):
                            scores[r['유형'][0]] += 1
                if st.form_submit_button("결과 확인"):
                    st.session_state.user_scores = scores
                    st.session_state.survey_step = 2
                    st.rerun()

    elif st.session_state.survey_step == 2:
        st.header("🎓 진로 로드맵")
        scores = st.session_state.user_scores
        max_type = max(scores, key=scores.get)
        st.success(f"당신의 유형은 **[{max_type}형]** 입니다!")
        
        if st.button("다시 검사하기"):
            st.session_state.survey_step = 1
            st.rerun()
            
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("직업 선택")
            df_jobs = load_data("Jobs")
            my_jobs = df_jobs[df_jobs['유형'].str.startswith(max_type)]
            selected_job = st.radio("직업 목록", my_jobs['직업명'].unique())
            
            if selected_job:
                row = my_jobs[my_jobs['직업명']==selected_job].iloc[0]
                st.info(row['설명'])
                if '이미지URL' in row and pd.notna(row['이미지URL']):
                    st.image(row['이미지URL'])

        with c_right:
            st.subheader("상세 로드맵")
            if selected_job:
                # ★ 공통 함수 재사용
                display_roadmap(selected_job)
