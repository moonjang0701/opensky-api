# 데이터 소스 및 평가 방식 설명

## ✅ 네, API 항적 데이터를 기반으로 평가됩니다!

프로그램은 **OpenSky Network API의 실제 항공기 ADS-B 항적 데이터**를 기반으로 항공로 안전성을 평가하도록 설계되었습니다.

---

## 📊 두 가지 모드 지원

### 1. 🌐 **Real Data Mode** (실제 데이터 모드) - **권장**

OpenSky Network에서 실제 ADS-B 데이터를 수집하여 평가합니다.

#### 사용 방법:
```bash
# 인증 사용 (권장 - 더 높은 rate limit)
python examples/realdata_assessment.py --airway Y711 --real-data \
  --username YOUR_OPENSKY_USERNAME \
  --password YOUR_OPENSKY_PASSWORD

# 익명 접근 (제한적)
python examples/realdata_assessment.py --airway Y711 --real-data
```

#### 수집되는 데이터:
- ✅ 항공기 위치 (위도, 경도, 고도)
- ✅ 지상 속도 (ground speed)
- ✅ 수직 속도 (vertical rate)
- ✅ 헤딩 (heading)
- ✅ 타임스탬프 (시간 정보)
- ✅ ICAO24 코드 (항공기 식별자)
- ✅ 콜사인 (callsign)

#### 데이터 처리 흐름:
```
OpenSky API
    ↓
실시간/역사적 ADS-B 데이터 수집
    ↓
항공로별 필터링 (bounding box)
    ↓
궤적(trajectory) 추출
    ↓
횡적 편차 계산
    ↓
통계 분석 (분포 피팅)
    ↓
Reich CRM 적용
    ↓
안전성 평가 결과
```

---

### 2. 📈 **Sample Data Mode** (샘플 데이터 모드)

개발/테스트용 시뮬레이션 데이터를 생성하여 평가합니다.

#### 사용 방법:
```bash
python examples/basic_assessment.py --airway Y711
```

#### 생성되는 데이터:
- 웨이포인트를 따라 비행하는 가상 항적
- 정규분포로 횡적 편차 시뮬레이션
- 현실적인 속도 및 고도 변화 모델링

---

## 🔍 실제 데이터 수집 프로세스

### Step 1: Bounding Box 생성
```python
from airway_safety_assessment.data import BoundingBoxHelper

# Y711 항공로의 웨이포인트로부터 bounding box 생성
waypoints = [(126.5, 37.5), (127.5, 36.5), (128.5, 35.5)]
bbox = BoundingBoxHelper.create_route_bbox(waypoints, buffer_nm=50)
# → (min_lat, max_lat, min_lon, max_lon)
```

### Step 2: 데이터 수집
```python
from airway_safety_assessment.data import OpenSkyClient
from datetime import datetime, timedelta

client = OpenSkyClient(username='user', password='pass')

# 최근 7일 데이터 수집
end_time = datetime.now()
start_time = end_time - timedelta(days=7)

traffic_data = client.collect_route_traffic(
    route_bbox=bbox,
    start_datetime=start_time,
    end_datetime=end_time,
    interval_minutes=360  # 6시간 간격 샘플링
)
```

### Step 3: 궤적 데이터 변환
```python
trajectories = []
for snapshot in traffic_data:
    for aircraft_state in snapshot['states']:
        trajectory = {
            'flight_id': aircraft_state['icao24'],
            'longitude': [aircraft_state['longitude']],
            'latitude': [aircraft_state['latitude']],
            'altitude': [aircraft_state['altitude']],
            'velocity': [aircraft_state['velocity']],
            'time': [aircraft_state['time_position']]
        }
        trajectories.append(trajectory)
```

### Step 4: 안전성 평가
```python
from airway_safety_assessment import AirwaySafetyAssessment

assessment = AirwaySafetyAssessment('Y711')

# 궤적 데이터 처리
parameters = assessment.process_trajectory_data(trajectories)

# Reich CRM 적용
results = assessment.assess_safety(parameters)
print(assessment.generate_report())
```

---

## 📋 수집 데이터 예시

### OpenSky API 응답 구조:
```json
{
  "time": 1707005824,
  "states": [
    {
      "icao24": "7c6b2f",
      "callsign": "KAL123  ",
      "origin_country": "Republic of Korea",
      "longitude": 126.8234,
      "latitude": 37.5012,
      "altitude": 10972.8,    // meters
      "velocity": 231.45,     // m/s
      "heading": 186.49,      // degrees
      "vertical_rate": 0.33,  // m/s
      "on_ground": false
    },
    // ... more aircraft
  ]
}
```

### 변환된 궤적 데이터:
```python
trajectory = {
    'flight_id': '7c6b2f',
    'callsign': 'KAL123',
    'aircraft_type': 'B738',  # 추가 조회 필요
    'longitude': [126.8234, 126.8345, 126.8456, ...],
    'latitude': [37.5012, 37.5123, 37.5234, ...],
    'altitude': [10972.8, 10980.5, 10985.3, ...],  # meters
    'velocity': [231.45, 232.12, 231.89, ...],     # m/s
    'time': [1707005824, 1707005834, 1707005844, ...],
    'heading': [186.49, 186.52, 186.48, ...]
}
```

---

## 🎯 평가에 사용되는 주요 파라미터

### 1. 횡적 편차 (Lateral Deviation)
- 항공로 중심선으로부터 항공기의 좌우 거리
- 실제 궤적 데이터에서 계산
- 확률 분포 피팅 (DE, N, NN, DDE, NDE)

### 2. 지상 속도 (Ground Speed)
- 항공기의 평균 속도
- 충돌 확률 계산에 사용
- 실제 velocity 데이터에서 추출

### 3. 고도 변화율 (Altitude Change)
- 고도 변경 시간 비율 (Pi)
- 수정된 Reich CRM에 사용
- 실제 altitude 데이터에서 계산

### 4. 횡적 점유율 (Lateral Occupancy)
- 웨이포인트 통과 시간 기반 계산
- 근접 항공기 쌍(proximate pairs) 분석
- 실제 time 데이터에서 추출

---

## 🔐 OpenSky Network 인증

### 무료 계정 생성:
1. https://opensky-network.org/ 방문
2. "Create Account" 클릭
3. 이메일 인증
4. Username/Password로 API 접근

### Rate Limits:
| 계정 타입 | 시간당 Requests | 동시 요청 |
|----------|----------------|----------|
| Anonymous | ~100 | 1 |
| Registered | ~400 | 2 |
| Academic | 협의 가능 | 협의 가능 |

---

## 💡 실전 사용 예시

### Y711 항공로 실제 데이터 평가:

```bash
# 1. OpenSky 계정으로 로그인하여 최근 7일 데이터 수집
python examples/realdata_assessment.py \
  --airway Y711 \
  --real-data \
  --username your_opensky_username \
  --password your_opensky_password

# 2. 수집된 실제 항적 데이터로 안전성 평가
# → 횡적 편차 계산
# → 분포 피팅
# → Reich CRM 적용
# → 안전성 보고서 생성
```

### 출력 예시:
```
📡 Data Source: OpenSky Network (Real ADS-B Data)
✅ OpenSky API client initialized
📅 Time Range:
   Start: 2024-01-26T00:00:00
   End:   2024-02-02T00:00:00
🔄 Collecting data...
✅ Data collection complete!
   Total snapshots: 28
   Total aircraft tracked: 1,247

✅ Data processing complete:
   Aircraft count: 1,247
   Best distribution: DDE
   Lateral overlap probability: 0.000012
   Average ground speed: 452.34 knots
   Altitude overlap rate: 0.0347

SAFETY ASSESSMENT RESULTS:
Collision Risk: 3.45e-12 per flight hour
Safety Status: ✅ SAFE
Safety Level: Excellent
```

---

## 📌 정리

| 항목 | 설명 |
|-----|-----|
| **데이터 소스** | OpenSky Network API (실제 ADS-B 데이터) |
| **데이터 타입** | 항공기 위치, 속도, 고도, 시간 |
| **수집 방식** | REST API 호출 (인증 권장) |
| **처리 방식** | 항공로별 필터링 → 궤적 추출 → 통계 분석 |
| **평가 방식** | Reich CRM (논문 기반 알고리즘) |
| **결과** | 충돌 위험도 + 안전성 보고서 |

**핵심:** 프로그램은 OpenSky Network의 **실제 항공기 ADS-B 항적 데이터**를 수집하고 분석하여 항공로의 안전성을 정량적으로 평가합니다! ✈️
