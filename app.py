import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# -----------------------------------------------------------------------------
# 1. 페이지 설정 & 스타일 (Page Config & Style)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Career Balance Sheet",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS로 디자인 다듬기
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .st-emotion-cache-16idsys p {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 데이터 로드 (Data Loading - Full Dataset)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # 1순위: 구글 시트 연결 시도
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Balance", ttl=0)
        return df
    except Exception:
        pass
    
    # 2순위: 연결 실패 시 내장 데이터 사용 (총합 100점 버전)
    data = {
        '직업군': [
            '전략 컨설턴트', '외국계 투자은행(IB)', '대형 로펌 변호사', '공인회계사(Big4)', '사모펀드(PE) 심사역',
            '네카라쿠배 개발자', '유니콘 스타트업 직원', '게임 개발자', 'AI 연구원/엔지니어', '대기업 전략기획',
            '증권사 브로커/PB', '시중은행 행원', '공기업 (메이저)', '공기업 (지방근무)', '7/9급 공무원',
            '5급 행정고시 사무관', '초등/중등 교사', '대학교 교직원', '대학 교수', '국책연구소 연구원',
            '의사 (전문의)', '치과의사', '약사', '간호사 (대학병원)', '수의사', '한의사',
            '방송국 PD', '방송기자/아나운서', '웹툰/웹소설 작가', '엔터테인먼트 A&R', '광고기획자 (AE)',
            '패션 MD/바이어', '항공기 조종사(파일럿)', '객실 승무원', '호텔리어/지배인', '셰프/요리사',
            '반도체 엔지니어', '배터리/2차전지 연구원', '자동차 엔지니어', '석유화학/정유 엔지니어', '제약/바이오 연구원',
            '건설/토목 엔지니어', '스마트팜 전문가', '스포츠 에이전트/마케터', '전시/공연 기획자', '통번역사',
            '노무사', '감정평가사', '관세사', '변리사', '1인 크리에이터/유튜버',
            '워케이션 프리랜서', '공간/인테리어 디자이너', '메타버스/VR 크리에이터', '데이터 사이언티스트'
        ],
        'Money': [
            50, 55, 50, 40, 50, 35, 25, 35, 40, 40, 45, 35, 25, 25, 15, 25, 15, 20, 30, 30,
            45, 45, 30, 30, 35, 40, 25, 30, 35, 15, 25, 25, 45, 25, 15, 25, 45, 40, 40, 45,
            35, 40, 30, 25, 20, 30, 35, 40, 35, 45, 25, 20, 25, 30, 45
        ],
        'WLB': [
            5, 5, 5, 10, 10, 20, 15, 15, 15, 15, 10, 25, 30, 30, 35, 10, 30, 35, 20, 30,
            10, 15, 30, 10, 20, 25, 5, 5, 15, 10, 10, 10, 15, 15, 15, 5, 10, 15, 20, 20,
            25, 5, 25, 10, 10, 25, 25, 20, 25, 10, 10, 35, 10, 20, 20
        ],
        'Culture': [
            10, 5, 10, 10, 10, 15, 35, 25, 15, 10, 10, 10, 10, 5, 5, 10, 15, 10, 15, 10,
            10, 10, 10, 10, 10, 10, 30, 15, 25, 35, 25, 20, 10, 15, 15, 15, 10, 15, 10, 5,
            15, 10, 15, 20, 25, 15, 10, 5, 10, 10, 45, 20, 25, 25, 15
        ],
        'Location': [
            20, 20, 20, 20, 15, 10, 10, 10, 10, 15, 15, 10, 10, 10, 10, 25, 10, 10, 5, 10,
            15, 10, 10, 25, 15, 5, 20, 25, 10, 25, 25, 25, 10, 25, 30, 30, 15, 10, 10, 10,
            5, 20, 15, 25, 25, 15, 15, 15, 15, 15, 10, 10, 25, 10, 10
        ],
        'Stability': [
            15, 15, 15, 20, 15, 20, 15, 15, 20, 20, 20, 20, 25, 30, 35, 30, 30, 25, 30, 20,
            20, 20, 20, 25, 20, 20, 20, 25, 15, 15, 15, 20, 20, 20, 25, 25, 20, 20, 20, 20,
            20, 25, 15, 20, 20, 15, 15, 20, 15, 20, 10, 15, 15, 15, 10
        ]
    }
    return pd.DataFrame(data)

df = load_data()

# -----------------------------------------------------------------------------
# 3. 사이드바 (Sidebar)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("🔍 Filter")
    st.write("비교할 직업을 선택하세요.")
    
    # 직업 검색 및 선택
    job_list = sorted(df['직업군'].unique().tolist())
    selected_jobs = st.multiselect(
        "직업 목록 (최대 3개 추천)",
        job_list,
        default=["전략 컨설턴트", "7/9급 공무원"]
    )
    
    st.divider()
    
    st.info("""
    **💡 항목별 가이드**
    * **Money:** 생애 소득 & 보상
    * **WLB:** 워라밸 & 휴식
    * **Culture:** 조직문화 & 자율성
    * **Location:** 근무지 & 서울 접근성
    * **Stability:** 고용 안정 & 정년
    """)

# -----------------------------------------------------------------------------
# 4. 차트 생성 함수 (Radar Chart)
# -----------------------------------------------------------------------------
def plot_radar_chart(jobs):
    fig = go.Figure()
    categories = ['Money', 'WLB', 'Culture', 'Location', 'Stability']
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A'] # Plotly 기본 색상

    for i, job in enumerate(jobs):
        job_data = df[df['직업군'] == job].iloc[0]
        values = [job_data[cat] for cat in categories]
        values += [values[0]]
        categories_closed = categories + [categories[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories_closed,
            fill='toself',
            name=job,
            line_color=colors[i % len(colors)],
            opacity=0.6
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 60], tickfont=dict(size=10, color="gray")),
            angularaxis=dict(tickfont=dict(size=12, weight="bold"))
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
        margin=dict(l=40, r=40, t=20, b=40),
        height=500
    )
    return fig

# -----------------------------------------------------------------------------
# 5. 메인 레이아웃 (Main Content)
# -----------------------------------------------------------------------------
st.title("⚖️ Career Balance Sheet")
st.markdown("##### :grey[당신의 직업 선택, 무엇을 얻고 무엇을 포기하시겠습니까?]")
st.write("")

# 탭 구조로 화면 분리
tab1, tab2, tab3 = st.tabs(["📊 비교 분석", "📋 전체 데이터", "💡 맞춤 추천"])

# [TAB 1] 비교 분석 -----------------------------------------------------------
with tab1:
    if selected_jobs:
        # 1. 단일 직업 선택 시 하이라이트 메트릭 보여주기
        if len(selected_jobs) == 1:
            job_name = selected_jobs[0]
            job_row = df[df['직업군'] == job_name].iloc[0]
            # 가장 점수가 높은 항목 찾기
            best_cat = job_row[['Money', 'WLB', 'Culture', 'Location', 'Stability']].astype(float).idxmax()
            best_val = job_row[best_cat]
            
            st.markdown(f"### ✨ **{job_name}**의 핵심 키워드")
            m1, m2, m3 = st.columns(3)
            m1.metric(label="최고 강점", value=best_cat, delta=f"{best_val}점")
            m2.metric(label="Money (보상)", value=job_row['Money'])
            m3.metric(label="Stability (안정성)", value=job_row['Stability'])
            st.divider()

        # 2. 메인 차트와 데이터 테이블
        col_chart, col_data = st.columns([1.5, 1])
        
        with col_chart:
            st.subheader("🕸️ 밸런스 레이더")
            chart = plot_radar_chart(selected_jobs)
            st.plotly_chart(chart, use_container_width=True)
            
        with col_data:
            st.subheader("🔢 상세 스코어")
            # 데이터프레임 가공
            view_df = df[df['직업군'].isin(selected_jobs)].set_index('직업군')
            view_df = view_df[['Money', 'WLB', 'Culture', 'Location', 'Stability']]
            
            # 히트맵 스타일링 적용
            st.dataframe(
                view_df.style.background_gradient(cmap='Blues', axis=None, vmin=0, vmax=60),
                use_container_width=True,
                height=400
            )
            
        # 3. 간단한 코멘트
        st.info("💡 **Tip:** 차트의 면적은 총점이 같으므로 비슷합니다. 어느 방향으로 뾰족한지(성향)를 확인하세요!")

    else:
        st.warning("👈 왼쪽 사이드바에서 직업을 선택해주세요.")

# [TAB 2] 전체 데이터 ---------------------------------------------------------
with tab2:
    st.subheader("📁 전체 직업 데이터베이스")
    st.markdown("모든 직업의 5대 요소 점수를 확인하고 검색할 수 있습니다.")
    
    # 검색 기능
    search_term = st.text_input("직업 이름 검색", "")
    
    if search_term:
        filtered_df = df[df['직업군'].str.contains(search_term)]
    else:
        filtered_df = df
        
    st.dataframe(
        filtered_df.set_index('직업군').style.bar(color='#d65f5f', vmin=0, vmax=60),
        use_container_width=True,
        height=600
    )

# [TAB 3] 맞춤 추천 (간단 버전) -----------------------------------------------
with tab3:
    st.subheader("🎯 나에게 맞는 직업 찾기")
    st.write("가장 중요하게 생각하는 가치를 선택해보세요.")
    
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        priority = st.selectbox("1순위 중요 항목", ['Money', 'WLB', 'Culture', 'Location', 'Stability'])
    with col_filter2:
        min_score = st.slider(f"최소 {priority} 점수", 0, 60, 40)
        
    # 필터링 로직
    result = df[df[priority] >= min_score].sort_values(by=priority, ascending=False)
    
    if not result.empty:
        st.success(f"조건에 맞는 직업이 **{len(result)}**개 있습니다!")
        st.dataframe(
            result[['직업군', priority, 'Money', 'WLB', 'Stability']].set_index('직업군'),
            use_container_width=True
        )
    else:
        st.error("조건에 맞는 직업이 없습니다. 점수를 조금 낮춰보세요.")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.divider()
st.caption("© 2026 Plant the Seed | Data based on relative comparison (Sum=100)")
