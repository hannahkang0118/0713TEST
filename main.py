import streamlit as st
 
import streamlit as st
import pandas as pd

# 1. 페이지 설정 (와이드 레이아웃)
st.set_page_config(page_title="도시 열섬현상 분석", layout="wide")

# 대제목 및 앱 설명
st.title("🌡️ 서울과 양평의 도시 열섬현상 분석")
st.markdown("대도시(서울)와 suburban 지역(양평)의 기온 데이터를 비교하여 도시 열섬현상(Urban Heat Island)을 분석합니다.")
st.markdown("---")

# 2. 데이터 불러오기 및 전처리 (캐싱 처리로 속도 최적화)
@st.cache_data
def load_and_process_data():
    # 데이터 로드 (요청하신 cp949 인코딩 적용)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 날짜형(datetime) 변환
    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])
    
    # 필요한 열만 필터링 및 이름 변경
    seoul = seoul[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "서울"})
    yangpyeong = yangpyeong[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "양평"})
    
    # 일시(Datetime) 기준으로 데이터 병합
    df = pd.merge(seoul, yangpyeong, on="일시")
    
    # 분석에 필요한 시간 파생 변수 및 기온차(서울 - 양평) 계산
    df["시"] = df["일시"].dt.hour
    df["월"] = df["일시"].dt.month
    df["기온차"] = df["서울"] - df["양평"]
    
    return df

# 파일 읽기 에러 예외 처리
try:
    df = load_and_process_data()

    # 3. 주요 요약 지표 (Metrics) 표시
    avg_diff = df["기온차"].mean()
    max_diff_idx = df["기온차"].idxmax()
    max_diff_time = df.loc[max_diff_idx, "일시"]
    max_diff_val = df.loc[max_diff_idx, "기온차"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="연간 평균 기온차 (서울 - 양평)", value=f"{avg_diff:.2f} °C")
    with col2:
        st.metric(label="최대 기온차 발생 시점", value=max_diff_time.strftime('%m월 %d일 %H시'))
    with col3:
        st.metric(label="최대 기온차 기록", value=f"{max_diff_val:.1f} °C")
        
    st.markdown("---")

    # 4. 그래프 ① : 1년간 두 지역의 기온 변화 (선그래프)
    st.subheader("① 1년간 서울과 양평의 기온 변화")
    line_df = df.set_index("일시")[["서울", "양평"]]
    st.line_chart(line_df)

    st.markdown("---")

    # 5. 그래프 ② & ③ : 기온차 시각화 (막대그래프 좌우 배치)
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("② 시각(0~23시)별 평균 기온차 (서울 - 양평)")
        hour_diff = df.groupby("시")["기온차"].mean()
        st.bar_chart(hour_diff)
        st.caption("💡 일반적으로 대도시의 콘크리트 축열 현상과 인공열로 인해 **밤과 새벽 시간대**에 기온차가 뚜렷해집니다.")

    with col_right:
        st.subheader("③ 월(1~12월)별 평균 기온차 (서울 - 양평)")
        month_diff = df.groupby("월")["기온차"].mean()
        st.bar_chart(month_diff)
        st.caption("💡 계절적 기후 특성(일사량, 습도, 바람 등)에 따른 월별 열섬현상의 강도 변화를 보여줍니다.")

    st.markdown("---")

    # 6. 데이터 확인 탭 (Expander)
    with st.expander("🔍 정제된 데이터 전체보기"):
        st.dataframe(df, use_container_width=True)

except FileNotFoundError:
    st.error("❌ 파일 로드 실패: '서울_기온.csv'와 '양평_기온.csv' 파일이 현재 파이썬 스크립트와 동일한 폴더에 위치해 있는지 확인해 주세요.")
