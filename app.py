import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="나의 진로 로드맵", page_icon="🌱")

# 구글 시트 데이터 연결 정보
sheet_id = "1ciZxapKzL5-hjDUXzIcOBybhjrfmBy5R8SV-5H5iL6Y"
sheet_gids = {
    "Questions": "901188331",
    "Jobs": "1538922399",
    "Majors": "1936690584",
    "Subjects": "2140742626"
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

# 앱의 현재 단계 관리
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'scores' not in st.session_state:
    st.session_state.scores = {'R':0, 'I':0, 'A':0, 'S':0, 'E':0, 'C':0}

st.title("🌱 나만의 진로 찾기")
st.write("간단한 설문을 통해 나에게 맞는 진로와 전공, 과목을 추천받으세요!")
st.markdown("---")

# === 1단계: 설문 ===
if st.session_state.step == 1:
    st.header("1. 흥미 유형 검사")
    df = load_data("Questions")
    
    if not df.empty:
        # 설문지 폼 시작
        with st.form("my_form"):
            scores = {'R':0, 'I':0, 'A':0, 'S':0, 'E':0, 'C':0}
            for i, row in df.iterrows():
                # 질문 출력
                if st.checkbox(f"{i+1}. {row['질문 내용']}"):
                    scores[row['유형'][0]] += 1
            
            # 제출 버튼
            submitted = st.form_submit_button("결과 확인하기")
            if submitted:
                st.session_state.scores = scores
                st.session_state.step = 2
                st.rerun()
    else:
        st.error("데이터를 불러올 수 없습니다. 구글 시트 공유 설정을 확인해주세요.")

# === 2단계: 결과 ===
elif st.session_state.step == 2:
    scores = st.session_state.scores
    # 최고 점수 유형 찾기
    my_type = max(scores, key=scores.get)
    
    st.success(f"학생은 **[{my_type} 유형]**의 성향이 가장 강합니다!")
    
    if st.button("다시 검사하기"):
        st.session_state.step = 1
        st.rerun()

    st.markdown("---")
    
    # 탭으로 나누어 보여주기
    tab1, tab2 = st.tabs(["추천 직업", "전공 및 과목"])
    
    with tab1:
        st.subheader(f"[{my_type} 유형] 추천 직업")
        df_jobs = load_data("Jobs")
        my_jobs = df_jobs[df_jobs['유형'].str.startswith(my_type)]
        
        # 라디오 버튼으로 직업 선택
        job_list = my_jobs['직업명'].unique()
        choice = st.radio("직업을 선택해보세요:", job_list)
        
        if choice:
            desc = my_jobs[my_jobs['직업명']==choice].iloc[0]['설명']
            st.info(f"{desc}")
            st.session_state.choice = choice # 선택한 직업 저장

    with tab2:
        if 'choice' in st.session_state:
            job = st.session_state.choice
            st.subheader(f"[{job}] 관련 로드맵")
            
            df_majors = load_data("Majors")
            row = df_majors[df_majors['직업명'] == job]
            
            if not row.empty:
                # 전공 선택
                m1 = row.iloc[0]['추천 학과 1']
                m2 = row.iloc[0]['추천 학과 2']
                major = st.selectbox("학과를 선택하세요:", [m1, m2])
                
                # 과목 추천
                df_subjects = load_data("Subjects")
                s_row = df_subjects[df_subjects['학과(전공)'].str.contains(major)]
                
                if not s_row.empty:
                    st.write("📘 **일반 선택:**", s_row.iloc[0]['일반 선택 과목'])
                    st.write("📙 **진로 선택:**", s_row.iloc[0]['진로 선택 과목 (심화)'])
        else:
            st.warning("왼쪽 [추천 직업] 탭에서 직업을 먼저 선택해주세요.")
