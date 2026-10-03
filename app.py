import streamlit as st
from data_loader import DataLoader
from filter_analyzer import DataFilter, DataAnalyzer
from viz_plotly import PlotlyVisualizer
from viz_pydeck import PydeckVisualizer

# 1. 페이지 설정
st.set_page_config(page_title="상권 분석 대시보드", layout="wide")
st.title("📊 상권 매출 데이터 3D 시각화 대시보드")

# 2. 데이터 로드 (데이터 전처리 담당의 클래스 활용)
@st.cache_data
def load_data():
    loader = DataLoader("data.csv")  # 파일 경로
    return loader.load_and_preprocess()

df_raw = load_data()

# 3. 사이드바 필터 조건 선택 (Streamlit 담당)
st.sidebar.header("필터 조건")
selected_year = st.sidebar.selectbox("연도", [2024, 2025, 2026])
selected_quarter = st.sidebar.selectbox("분기", [1, 2, 3, 4])

# 4. 데이터 필터링 (분석&필터 담당의 클래스 활용)
filter_tool = DataFilter(df_raw)
df_filtered = filter_tool.apply_filters(selected_year, selected_quarter)

# 5. 통계 정보 표시
analyzer = DataAnalyzer(df_filtered)
stats = analyzer.get_summary_stats()

col1, col2, col3 = st.columns(3)
col1.metric("총 매출액", f"{stats['총매출']:,} 원")
col2.metric("총 건수", f"{stats['총건수']:,} 건")
col3.metric("평균 객단가", f"{int(stats['평균객단가']):,} 원")

st.markdown("---")

# 6. 시각화 영역 (Plotly & Pydeck 담당의 클래스 활용)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌋 Plotly 3D 가우스 매출 산맥")
    plotly_viz = PlotlyVisualizer(df_filtered)
    fig_3d = plotly_viz.create_3d_gaussian_surface()
    st.plotly_chart(fig_3d, use_container_width=True)

with col_right:
    st.subheader("🗺️ Pydeck 3D 상권 기둥 지도")
    pydeck_viz = PydeckVisualizer(df_filtered)
    deck_map = pydeck_viz.create_column_map()
    st.pydeck_chart(deck_map)