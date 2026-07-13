import streamlit as st
import streamlit as st
import pandas as pd

# 1. 페이지 설정 (와이드 레이아웃 적용)
st.set_page_config(page_title="도시 열섬현상 및 전력 수요 분석", layout="wide")

st.title("🌡️ 서울·양평 열섬현상 및 기온-전력 수요 연계 분석")
st.markdown("본 대시보드는 2025년 시간별 데이터를 바탕으로 도시 열섬현상을 분석하고, 기온 변화에 따른 전력수요의 영향을 살펴봅니다.")
st.markdown("---")

# 2. 데이터 로딩 및 전처리 함수 (캐싱 적용으로 웹앱 속도 최적화)
@st.cache_data
def load_data():
    # 데이터 읽기 (요청하신 cp949 인코딩 반영)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 날짜형(datetime) 변환
    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])
    power["일시"] = pd.to_datetime(power["일시"])
    
    # 기온 데이터 열 필터링 및 이름 정리
    seoul_temp = seoul[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "서울"})
    yangpyeong_temp = yangpyeong[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "양평"})
    
    # [탭1용 데이터] 서울 기온 + 양평 기온 병합 (일시 기준)
    df_temp = pd.merge(seoul_temp, yangpyeong_temp, on="일시")
    df_temp["시"] = df_temp["일시"].dt.hour
    df_temp["월"] = df_temp["일시"].dt.month
    df_temp["기온차"] = df_temp["서울"] - df_temp["양평"]
    
    # [탭2용 데이터] 서울 기온 + 전력수요 병합 (일시 기준)
    df_power = pd.merge(seoul_temp, power[["일시", "전력수요(MWh)"]], on="일시")
    df_power["월"] = df_power["일시"].dt.month
    
    # 기온 구간 생성 (5도 단위 버림 연산 처리 후 정수형 변환)
    df_power["기온구간"] = (df_power["서울"] // 5 * 5).astype(int)
    
    return df_temp, df_power

# 예외 처리를 통한 안정적인 파일 로드
try:
    df_temp, df_power = load_data()
    
    # 3. 탭 구성 (st.tabs 사용)
    tab1, tab2 = st.tabs(["📊 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # -------------------------------------------------------------------------
    # [탭1: 열섬 분석]
    # -------------------------------------------------------------------------
    with tab1:
        st.header("🏢 도시 열섬현상(UHI) 분석")
        st.markdown("서울(대도시)과 양평(교외 지역)의 기온 데이터를 비교하여 도시화에 따른 열축적 효과를 확인합니다.")
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역의 기온 변화 패턴")
        line_df = df_temp.set_index("일시")[["서울", "양평"]]
        st.line_chart(line_df)
        
        st.markdown("---")
        
        # ②, ③ 그래프 화면 분할 배치 (좌우)
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("② 시각(0~23시)별 평균 기온차 (서울 - 양평)")
            hour_diff = df_temp.groupby("시")["기온차"].mean()
            st.bar_chart(hour_diff)
            st.caption("💡 대도시 인공열과 아스팔트·콘크리트 축열로 주로 밤~새벽 시간대에 기온차가 극대화됩니다.")
            
        with col2:
            st.subheader("③ 월(1~12월)별 평균 기온차 (서울 - 양평)")
            month_diff = df_temp.groupby("월")["기온차"].mean()
            st.bar_chart(month_diff)
            st.caption("💡 일사량, 계절풍 및 대기 정체 정도 등 계절적 요인에 따른 월별 열섬 추이입니다.")
            
        # 원본 데이터 확인 펼치기
        with st.expander("🔍 열섬 분석 원본 데이터 확인"):
            st.dataframe(df_temp, use_container_width=True)

    # -------------------------------------------------------------------------
    # [탭2: 전력 연결]
    # -------------------------------------------------------------------------
    with tab2:
        st.header("📈 기온과 전력수요의 상관관계 분석")
        st.markdown("서울의 기온 변화에 따른 실제 전력수요(MWh)의 연계 특징을 다각도로 살펴봅니다.")
        
        # ① 기온(가로)과 전력수요(세로)의 산점도
        st.subheader("① 기온과 전력수요의 상관관계 (산점도)")
        scatter_df = df_power[["서울", "전력수요(MWh)"]].rename(columns={"서울": "서울 기온(°C)"})
        st.scatter_chart(data=scatter_df, x="서울 기온(°C)", y="전력수요(MWh)")
        st.caption("💡 기온이 아주 낮거나(난방) 높을 때(냉방) 양쪽 끝에서 전력 수요가 증가하는 U자 형태의 패턴을 보입니다.")
        
        st.markdown("---")
        
        # ②, ③ 그래프 화면 분할 배치 (좌우)
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("② 기온 구간별 평균 전력수요")
            # 5도 단위 구간별 평균 계산 및 시각화용 셋팅
            temp_band_power = df_power.groupby("기온구간")["전력수요(MWh)"].mean().reset_index()
            temp_band_power["기온구간_표시"] = temp_band_power["기온구간"].apply(lambda x: f"{x} ~ {x+5}°C")
            chart_band = temp_band_power.set_index("기온구간_표시")["전력수요(MWh)"]
            st.bar_chart(chart_band)
            st.caption("💡 기온 구간별(5°C 단위) 냉난방 임계점이 작동하여 전력이 급증하기 시작하는 온도를 직관적으로 볼 수 있습니다.")
            
        with col4:
            st.subheader("③ 월(1~12월)별 평균 전력수요")
            month_power = df_power.groupby("월")["전력수요(MWh)"].mean()
            st.bar_chart(month_power)
            st.caption("💡 전력 사용량이 피크를 이루는 하절기(7-8월) 및 동절기(12-1월)의 전력 공급 기획용 월별 추이입니다.")
            
        # 원본 데이터 확인 펼치기
        with st.expander("🔍 전력 연계 분석 원본 데이터 확인"):
            st.dataframe(df_power, use_container_width=True)

except FileNotFoundError:
    st.error("❌ 파일 로드 실패: 동일 폴더 내에 '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 파일이 모두 존재하는지 확인해 주세요.")
