import streamlit as st
import pandas as pd

# 기존의 긴 전체 경로 대신, 파일 이름만 적어줍니다.
# GitHub 저장소에 파일이 함께 있기 때문에 이렇게만 적어도 인식이 됩니다.
file_path = 'netflix_titles.csv'

try:
    df = pd.read_csv(file_path)
    # 이후 데이터 처리 코드...
except Exception as e:
    st.error(f"❌ 에러가 발생했습니다: {e}")

import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="Netflix 분석 대시보드", layout="wide")

st.title("🎬 넷플릭스 데이터 분석 연습 (개인 연습용)")

# 파일 경로
file_path = r"C:\Users\lhseo\OneDrive\바탕 화면\Netflix Analysis\archive (10)\netflix_titles.csv"

try:
    # 2. 데이터 불러오기
    df = pd.read_csv(file_path)
    st.success("✅ 데이터를 성공적으로 불러왔습니다!")

    # 3. 사이드바 - 상세 검색 필터
    st.sidebar.header("🔍 상세 검색 필터")
    
    # [순서 변경 1] 연도 범위 설정
    year_range = st.sidebar.slider(
        "개봉 연도 범위", 
        int(df['release_year'].min()), 
        int(df['release_year'].max()), 
        (2015, 2021)
    )

    # [순서 변경 2] 먼저 연도로 필터링된 filtered_df를 생성
    filtered_df = df[
        (df['release_year'] >= year_range[0]) & 
        (df['release_year'] <= year_range[1])
    ]

    # [순서 변경 3] 국가 선택 박스 추가
    countries = sorted(df['country'].dropna().unique())
    selected_country = st.sidebar.selectbox("상세 분석할 국가 선택", ["All"] + countries)

    # [순서 변경 4] 선택된 국가가 있으면 한 번 더 필터링 (최종 결과는 display_df)
    if selected_country != "All":
        display_df = filtered_df[filtered_df['country'] == selected_country]
        st.subheader(f"📍 {selected_country} 상세 분석 결과")
    else:
        display_df = filtered_df

    # 4. 상단 핵심 지표 (Metrics) - 이제 display_df를 기준으로 지표를 보여줍니다.
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("분석 대상 콘텐츠 수", len(display_df))
    with col2:
        movie_count = len(display_df[display_df['type'] == 'Movie'])
        st.metric("영화 개수", movie_count)
    with col3:
        tv_count = len(display_df[display_df['type'] == 'TV Show'])
        st.metric("TV 쇼 개수", tv_count)

    st.divider() # 구분선

    # --- 검색 기능 추가 ---
    st.sidebar.divider()
    st.sidebar.header("🔍 키워드 검색")
    search_term = st.sidebar.text_input("콘텐츠 제목 또는 설명 검색")

    if search_term:
        display_df = display_df[
            display_df['title'].str.contains(search_term, case=False, na=False) |
            display_df['description'].str.contains(search_term, case=False, na=False)
        ]

    # --- 자동 인사이트 요약 ---
    st.info(f"💡 **분석 결과 요약:** 선택하신 조건 내에 총 **{len(display_df)}개**의 콘텐츠가 있으며, 그중 영화가 **{len(display_df[display_df['type']=='Movie'])}개**로 다수를 차지하고 있습니다.")

    # 5. 데이터 시각화 파트 (모든 차트는 이제 display_df를 사용합니다)
    row1_col1, row1_col2 = st.columns([1, 1])
    
    with row1_col1:
        st.subheader("1. 데이터 요약 (상위 10개)")
        st.dataframe(display_df.head(10))

    with row1_col2:
        st.subheader("2. 연도별 콘텐츠 등록 추이")
        # 연도별 개수 카운트
        year_counts = display_df['release_year'].value_counts().reset_index()
        year_counts.columns = ['year', 'count']
        year_counts = year_counts.sort_values('year')
        
        fig_line = px.line(year_counts, x='year', y='count', title=f"{selected_country} 지역 성장세")
        st.plotly_chart(fig_line, use_container_width=True)

    row2_col1, row2_col2 = st.columns([1, 1])

    with row2_col1:
        st.subheader("3. 콘텐츠 보유량 상위 10개국")
        # 국가별 분석은 전체 연도 필터 결과(filtered_df)를 보여주는 게 더 의미 있을 수 있습니다.
        top_10_countries = filtered_df['country'].value_counts().head(10)
        fig_country = px.bar(top_10_countries, x=top_10_countries.index, y=top_10_countries.values, 
                             labels={'x': '국가', 'y': '콘텐츠 수'},
                             color=top_10_countries.values, color_continuous_scale='Reds')
        st.plotly_chart(fig_country, use_container_width=True)

    with row2_col2:
        st.subheader("4. 어떤 장르가 가장 많을까?")
        # 선택된 국가/연도 기준 장르 비중
        genres = display_df['listed_in'].str.split(', ').explode().value_counts().head(8)
        fig_genre = px.pie(values=genres.values, names=genres.index, hole=0.3)
        st.plotly_chart(fig_genre, use_container_width=True)

except Exception as e:
    st.error(f"❌ 에러가 발생했습니다: {e}")