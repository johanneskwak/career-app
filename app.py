import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------------------------------------
# [1] 기본 설정 및 데이터 연결
# -----------------------------------------------------------
st.set_page_config(page_title="나의 진로 내비게이션", page_icon="🧭", layout="wide")

# 선생님의 구글 시트 ID
sheet_id = "1ciZxapKzL5-hjDUXzIcOBybhjrfmBy5R8SV-5H5iL6Y"

# 시트별 GID (선생님이 주신 번호 완벽 반영)
sheet_gids = {
    "Questions": "901188331",   # 설문 문항
    "Jobs": "1538922399",       # 직업 정보 (이미지URL 포함)
    "Majors": "1936690584",     # 전공 매칭
    "Subjects": "2140742626",   # 과목 매칭
    "Balance": "457088843"      # [NEW] 밸런스 게임 데이터
}

# 데이터 불러오기 함수 (60초마다 자동 업데이트)
@st.cache_data(ttl=60)
def load_data(sheet_name):
    gid = sheet_gids[sheet_name]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# -----------------------------------------------------------
# [2] 앱 헤더 및 메뉴 구성
# -----------------------------------------------------------
st.title("🧭 나의 진로 내비게이션")
st.markdown("나의 **흥미(적성)**와 **가치관(현실)**을 모두 고려하여 최적의 진로를 찾아보세요!")
st.divider()

# 탭 메뉴 구성
tab1, tab2 = st.tabs(["⚖️ 가치관 밸런스 게임", "📝 흥미 유형 & 로드맵"])

# ===========================================================
# [TAB 1] 가치관 밸런스 게임 (돈 vs 워라벨 vs ...)
# ===========================================================
with tab1:
    st.header("⚖️ 나에게 가장 중요한 직업의 조건은?")
    st.info("총 100점의 점수를 4가지 항목에 나누어 주세요. (합계가 100이 되어야 결과를 볼 수 있어요!)")

    # 화면을 좌우로 나눔
    col_input, col_result = st.columns([1, 1.2])

    with col_input:
        st.subheader("1️⃣ 가치관 점수 배분")
        
        # 슬라이더 입력
        money = st.slider("💰 돈 (연봉, 성과급)", 0, 100, 25)
        wlb = st.slider("🏖️ 워라벨 (칼퇴, 휴가)", 0, 100, 25)
        culture = st.slider("🎨 문화 (수평적, 재미)", 0, 100, 25)
        location = st.slider("📍 근무지 (서울, 핫플)", 0, 100, 25)

        total_score = money + wlb + culture + location
        
        # 점수 검증 로직
        if total_score == 100:
            st.success(f"합계: {total_score}점 (완벽해요! 😎)")
            ready_to_analyze = True
        elif total_score > 100:
            st.error(f"합계: {total_score}점 (100점을 넘었어요! {total_score-100}점을 줄여주세요)")
            ready_to_analyze = False
        else:
            st.warning(f"합계: {total_score}점 ({100-total_score}점이 더 필요해요!)")
            ready_to_analyze = False

    with col_result:
        st.subheader("2️⃣ 분석 결과")
        
        if ready_to_analyze:
            if st.button("내 가치관에 맞는 현실 직업 찾기 🔍", type="primary"):
                df_bal = load_data("Balance")
                
                if not df_bal.empty:
                    # [알고리즘] 유클리드 거리 계산 (내 점수와 가장 가까운 직업 찾기)
                    # 거리 = 루트( (내돈-직업돈)^2 + (내워라벨-직업워라벨)^2 ... )
                    df_bal['차이'] = np.sqrt(
                        (df_bal['돈(Money)'] - money)**2 +
                        (df_bal['워라벨(WLB)'] - wlb)**2 +
                        (df_bal['문화(Culture)'] - culture)**2 +
                        (df_bal['근무지(Location)'] - location)**2
                    )
                    
                    # 차이가 작은 순서대로 정렬하여 상위 3개 추출
                    top3 = df_bal.sort_values(by='차이').head(3)
                    
                    st.write("당신의 가치관과 가장 비슷한 직업군입니다.")
                    
                    for idx, row in top3.iterrows():
                        with st.container():
                            st.markdown(f"### 🥇 {row['직업군']}")
                            st.caption(f"💬 \"{row['한줄평']}\"")
                            st.info(f"🏢 **대표 근무지:** {row['대표 기업/위치 (예시)']}")
                            
                            # 상세 점수 지표
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("돈", row['돈(Money)'])
                            m2.metric("워라벨", row['워라벨(WLB)'])
                            m3.metric("문화", row['문화(Culture)'])
                            m4.metric("근무지", row['근무지(Location)'])
                            st.markdown("---")
                else:
                    st.error("데이터를 불러오지 못했습니다. 구글 시트 [Balance] 탭을 확인해주세요.")
        else:
            st.info("👈 왼쪽에서 점수 합계를 100점으로 맞춰주세요.")

# ===========================================================
# [TAB 2] 흥미 유형 & 로드맵 (기존 기능 통합)
# ===========================================================
with tab2:
    # 세션 상태 관리 (설문 단계 유지)
    if 'survey_step' not in st.session_state:
        st.session_state.survey_step = 1
    if 'user_scores' not in st.session_state:
        st.session_state.user_scores = {'R':0, 'I':0, 'A':0, 'S':0, 'E':0, 'C':0}

    # --- 설문 단계 ---
    if st.session_state.survey_step == 1:
        st.header("📝 홀랜드 흥미 유형 검사")
        st.write("다음 질문에 해당되는 내용을 체크해주세요.")
        
        df_q = load_data("Questions")
        
        if not df_q.empty:
            with st.form("survey_form"):
                scores = {'R':0, 'I':0, 'A':0, 'S':0, 'E':0, 'C':0}
                cols = st.columns(2)
                for i, row in df_q.iterrows():
                    with cols[i % 2]:
                        if st.checkbox(f"{i+1}. {row['질문 내용']}", key=f"q_{i}"):
                            scores[row['유형'][0]] += 1
                
                if st.form_submit_button("결과 확인하기 👉"):
                    st.session_state.user_scores = scores
                    st.session_state.survey_step = 2
                    st.rerun()
        else:
            st.error("질문 데이터를 불러오지 못했습니다.")

    # --- 결과 및 로드맵 단계 ---
    elif st.session_state.survey_step == 2:
        st.header("🎓 나만의 진로 로드맵")
        
        scores = st.session_state.user_scores
        max_type = max(scores, key=scores.get)
        
        st.success(f"분석 결과, 학생은 **[{max_type} 유형]**의 성향이 가장 강합니다!")
        
        if st.button("🔄 다시 검사하기"):
            st.session_state.survey_step = 1
            st.rerun()
            
        st.markdown("---")
        
        # 직업 -> 전공 -> 과목 순차 선택
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("1️⃣ 직업 선택")
            df_jobs = load_data("Jobs")
            # 내 유형에 맞는 직업 필터링
            my_jobs = df_jobs[df_jobs['유형'].str.startswith(max_type)]
            
            job_list = my_jobs['직업명'].unique()
            selected_job = st.radio("관심 있는 직업을 선택하세요:", job_list)
            
            if selected_job:
                job_row = my_jobs[my_jobs['직업명'] == selected_job].iloc[0]
                st.info(f"{job_row['설명']}")
                
                # 이미지 출력 (URL이 있을 경우만)
                if '이미지URL' in job_row and pd.notna(job_row['이미지URL']):
                    st.image(job_row['이미지URL'], caption=f"{selected_job} 관련 이미지", use_container_width=True)

        with col_right:
            st.subheader("2️⃣ 전공 및 과목 추천")
            
            if selected_job:
                df_majors = load_data("Majors")
                major_row = df_majors[df_majors['직업명'] == selected_job]
                
                if not major_row.empty:
                    # 전공 리스트업
                    m1 = major_row.iloc[0]['추천 학과 1']
                    m2 = major_row.iloc[0]['추천 학과 2']
                    m3 = major_row.iloc[0]['추천 학과 3'] if '추천 학과 3' in major_row.columns else None
                    
                    options = [m for m in [m1, m2, m3] if pd.notna(m)]
                    selected_major = st.selectbox("진학 희망 학과를 선택하세요:", options)
                    
                    st.divider()
                    
                    # 과목 추천 로직 (키워드 매칭 강화)
                    st.markdown(f"**📚 '{selected_major}' 진학을 위한 고교 과목**")
                    df_subjects = load_data("Subjects")
                    
                    # 컬럼 이름 유연하게 찾기
                    target_col = '학과(전공)'
                    if target_col not in df_subjects.columns:
                        # 혹시 이름이 다를 경우 첫번째 컬럼을 사용
                        target_col = df_subjects.columns[0]

                    # '학과(전공)' 열에 선택한 전공 글자가 포함된 행 찾기
                    subject_row = df_subjects[df_subjects[target_col].astype(str).str.contains(selected_major)]
                    
                    if not subject_row.empty:
                        subj_data = subject_row.iloc[0]
                        st.success("✅ 추천 과목 데이터를 찾았습니다.")
                        st.write("📘 **일반 선택:**", subj_data['일반 선택 과목'])
                        st.write("📙 **진로 선택:**", subj_data['진로 선택 과목 (심화)'])
                    else:
                        st.warning(f"'{selected_major}'에 대한 과목 데이터가 시트에 없습니다.")
                        st.caption(f"팁: 구글 시트 [Subjects] 탭의 A열에 '{selected_major}' 단어를 포함시켜주세요.")
                else:
                    st.warning("이 직업에 연결된 전공 데이터가 없습니다.")
            else:
                st.info("👈 왼쪽에서 직업을 먼저 선택해주세요.")
