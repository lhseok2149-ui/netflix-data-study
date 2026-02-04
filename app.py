import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Netflix 분석 대시보드", layout="wide")
st.title("🎬 넷플릭스 데이터 분석 연습 (개인 연습용)")

file_path = 'netflix_titles.csv' 

try:
    df = pd.read_csv(file_path)
    # 데이터 로딩 성공 메시지는 사이드바에 작게 표시하거나 생략하는 것이 깔끔합니다.
    st.sidebar.success("✅ 데이터 로드 완료")

    # --- 필터링 로직 ---
    st.sidebar.header("🔍 상세 검색 필터")
    
    year_range = st.sidebar.slider(
        "개봉 연도 범위", 
        int(df['release_year'].min()), 
        int(df['release_year'].max()), 
        (2015, 2021)
    )

    filtered_df = df[
        (df['release_year'] >= year_range[0]) & 
        (df['release_year'] <= year_range[1])
    ].copy() # copy()를 써주는 것이 데이터 조작 시 안전합니다.

    countries = sorted(df['country'].dropna().unique())
    selected_country = st.sidebar.selectbox("상세 분석할 국가 선택", ["All"] + countries)

    if selected_country != "All":
        display_df = filtered_df[filtered_df['country'] == selected_country]
    else:
        display_df = filtered_df

    # --- 검색 기능 ---
    search_term = st.sidebar.text_input("콘텐츠 제목 또는 설명 검색")
    if search_term:
        display_df = display_df[
            display_df['title'].str.contains(search_term, case=False, na=False) |
            display_df['description'].str.contains(search_term, case=False, na=False)
        ]

    # --- 화면 표시 ---
    if display_df.empty:
        st.warning("⚠️ 선택하신 조건에 해당하는 데이터가 없습니다. 필터를 조절해 보세요.")
    else:
        # 지표 (Metrics)
        col1, col2, col3 = st.columns(3)
        col1.metric("분석 대상 콘텐츠", f"{len(display_df)}개")
        col2.metric("영화", f"{len(display_df[display_df['type'] == 'Movie'])}개")
        col3.metric("TV 쇼", f"{len(display_df[display_df['type'] == 'TV Show'])}개")

        st.divider()

        # 시각화
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.subheader("1. 데이터 샘플 (상위 10개)")
            st.dataframe(display_df.head(10), use_container_width=True)

        with row1_col2:
            st.subheader("2. 연도별 콘텐츠 등록 추이")
            year_counts = display_df['release_year'].value_counts().reset_index()
            year_counts.columns = ['year', 'count']
            fig_line = px.line(year_counts.sort_values('year'), x='year', y='count', markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.subheader("3. 콘텐츠 보유량 상위 10개국")
            top_10 = filtered_df['country'].value_counts().head(10)
            fig_bar = px.bar(top_10, color=top_10.values, color_continuous_scale='Reds')
            st.plotly_chart(fig_bar, use_container_width=True)

        with row2_col2:
            st.subheader("4. 주요 장르 비중")
            genres = display_df['listed_in'].str.split(', ').explode().value_counts().head(8)
            fig_pie = px.pie(values=genres.values, names=genres.index, hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

except Exception as e:
    st.error(f"❌ 실행 중 오류가 발생했습니다: {e}")