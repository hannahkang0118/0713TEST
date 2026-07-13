<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>열섬현상과 전력수요의 관계 분석</title>
    <!-- 데이터 파싱 및 시각화 라이브러리 CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Chart.js 추세선 플러그인 -->
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-trendline"></script>
    
    <style>
        :root {
            --primary-blue: #2b6cb0;
            --secondary-blue: #ebf8ff;
            --primary-orange: #dd6b20;
            --secondary-orange: #fffaf0;
            --dark-gray: #2d3748;
            --light-gray: #f7fafc;
            --border-color: #e2e8f0;
            --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        }

        body {
            background-color: var(--light-gray);
            color: var(--dark-gray);
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* 헤더 디자인 */
        header {
            background: linear-gradient(135deg, var(--primary-blue), #4299e1);
            color: white;
            padding: 30px 20px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: var(--card-shadow);
        }

        header h1 {
            font-size: 2rem;
            margin-bottom: 8px;
        }

        header p {
            font-size: 1.1rem;
            opacity: 0.95;
            font-weight: 500;
        }

        /* 오류 배너 */
        #error-banner {
            display: none;
            background-color: #fff5f5;
            border: 1px solid #fed7d7;
            border-left: 5px solid #e53e3e;
            color: #c53030;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
        }

        #error-banner h3 { margin-bottom: 8px; }
        #error-banner ul { margin-left: 20px; margin-top: 8px; }

        /* 로딩 창 */
        #loading-spinner {
            text-align: center;
            padding: 5px;
            font-size: 1.2rem;
            color: var(--primary-blue);
            font-weight: bold;
        }

        /* 둥근 카드 형태 디자인 */
        .card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border-color);
        }

        .card h2 {
            font-size: 1.3rem;
            color: var(--primary-blue);
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* 필터 스타일 */
        .filter-section {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 15px;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .filter-group label {
            font-size: 0.85rem;
            font-weight: bold;
            color: #4a5568;
        }

        .filter-group select {
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background-color: white;
            font-size: 0.95rem;
            color: var(--dark-gray);
            outline: none;
            cursor: pointer;
        }

        .filter-group select:focus {
            border-color: var(--primary-blue);
        }

        /* 반응형 그리드 뷰 */
        .grid-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }

        @media (max-width: 900px) {
            .grid-layout {
                grid-template-columns: 1fr;
            }
        }

        .chart-container {
            position: relative;
            width: 100%;
            height: 380px;
            margin-top: 10px;
        }

        /* 상관관계 요약 스탯 */
        .stats-wrapper {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .stats-wrapper {
                grid-template-columns: 1fr;
            }
        }

        .stat-box {
            background-color: var(--secondary-orange);
            border: 1px solid #feebc8;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .stat-box .r-val {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--primary-orange);
            margin: 5px 0;
        }

        .stat-box .r-text {
            font-weight: bold;
            font-size: 1.05rem;
            color: #c05621;
        }

        .notice-text {
            font-size: 0.85rem;
            color: #718096;
            margin-top: 12px;
            padding-left: 8px;
            border-left: 3px solid #cbd5e0;
        }

        /* 결과 요약 텍스트 리스트 */
        .result-list {
            list-style-type: none;
        }

        .result-list li {
            position: relative;
            padding-left: 25px;
            margin-bottom: 12px;
        }

        .result-list li::before {
            content: "•";
            position: absolute;
            left: 8px;
            color: var(--primary-orange);
            font-size: 1.5rem;
            top: -4px;
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>열섬현상과 전력수요의 관계 분석</h1>
        <p>🤔 탐구 질문: 열섬 강도가 커질수록 전력수요도 증가할까?</p>
    </header>

    <!-- 문제 상황 대처 에러 알림창 -->
    <div id="error-banner">
        <h3>⚠️ 데이터를 불러오지 못했습니다.</h3>
        <p>아래 원인을 점검하고 해결해 보세요:</p>
        <ul>
            <li><strong>파일 위치 확인:</strong> <code>index.html</code>과 같은 폴더(경로) 내에 <code>서울_기온.csv</code>, <code>양평_기온.csv</code>, <code>전력수요.csv</code> 파일이 대소문자까지 정확히 배치되었는지 확인해 주세요.</li>
            <li><strong>로컬 보안 정책(CORS) 제한:</strong> 로컬 환경(하드디스크)에서 더블 클릭으로 파일을 열 경우 브라우저 보안 정책상 파일 로드가 거부될 수 있습니다. VS Code의 <strong>Live Server</strong> 환경을 사용해 실행하거나, <strong>GitHub Pages 저장소</strong>에 업로드하여 확인하시면 정상적으로 구동됩니다.</li>
        </ul>
    </div>

    <div id="loading-spinner">📊 데이터를 파싱하고 로드하는 중입니다...</div>

    <div id="main-content" style="display: none;">
        <!-- 2. 데이터 확인 영역 -->
        <div class="card">
            <h2>ℹ️ 데이터 정보 및 날짜 필터</h2>
            <p>본 데이터 시각화 앱은 <strong>2025년 1년 동안 수집된 1시간 단위 데이터(총 8,760개 행)</strong>를 분석 기반으로 삼고 있습니다. 도심(서울)과 교외(양평)의 기온 격차 추이와 같은 시간대의 전국 전력수요(MWh) 변동 데이터를 정밀 연계 매핑하여 분석을 실시간으로 도출합니다.</p>
            
            <div class="filter-section">
                <div class="filter-group">
                    <label for="month-select">📅 분석 월 선택</label>
                    <select id="month-select">
                        <!-- 스크립트에서 자동 동적 바인딩 -->
                    </select>
                </div>
            </div>
        </div>

        <div class="grid-layout">
            <!-- 3. 열섬현상 분석 카드 -->
            <div class="card">
                <h2>🏙️ 1. 도시 열섬현상(UHI) 분석</h2>
                <p>같은 시간대 도심(서울)과 교외(양평)의 온도 분포 추이입니다.<br><strong>열섬 강도 = 도심 기온(서울) - 교외 기온(양평)</strong> 공식을 적용하여 선그래프로 모니터링합니다.</p>
                <div class="chart-container">
                    <canvas id="tempChart"></canvas>
                </div>
            </div>

            <!-- 4. 전력수요 분석 카드 -->
            <div class="card">
                <h2>⚡ 2. 시간 흐름별 전력수요 분석</h2>
                <p>선택한 달의 시간 변화에 연동되는 전력수요량(MWh)의 변화폭입니다. 기온이 높은 여름철 피크 시기나 혹한기 난방 전력의 임계 흐름을 한눈에 식별하기 용이합니다.</p>
                <div class="chart-container">
                    <canvas id="powerChart"></canvas>
                </div>
            </div>
        </div>

        <!-- 5. 상관관계 분석 카드 -->
        <div class="card">
            <h2>📊 3. 두 변수 간의 상관관계 심층 분석</h2>
            <p>산출된 <strong>시간별 열섬 강도</strong>를 가로축(X축), <strong>전력수요(MWh)</strong>를 세로축(Y축)으로 정의하여 분포 특징과 오렌지색 선형 추세선을 도출합니다.</p>
            
            <div class="stats-wrapper" style="margin-top: 15px;">
                <div>
                    <div class="stat-box">
                        <p style="font-size: 0.9rem; color: #7b341e; font-weight: bold;">피어슨 상관계수 (r)</p>
                        <div class="r-val" id="r-value">0.00</div>
                        <div class="r-text" id="r-interpretation">분석 중</div>
                    </div>
                    <p class="notice-text">
                        ⚠️ <strong>통계적 유의사항:</strong> 산출된 상관계수는 두 변수의 변화 방향성이 유사함을 나타내는 지표일 뿐, 두 요인의 직접적인 <strong>'인과관계'를 강제하고 확정하는 의미는 아닙니다.</strong> 전력 소비는 요일 특성이나 경제 산업 생산 조업량 등 타 거시 변수 요인이 복합 작용할 수 있습니다.
                    </p>
                </div>
                <div class="chart-container">
                    <canvas id="scatterChart"></canvas>
                </div>
            </div>
        </div>

        <!-- 6. 탐구 결과 카드 -->
        <div class="card">
            <h2>📝 4. 실제 데이터 기반 탐구 결과 요약</h2>
            <ul class="result-list" id="summary-text-box">
                <!-- 동적으로 채워집니다 -->
            </ul>
        </div>
    </div>
</div>

<script>
    // 전역 상태 변수
    let mergedDataset = []; 
    let activeCharts = {};

    // 데이터 파일 주소 셋팅
    const csvPaths = {
        seoul: "서울_기온.csv",
        yangpyeong: "양평_기온.csv",
        power: "전력수요.csv"
    };

    // PapaParse 기반 비동기 데이터 fetch & 파싱 래퍼
    function parseCsvFile(url) {
        return new Promise((resolve, reject) => {
            Papa.parse(url, {
                download: true,
                header: true,
                skipEmptyLines: true,
                encoding: "cp949",
                complete: (res) => resolve(res.data),
                error: (err) => reject(err)
            });
        });
    }

    // 메인 로드 기동 함수
    async function startApplication() {
        try {
            // 3가지 파일 동시 로드 진행
            const [seoulRaw, yangpyeongRaw, powerRaw] = await Promise.all([
                parseCsvFile(csvPaths.seoul),
                parseCsvFile(csvPaths.yangpyeong),
                parseCsvFile(csvPaths.power)
            ]);

            // 일시(Timestamp) 기반 효율적인 해시 맵 구조로 매핑 결합
            const dataIntegrator = new Map();

            seoulRaw.forEach(row => {
                if(row['일시'] && row['기온(°C)']) {
                    dataIntegrator.set(row['일시'], {
                        timeStr: row['일시'],
                        seoulTemp: parseFloat(row['기온(°C)'])
                    });
                }
            });

            yangpyeongRaw.forEach(row => {
                const existing = dataIntegrator.get(row['일시']);
                if(existing && row['기온(°C)']) {
                    existing.yangpyeongTemp = parseFloat(row['기온(°C)']);
                }
            });

            powerRaw.forEach(row => {
                const existing = dataIntegrator.get(row['일시']);
                if(existing && row['전력수요(MWh)']) {
                    existing.powerDemand = parseFloat(row['전력수요(MWh)']);
                }
            });

            // 매핑이 유효하고 숫자가 결측되지 않은 무결한 정제 데이터 배열 가공
            mergedDataset = Array.from(dataIntegrator.values()).filter(item => 
                item.timeStr && 
                !isNaN(item.seoulTemp) && 
                !isNaN(item.yangpyeongTemp) && 
                !isNaN(item.powerDemand)
            ).map(item => {
                const parseDate = new Date(item.timeStr);
                return {
                    ...item,
                    dateObj: parseDate,
                    monthVal: parseDate.getMonth() + 1,
                    // 요구사항: 열섬 강도 = 도심 기온 - 교외 기온
                    uhiStrength: item.seoulTemp - item.yangpyeongTemp
                };
            });

            if(mergedDataset.length === 0) {
                throw new Error("결합된 행의 개수가 0개입니다. CSV 내부 포맷 및 매핑 기준 컬럼을 재확인하세요.");
            }

            // 필터 채우기 및 화면 전환
            buildMonthFilter();
            document.getElementById("loading-spinner").style.display = "none";
            document.getElementById("main-content").style.display = "block";

            // 초기 대시보드 업데이트 수행 (여름철 분석 유도가 좋은 7월 기본 배치 선택)
            const selectEl = document.getElementById("month-select");
            if([...selectEl.options].some(o => o.value == "7")) {
                selectEl.value = "7";
            }
            refreshDashboardCharts();

        } catch (error) {
            console.error("Application Load Crash:", error);
            document.getElementById("loading-spinner").style.display = "none";
            document.getElementById("error-banner").style.display = "block";
        }
    }

    // 월 드롭다운 옵션 바인딩
    function buildMonthFilter() {
        const select = document.getElementById("month-select");
        const monthSet = [...new Set(mergedDataset.map(d => d.monthVal))].sort((a,b) => a - b);
        
        monthSet.forEach(m => {
            const opt = document.createElement("option");
            opt.value = m;
            opt.textContent = `${m}월 데이터 시각화`;
            select.appendChild(opt);
        });

        select.addEventListener("change", refreshDashboardCharts);
    }

    // 데이터 리프레시 컨트롤러
    function refreshDashboardCharts() {
        const selectedMonth = parseInt(document.getElementById("month-select").value);
        const activeSubset = mergedDataset.filter(d => d.monthVal === selectedMonth);
        
        // 시간 흐름별 순차 정렬 보장
        activeSubset.sort((a, b) => a.dateObj - b.dateObj);

        // 각각의 그래프 표출 기동
        renderLineTemperature(activeSubset);
        renderLinePower(activeSubset);
        analyzeScatterCorrelation(activeSubset, selectedMonth);
    }

    // 1. 도심·교외 기온과 열섬 강도의 변화 선그래프
    function renderLineTemperature(dataset) {
        const timelines = dataset.map(d => d.timeStr.substring(5, 16)); // MM-DD HH:mm 규격화
        
        if(activeCharts.tempChart) activeCharts.tempChart.destroy();

        const ctx = document.getElementById("tempChart").getContext("2d");
        activeCharts.tempChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timelines,
                datasets: [
                    { label: '도심(서울) 기온 (°C)', data: dataset.map(d => d.seoulTemp), borderColor: '#e53e3e', borderWidth: 1.5, pointRadius: 0, fill: false },
                    { label: '교외(양평) 기온 (°C)', data: dataset.map(d => d.yangpyeongTemp), borderColor: '#3182ce', borderWidth: 1.5, pointRadius: 0, fill: false },
                    { label: '열섬 강도 격차 (°C)', data: dataset.map(d => d.uhiStrength), borderColor: '#ed8936', borderWidth: 1.2, pointRadius: 0, fill: false, borderDash: [4, 4] }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: '시간 흐름에 따른 관측 지점별 기온 및 열섬 강도 추이', font: { size: 14 } },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: { ticks: { maxTicksLimit: 8 }, title: { display: true, text: '관측 시각' } },
                    y: { title: { display: true, text: '기온 및 격차 변동폭 (°C)' } }
                }
            }
        });
    }

    // 2. 시간 또는 날짜에 따른 전력수요 변화 선그래프
    function renderLinePower(dataset) {
        const timelines = dataset.map(d => d.timeStr.substring(5, 16));

        if(activeCharts.powerChart) activeCharts.powerChart.destroy();

        const ctx = document.getElementById("powerChart").getContext("2d");
        activeCharts.powerChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timelines,
                datasets: [{
                    label: '시간별 전력수요량',
                    data: dataset.map(d => d.powerDemand),
                    borderColor: '#319795',
                    backgroundColor: 'rgba(49, 151, 149, 0.08)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: '관측 기간 내 전력수요량 흐름 추이', font: { size: 14 } }
                },
                scales: {
                    x: { ticks: { maxTicksLimit: 8 }, title: { display: true, text: '관측 시각' } },
                    y: { title: { display: true, text: '전력수요 단위 (MWh)' } }
                }
            }
        });
    }

    // 3. 피어슨 상관계수 연산 및 추세선 산점도 매핑
    function analyzeScatterCorrelation(dataset, monthName) {
        const xArr = dataset.map(d => d.uhiStrength);
        const yArr = dataset.map(d => d.powerDemand);
        const count = dataset.length;

        // 통계 기초 대수 연산
        const sumX = xArr.reduce((a, b) => a + b, 0);
        const sumY = yArr.reduce((a, b) => a + b, 0);
        const sumXY = xArr.reduce((acc, x, idx) => acc + (x * yArr[idx]), 0);
        const sumXSquare = xArr.reduce((acc, x) => acc + (x * x), 0);
        const sumYSquare = yArr.reduce((acc, y) => acc + (y * y), 0);

        // 피어슨 r 수식 대입
        const numerator = (count * sumXY) - (sumX * sumY);
        const denominator = Math.sqrt(((count * sumXSquare) - (sumX * sumX)) * ((count * sumYSquare) - (sumY * sumY)));
        
        const rVal = denominator === 0 ? 0 : (numerator / denominator);
        
        // 스탯 표기 반영
        document.getElementById("r-value").textContent = rVal.toFixed(3);

        // 요구사항: 상관계수 부호 크기에 따른 조건부 해석 텍스트 매칭
        let interpString = "";
        const absR = Math.abs(rVal);

        if(absR < 0.2) {
            interpString = "상관관계가 약함 (선형 연관성 미미)";
        } else {
            if(rVal > 0) {
                interpString = absR >= 0.4 ? "뚜렷한 양의 상관관계" : "약한 양의 상관관계";
            } else {
                interpString = absR >= 0.4 ? "뚜렷한 음의 상관관계" : "약한 음의 상관관계";
            }
        }
        document.getElementById("r-interpretation").textContent = interpString;

        // 산점도 객체 배열화
        const pointsData = dataset.map(d => ({ x: d.uhiStrength, y: d.powerDemand }));

        if(activeCharts.scatterChart) activeCharts.scatterChart.destroy();

        const ctx = document.getElementById("scatterChart").getContext("2d");
        activeCharts.scatterChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: '시간별 데이터 산포 구조',
                    data: pointsData,
                    backgroundColor: 'rgba(43, 108, 176, 0.6)',
                    pointRadius: 3.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: '열섬 강도에 따른 전력수요 분산도 및 회귀선 패턴', font: { size: 14 } },
                    // 외부 플러그인을 사용하여 산점도에 1차 추세선 오버레이
                    trendlineLinear: {
                        style: "rgba(221, 107, 32, 0.95)",
                        lineStyle: "solid",
                        width: 2.5
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `열섬강도: ${ctx.parsed.x.toFixed(1)}°C | 전력수요: ${ctx.parsed.y.toLocaleString()} MWh`
                        }
                    }
                },
                scales: {
                    x: { type: 'linear', position: 'bottom', title: { display: true, text: '열섬 강도 (도심 기온 - 교외 기온) (°C)' } },
                    y: { title: { display: true, text: '전력수요량 (MWh)' } }
                }
            }
        });

        // 4. 탐구 결과 요약 바인딩 (임의 왜곡이나 조작이 배제된 실제 연산 통계 지표 정보 기술)
        writeSummaryCard(dataset, monthName, rVal, interpString);
    }

    // 데이터 기반 요약 내용 출력문
    function writeSummaryCard(dataset, month, r, interpretationText) {
        const box = document.getElementById("summary-text-box");
        
        // 실측값 수치화 연산
        const avgUhi = (dataset.reduce((acc, d) => acc + d.uhiStrength, 0) / dataset.length).toFixed(2);
        
        // 최대 열섬 강도가 나타난 데이터 정보 정렬 추출
        const maxUhiPoint = [...dataset].sort((a,b) => b.uhiStrength - a.uhiStrength)[0];
        
        // 최고 도심 기온 시점 추출
        const maxSeoulPoint = [...dataset].sort((a,b) => b.seoulTemp - a.seoulTemp)[0];

        box.innerHTML = `
            <li>선택된 <strong>${month}월</strong> 관측 기간 내 유효 매핑 데이터 수는 총 <strong>${dataset.length}시간</strong> 분량입니다.</li>
            <li>해당 월의 평균적인 도시 열섬 강도는 <strong>${avgUhi} °C</strong> 수준으로 관측되었으며, 가장 격차가 컸던 최고 기록 시점은 <strong>${maxUhiPoint.timeStr}</strong>로 도심과 교외 기온 차이가 최대 <strong>${maxUhiPoint.uhiStrength.toFixed(1)} °C</strong>까지 벌어졌습니다.</li>
            <li>분석 데이터 기간 중 서울 도심의 최고 기온은 <strong>${maxSeoulPoint.timeStr}</strong>에 기록된 <strong>${maxSeoulPoint.seoulTemp.toFixed(1)} °C</strong>이며, 해당 시점의 전력수요는 <strong>${maxSeoulPoint.powerDemand.toLocaleString()} MWh</strong>로 확인됩니다.</li>
            <li>실제 관측값을 통한 통계적 검증 결과, 열섬 강도와 전력수요량 간의 피어슨 상관계수($r$)는 <strong>${r.toFixed(3)}</strong>를 기록하여 최종적으로 <strong>"${interpretationText}"</strong>의 특성을 띠는 것으로 명확히 요약해 볼 수 있습니다.</li>
        `;
    }

    // 도큐먼트 로드 완료 시 구동 개시
    window.addEventListener("DOMContentLoaded", startApplication);
</script>

</body>
</html>
