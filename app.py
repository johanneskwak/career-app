import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# -----------------------------------------------------------------------------
# 1. 페이지 설정 & 스타일
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Career Compass Pro",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# UI/UX 스타일링 (카드 디자인, 태그 등)
st.markdown("""
<style>
    /* 메인 컨테이너 스타일 */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    /* 정보 박스 스타일 */
    .info-box {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%;
    }
    .info-title {
        font-weight: 700;
        color: #1E40AF;
        margin-bottom: 10px;
        display: block;
    }
    /* 과목 태그 스타일 */
    .tag-base {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 3px;
    }
    .tag-gen {
        background-color: #DBEAFE;
        color: #1E40AF;
        border: 1px solid #BFDBFE;
    }
    .tag-career {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
    }
    /* 단계 표시 스타일 */
    .step-indicator {
        padding: 10px 20px;
        background-color: #EFF6FF;
        border-radius: 30px;
        color: #1D4ED8;
        font-weight: bold;
        margin-bottom: 20px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 데이터 센터 (직업 스탯 + 상세 가이드)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # 1. 직업 정량 데이터 (홀란드 코드 + 5대 가치관 점수)
    # 실제로는 100개 이상의 직업이 들어갈 수 있습니다.
    df = pd.DataFrame({
        '직업군': [
            '소프트웨어 개발자', '데이터 사이언티스트', '정보보안 전문가', 'AI 연구원', '반도체 엔지니어',
            '의사 (전문의)', '약사', '간호사', '수의사', '치과의사', '물리치료사',
            '경영 컨설턴트', '공인회계사(CPA)', '투자은행가(IB)', '마케팅 전문가', '관세사', '감정평가사',
            '변호사 (로스쿨)', '판사/검사', '변리사', '노무사', '경찰공무원',
            '5급 행정고시', '7/9급 공무원', '외교관', '중등 교사', '대학교수', '국책연구원',
            '건축가', '도시계획가', '항공기 조종사', '승무원',
            '방송 PD', '기자', '웹툰 작가', '큐레이터', '게임 기획자', 'UX/UI 디자이너'
        ],
        'Holland_Code': [
            'IR', 'IC', 'IC', 'IR', 'RI',
            'IS', 'SC', 'SI', 'IR', 'IR', 'SR',
            'EC', 'CE', 'EC', 'AE', 'CE', 'CE',
            'EI', 'EI', 'IE', 'ES', 'SE',
            'ES', 'CS', 'SA', 'SA', 'IA', 'IR',
            'AR', 'IE', 'RI', 'SE',
            'AE', 'EI', 'AI', 'AE', 'AI', 'AE'
        ],
        'Money': [45, 50, 45, 50, 50, 60, 45, 35, 45, 55, 35, 55, 50, 60, 35, 40, 50, 55, 50, 55, 40, 30, 35, 25, 40, 30, 40, 35, 40, 35, 55, 30, 35, 30, 40, 25, 35, 35],
        'WLB':   [25, 25, 20, 20, 15, 10, 35, 15, 25, 25, 30, 5, 10, 5, 25, 30, 25, 5, 10, 15, 30, 15, 15, 35, 15, 35, 35, 35, 15, 25, 20, 20, 5, 5, 20, 30, 20, 25],
        'Culture':[35, 30, 25, 25, 15, 10, 15, 10, 15, 15, 20, 10, 15, 5, 40, 15, 15, 10, 5, 15, 20, 5, 10, 10, 15, 15, 20, 20, 25, 20, 10, 20, 30, 20, 40, 25, 40, 40],
        'Location':[15, 15, 15, 10, 10, 20, 20, 25, 20, 20, 20, 25, 25, 25, 20, 20, 15, 25, 10, 20, 20, 10, 30, 15, 10, 15, 10, 10, 20, 15, 10, 30, 25, 20, 10, 20, 15, 15],
        'Stability':[20, 25, 30, 25, 30, 60, 50, 40, 50, 55, 45, 15, 40, 10, 15, 40, 40, 30, 50, 45, 35, 50, 55, 60, 50, 55, 50, 50, 20, 30, 40, 20, 20, 25, 10, 20, 15, 20]
    })
    
    # 2. 상세 진로 가이드 (30개 이상 확장)
    # [Tip] 코드 길이상 주요 직업군은 상세히, 나머지는 패턴화하여 작성
    guide = {
        # --- IT/공학 ---
        "소프트웨어 개발자": {"major": "컴퓨터공학, 소프트웨어학", "hs_g": "수학I/II, 미적분, 물리학I, 정보", "hs_c": "인공지능 수학, 정보과학", "steps": ["CS 기초(자료구조/알고리즘)", "나만의 웹/앱 프로젝트 배포", "코딩테스트 및 기술면접"]},
        "데이터 사이언티스트": {"major": "통계학, 산업공학, 데이터사이언스", "hs_g": "확률과 통계, 미적분, 사회문제탐구", "hs_c": "실용 통계, 수학과제 탐구", "steps": ["Python/SQL 및 통계학 마스터", "Kaggle 등 분석 대회 참여", "석사 진학 또는 실무 프로젝트"]},
        "반도체 엔지니어": {"major": "전자공학, 신소재공학", "hs_g": "물리학I/II, 화학I, 미적분", "hs_c": "공학 일반, 고급 물리학", "steps": ["회로이론/반도체공학 학점 관리", "반도체 공정 실습 경험", "대기업 직무적성검사(GSAT 등)"]},
        "정보보안 전문가": {"major": "정보보호학, 컴퓨터공학", "hs_g": "정보, 수학I/II, 확률과 통계", "hs_c": "정보과학, 암호학 기초(독학)", "steps": ["네트워크/운영체제 심화 학습", "해킹 방어 대회(CTF) 참여", "정보보안기사 자격증"]},
        "AI 연구원": {"major": "컴퓨터공학, 인공지능학, 수학", "hs_g": "미적분, 기하, 확률과 통계", "hs_c": "인공지능 수학, 심화 수학", "steps": ["대학원(석/박사) 진학 필수", "최신 논문 구현 및 게재", "PyTorch/TensorFlow 숙련"]},
        
        # --- 의료/보건 ---
        "의사 (전문의)": {"major": "의예과", "hs_g": "생명과학I, 화학I, 미적분", "hs_c": "생명과학II, 화학II", "steps": ["의대 6년(예과+본과)", "의사 국가고시 합격", "인턴 1년 + 레지던트 3~4년"]},
        "약사": {"major": "약학과", "hs_g": "화학I, 생명과학I, 미적분", "hs_c": "화학II, 융합과학 탐구", "steps": ["약대 6년 과정 입학", "약학 필수 실무 실습", "약사 면허 시험 합격"]},
        "간호사": {"major": "간호학과", "hs_g": "생명과학I, 생활과 윤리", "hs_c": "보건 간호, 인체 구조와 기능", "steps": ["간호학과 4년 졸업", "간호사 국가고시 합격", "대학병원/종합병원 취업"]},
        "수의사": {"major": "수의예과", "hs_g": "생명과학I, 화학I", "hs_c": "생명과학II, 고급 생명과학", "steps": ["수의대 6년 졸업", "수의사 국가고시 합격", "임상(동물병원) 또는 비임상 진로"]},
        "치과의사": {"major": "치의예과", "hs_g": "생명과학I, 화학I, 미적분", "hs_c": "화학II, 과학과제 연구", "steps": ["치대/치전원 졸업", "치과의사 면허 취득", "전문의 과정(선택) 또는 개원"]},
        "물리치료사": {"major": "물리치료학과", "hs_g": "생명과학I, 체육", "hs_c": "스포츠 생활, 재활 기초", "steps": ["관련 학과 졸업", "국가고시 합격", "병원 재활센터 취업"]},

        # --- 경영/법조 ---
        "경영 컨설턴트": {"major": "경영학, 경제학, 산업공학", "hs_g": "경제, 사회문화, 영어회화", "hs_c": "국제 경제, 사회문제 탐구", "steps": ["전략 학회 활동 및 공모전", "RA(Research Assistant) 인턴", "Case Interview 준비"]},
        "공인회계사(CPA)": {"major": "경영학, 회계학, 세무학", "hs_g": "경제, 확률과 통계", "hs_c": "경제 수학, 실용 경제", "steps": ["학점 이수 및 토익 점수 확보", "1차 시험(객관식)", "2차 시험(서술형)"]},
        "변호사 (로스쿨)": {"major": "자유전공, 정치외교, 경제", "hs_g": "정치와 법, 생활과 윤리, 화작", "hs_c": "사회문제 탐구, 고전 읽기", "steps": ["학점(GPA) 및 토익 고득점", "LEET(법학적성시험) 준비", "로스쿨 3년 + 변호사 시험"]},
        "판사/검사": {"major": "로스쿨 진학 필수", "hs_g": "정치와 법, 윤리와 사상", "hs_c": "사회 탐구 방법", "steps": ["로스쿨 최상위권 성적 유지", "검찰 실무/재판 연구원 선발", "본시험 합격"]},
        "변리사": {"major": "전기전자, 기계, 화학공학", "hs_g": "물리학I, 화학I, 미적분", "hs_c": "지식재산 일반, 공학 일반", "steps": ["이공계 전공 지식 확보", "토익 점수 취득", "변리사 1차/2차 시험 합격"]},
        "노무사": {"major": "법학, 경영학, 사회학", "hs_g": "정치와 법, 사회문화", "hs_c": "사회문제 탐구", "steps": ["노동법 지식 습득", "영어 성적 확보", "공인노무사 자격 시험"]},
        "관세사": {"major": "무역학, 국제통상학", "hs_g": "경제, 영어", "hs_c": "국제 경제, 비즈니스 영어", "steps": ["무역 영어/회계학 공부", "1차 시험 합격", "2차 논술 시험 합격"]},

        # --- 공공/교육 ---
        "5급 행정고시": {"major": "행정학, 경제학, 정치외교", "hs_g": "정치와 법, 한국사, 경제", "hs_c": "국제 정치, 지역 이해", "steps": ["PSAT(1차) 및 한국사/영어", "2차 전공 논술(경제/행정법)", "3차 심층 면접"]},
        "7/9급 공무원": {"major": "행정학, 전공 무관", "hs_g": "국어, 영어, 한국사", "hs_c": "사회문제 탐구", "steps": ["필기 시험 과목 집중", "가산점 자격증(컴활 등) 취득", "면접 준비"]},
        "경찰공무원": {"major": "경찰행정학과", "hs_g": "정치와 법, 체육", "hs_c": "형사법 기초(대체가능)", "steps": ["필기(형사법/경찰학/헌법)", "체력 검정(상시 관리)", "면접 및 신원 조회"]},
        "외교관": {"major": "정치외교학, 국제학", "hs_g": "영어, 제2외국어, 세계사", "hs_c": "국제 정치, 국제 관계", "steps": ["외교관 후보자 선발시험(PSAT)", "전공 평가 및 통합 논술", "외교원 연수"]},
        "중등 교사": {"major": "사범대학(해당 전공)", "hs_g": "교육학(선택), 전공 관련 과목", "hs_c": "교육학, 심리학", "steps": ["교원 자격증 취득", "임용고시 1차(교육학/전공)", "임용고시 2차(수업실연/면접)"]},
        "대학교수": {"major": "관련 전공 박사", "hs_g": "전공 심화 과목", "hs_c": "과제 연구", "steps": ["박사 학위 취득", "우수한 연구 실적(논문)", "대학 임용 지원"]},

        # --- 예술/기타 ---
        "방송 PD": {"major": "신문방송학, 미디어커뮤니케이션", "hs_g": "언어와 매체, 사회문화", "hs_c": "매체와 비평, 영상 제작", "steps": ["영상 제작 경험(동아리/유튜브)", "작문/논술(언론고시) 준비", "실무 면접 및 기획안 평가"]},
        "기자": {"major": "언론홍보학, 사회학, 정치학", "hs_g": "화법과 작문, 정치와 법", "hs_c": "사회 탐구 방법", "steps": ["글쓰기/논술 능력 배양", "시사 상식 및 토익", "언론사 공채 필기/면접"]},
        "웹툰 작가": {"major": "만화애니메이션과", "hs_g": "미술, 문학", "hs_c": "드로잉, 스토리텔링", "steps": ["디지털 드로잉 숙련", "포트폴리오 제작 및 공모전", "플랫폼 연재 계약"]},
        "항공기 조종사": {"major": "항공운항학과", "hs_g": "물리학I, 지구과학I, 영어", "hs_c": "고급 지구과학", "steps": ["비행 교육원 입교 및 면장 취득", "비행 시간(타임빌딩) 축적", "항공사 입사"]},
        "승무원": {"major": "항공서비스학과, 어문계열", "hs_g": "영어회화, 제2외국어", "hs_c": "여행 지리, 매너와 에티켓", "steps": ["어학 성적(토익/스피킹) 확보", "서비스 마인드 및 체력 관리", "항공사 면접(이미지/방송)"]},
        "건축가": {"major": "건축학과(5년제)", "hs_g": "물리학I, 미적분, 미술", "hs_c": "공학 일반, 미술 창작", "steps": ["건축학 인증 프로그램 졸업", "실무 수련(3년)", "건축사 자격 시험"]},
    }
    
    return df, guide

df, career_guide = load_data()

# -----------------------------------------------------------------------------
# 3. 사이드바 (상태 관리)
# -----------------------------------------------------------------------------
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: 홀란드, 2: 밸런스, 3: 결과

with st.sidebar:
    st.header("🧭 진행 상황")
    
    if st.session_state.step == 1:
        st.markdown("<div class='step-indicator'>STEP 1. 적성 검사</div>", unsafe_allow_html=True)
        st.info("나의 흥미 유형(홀란드 코드)을 알아보는 단계입니다.")
    elif st.session_state.step == 2:
        st.markdown("<div class='step-indicator'>STEP 2. 가치관 설정</div>", unsafe_allow_html=True)
        st.info("직업 선택 시 무엇을 중요하게 생각하시나요?")
    else:
        st.markdown("<div class='step-indicator'>STEP 3. 결과 확인</div>", unsafe_allow_html=True)
        st.success("분석 완료! 추천 직업과 상세 로드맵을 확인하세요.")
        if st.button("🔄 처음부터 다시 하기"):
            st.session_state.step = 1
            st.rerun()

    st.divider()
    st.caption("Created by Plant the Seed 🌱")

# -----------------------------------------------------------------------------
# 4. 메인 콘텐츠 (단계별 흐름 제어)
# -----------------------------------------------------------------------------

# =============================================================================
# [STEP 1] 홀란드 적성 검사
# =============================================================================
if st.session_state.step == 1:
    st.markdown("<h1 class='main-header'>🕵️‍♀️ STEP 1. 나의 흥미 유형 찾기</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>각 활동에 대해 얼마나 흥미가 있는지 선택해주세요. (1점: 싫음 ~ 5점: 매우 좋음)</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🔧 사물/도구")
        r = st.slider("기계를 만지거나 도구로 무언가 만드는 것이 좋은가요?", 1, 5, 3)
        st.markdown("#### 🔬 탐구/분석")
        i = st.slider("수학 문제를 풀거나 과학적 원리를 탐구하는 게 재미있나요?", 1, 5, 3)
        st.markdown("#### 🎨 예술/창작")
        a = st.slider("상상력이 풍부하고 무언가 표현하는 것을 좋아하나요?", 1, 5, 3)
    with c2:
        st.markdown("#### 🤝 봉사/교육")
        s = st.slider("친구의 고민을 들어주거나 가르쳐주는 게 보람찬가요?", 1, 5, 3)
        st.markdown("#### 🎤 리더십/설득")
        e = st.slider("앞장서서 이끄는 것이나 설득하는 것을 잘하나요?", 1, 5, 3)
        st.markdown("#### 🗂️ 정리/규칙")
        c = st.slider("계획을 세우고 규칙에 따라 정리하는 것이 편한가요?", 1, 5, 3)

    if st.button("다음 단계로 이동 ➡️", type="primary"):
        # 점수 계산 및 저장
        scores = {'R': r, 'I': i, 'A': a, 'S': s, 'E': e, 'C': c}
        # 상위 2개 코드 조합 (예: IR)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_code = sorted_scores[0][0] + sorted_scores[1][0]
        st.session_state.holland_code = top_code
        st.session_state.step = 2
        st.rerun()

# =============================================================================
# [STEP 2] 가치관 밸런스 게임
# =============================================================================
elif st.session_state.step == 2:
    st.markdown("<h1 class='main-header'>⚖️ STEP 2. 직업 가치관 밸런스</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>직업을 선택할 때 **중요하게 생각하는 요소**의 비중을 조절하세요. (총합은 자동 계산됩니다)</p>", unsafe_allow_html=True)

    col_input, col_chart = st.columns([1, 1])
    
    with col_input:
        v_money = st.slider("💰 **돈 (Money)** : 높은 연봉과 보상", 0, 100, 50)
        v_wlb = st.slider("🧘 **워라밸 (WLB)** : 저녁이 있는 삶, 휴식", 0, 100, 50)
        v_culture = st.slider("🎨 **문화 (Culture)** : 수평적이고 자유로운 분위기", 0, 100, 20)
        v_loc = st.slider("📍 **근무지 (Location)** : 서울/수도권, 출퇴근 편의", 0, 100, 30)
        v_stable = st.slider("🛡️ **안정성 (Stability)** : 정년 보장, 낮은 해고 위험", 0, 100, 50)

    # 벡터 정규화
    total = v_money + v_wlb + v_culture + v_loc + v_stable
    if total == 0: total = 1
    user_vec = [(x/total)*100 for x in [v_money, v_wlb, v_culture, v_loc, v_stable]]
    st.session_state.user_vector = user_vec

    with col_chart:
        fig = go.Figure(go.Scatterpolar(
            r=user_vec + [user_vec[0]],
            theta=['돈', '워라밸', '문화', '근무지', '안정성', '돈'],
            fill='toself',
            name='나의 가치관',
            line_color='#3B82F6'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 40])), 
            showlegend=False, 
            height=350,
            title="나의 가치관 다이아몬드"
        )
        st.plotly_chart(fig, use_container_width=True)

    if st.button("결과 분석 보기 🚀", type="primary"):
        st.session_state.step = 3
        st.rerun()

# =============================================================================
# [STEP 3] 결과 및 로드맵
# =============================================================================
elif st.session_state.step == 3:
    st.markdown(f"<h1 class='main-header'>🎯 분석 결과: [{st.session_state.holland_code}형]</h1>", unsafe_allow_html=True)
    
    # 1. 추천 알고리즘
    def calc_score(row):
        # 가치관 점수 (유클리드 거리)
        job_vec = np.array([row['Money'], row['WLB'], row['Culture'], row['Location'], row['Stability']])
        user_vec = np.array(st.session_state.user_vector)
        value_match = 100 - np.linalg.norm(job_vec - user_vec)
        
        # 홀란드 보너스 (코드가 1개라도 겹치면 가산점)
        holland_bonus = 0
        if st.session_state.holland_code[0] in row['Holland_Code']: holland_bonus += 5
        if st.session_state.holland_code[1] in row['Holland_Code']: holland_bonus += 3
        
        return value_match + holland_bonus

    df['Score'] = df.apply(calc_score, axis=1)
    # 상위 5개 직업 추출
    top_jobs = df.sort_values('Score', ascending=False).head(5)
    
    # 2. 추천 직업 리스트 (가로 배치)
    st.markdown("### 🏆 당신을 위한 TOP 5 추천 직업")
    st.caption("아래 직업 중 하나를 선택하면 상세 로드맵이 펼쳐집니다.")
    
    # 선택을 위한 라디오 버튼 or 버튼 그룹 (여기서는 Selectbox 사용)
    # job_names = top_jobs['직업군'].tolist()
    
    # 카드 형태로 보여주기 위해 컬럼 사용
    cols = st.columns(5)
    selected_job_from_card = None
    
    # 기본 선택값 (1위 직업)
    if 'selected_job' not in st.session_state:
        st.session_state.selected_job = top_jobs.iloc[0]['직업군']

    # 직업 선택 UI
    job_options = top_jobs['직업군'].tolist()
    st.session_state.selected_job = st.selectbox(
        "👉 상세 정보를 확인할 직업을 선택하세요:",
        job_options,
        index=0
    )

    st.divider()

    # 3. 상세 로드맵 뷰 (Expandable Section)
    target_job = st.session_state.selected_job
    
    if target_job in career_guide:
        info = career_guide[target_job]
        
        st.markdown(f"## 🚩 **{target_job}** 마스터 플랜")
        
        # [A] 학과 및 고교학점제
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<div class="info-box">
                <span class="info-title">🎓 대학 전공 추천</span>
                <p>{}</p>
            </div>""".format(info['major']), unsafe_allow_html=True)
        
        with c2:
            st.markdown("""<div class="info-box">
                <span class="info-title">📘 고교 일반선택 과목</span>
                {}
            </div>""".format("".join([f"<span class='tag-base tag-gen'>{s}</span>" for s in info['hs_g'].split(', ')])), unsafe_allow_html=True)
            
        with c3:
            st.markdown("""<div class="info-box">
                <span class="info-title">🚀 고교 진로선택 과목</span>
                {}
            </div>""".format("".join([f"<span class='tag-base tag-career'>{s}</span>" for s in info['hs_c'].split(', ')])), unsafe_allow_html=True)
            
        # [B] 단계별 로드맵
        st.write("")
        st.markdown("### 🛤️ 커리어 로드맵")
        
        for idx, step_text in enumerate(info['steps']):
            # 카드 스타일의 스텝 표시
            st.info(f"**STEP {idx+1}** : {step_text}")
            
    else:
        st.warning("선택하신 직업의 상세 데이터가 준비 중입니다.")

    # 4. 전체 데이터 보기 (옵션)
    with st.expander("📊 추천 직업 데이터 상세 점수 보기"):
        st.dataframe(top_jobs[['직업군', 'Holland_Code', 'Score', 'Money', 'WLB', 'Stability']].set_index('직업군'))
