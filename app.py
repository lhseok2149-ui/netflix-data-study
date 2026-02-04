import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="Netflix 분석 대시보드", layout="wide")

st.title("🎬 넷플릭스 데이터 분석 연습 (개인 연습용)")

# 🌟 파일 경로 설정 (GitHub 배포를 위해 파일 이름만 사용)
file_path = 'netflix_titles.csv' 

try:
    # 2. 데이터 불러오기
    df = pd.read_csv(file_path)
    st.success("✅ 데이터를 성공적으로 불러왔습니다!")

    # 3. 사이드바 - 상세 검색 필터
    st.sidebar.header("🔍 상세 검색 필터")
    
    # 연도 범위 설정
    year_range = st.sidebar.slider(
        "개봉 연도 범위", 
        int(df['release_year'].min()), 
        int(df['release_year'].max()), 
        (2015, 2021)
    )

    # 연도로 먼저 필터링
    filtered_df = df[
        (df['release_year'] >= year_range[0]) & 
        (df['release_year'] <= year_range[1])
    ]

    # 국가 선택 박스
    countries = sorted(df['country'].dropna().unique())
    selected_country = st.sidebar.selectbox("상세 분석할 국가 선택", ["All"] + countries)

    # 국가 필터 적용
    if selected_country != "All":
        display_df = filtered_df[filtered_df['country'] == selected_country]
        st.subheader(f"📍 {selected_country} 상세 분석 결과")
    else:
        display_df = filtered_df

    # 4. 상단 핵심 지표 (Metrics)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("분석 대상 콘텐츠 수", len(display_df))
    with col2:
        movie_count = len(display_df[display_df['type'] == 'Movie'])
        st.metric("영화 개수", movie_count)
    with col3:
        tv_count = len(display_df[display_df['type'] == 'TV Show'])
        st.metric("TV 쇼 개수", tv_count)

    st.divider() 

    # --- 검색 기능 ---
    st.sidebar.divider()
    st.sidebar.header("🔍 키워드 검색")
    search_term = st.sidebar.text_input("콘텐츠 제목 또는 설명 검색")

    if search_term:
        display_df = display_df[
            display_df['title'].str.contains(search_term, case=False, na=False) |
            display_df['description'].str.contains(search_term, case=False, na=False)
        ]

    # --- 요약 메시지 ---
    st.info(f"💡 **분석 결과 요약:** 선택하신 조건 내에 총 **{len(display_df)}개**의 콘텐츠가 있습니다.")

    # 5. 데이터 시각화
    row1_col1, row1_col2 = st.columns([1, 1])
    
    with row1_col1:
        st.subheader("1. 데이터 요약 (상위 10개)")
        st.dataframe(display_df.head(10))

    with row1_col2:
        st.subheader("2. 연도별 콘텐츠 등록 추이")
        year_counts = display_df['release_year'].value_counts().reset_index()
        year_counts.columns = ['year', 'count']
        year_counts = year_counts.sort_values('year')
        fig_line = px.line(year_counts, x='year', y='count', title="연도별 성장세")
        st.plotly_chart(fig_line, use_container_width=True)

    row2_col1, row2_col2 = st.columns([1, 1])

    with row2_col1:
        st.subheader("3. 콘텐츠 보유량 상위 10개국")
        top_10_countries = filtered_df['country'].value_counts().head(10)
        fig_country = px.bar(top_10_countries, x=top_10_countries.index, y=top_10_countries.values, 
                             color=top_10_countries.values, color_continuous_scale='Reds')
        st.plotly_chart(fig_country, use_container_width=True)

    with row2_col2:
        st.subheader("4. 장르 비중 (TOP 8)")
        genres = display_df['listed_in'].str.split(', ').explode().value_counts().head(8)
        fig_genre = px.pie(values=genres.values, names=genres.index, hole=0.3)
        st.plotly_chart(fig_genre, use_container_width=True)

except Exception as e:
    st.error(f"❌ 에러가 발생했습니다: {e}")