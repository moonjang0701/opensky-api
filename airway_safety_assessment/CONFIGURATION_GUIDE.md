# 항공로 위치 및 날짜 설정 가이드

## 질문: Y711 평가할 때 위치나 날짜는 어떻게 설정됨?

## 답변: 세 가지 방법으로 설정 가능합니다! 🎯

---

## 방법 1: 대화형 설정 도구 사용 (권장) ⭐

### Step 1: 항공로 설정 도구 실행
```bash
cd airway_safety_assessment/examples
python configure_airway.py
```

### Step 2: 새 항공로 추가
```
메뉴:
  1. 모든 항공로 보기
  2. 새 항공로 추가      ← 선택
  3. 항공로 웨이포인트 편집
  0. 종료

선택 (0-3): 2
```

### Step 3: 항공로 정보 입력
```
항공로 이름 (예: Y711, MY001): Y711
설명 (예: 서울-부산 항공로): 인천-대구-부산 국내선

웨이포인트 입력 (최소 2개 필요):
웨이포인트 1:
  이름 (예: OLMEN): RKSI
  위도 (예: 37.5): 37.4692
  경도 (예: 126.5): 126.4505
  ✅ RKSI 추가됨 (37.4692, 126.4505)

웨이포인트 2:
  이름 (예: OLMEN): DAEGU
  위도 (예: 37.5): 35.8941
  경도 (예: 126.5): 128.6592
  ✅ DAEGU 추가됨 (35.8941, 128.6592)

웨이포인트 3:
  이름 (예: OLMEN): RKPK
  위도 (예: 37.5): 35.1795
  경도 (예: 126.5): 129.0353
  ✅ RKPK 추가됨 (35.1795, 129.0353)

웨이포인트 4:
  이름 (예: OLMEN): [Enter로 종료]

항공로 분리 거리 (nm, 기본값 160): 160

항공로 유형:
  1. parallel (평행)
  2. single (단선)
  3. crossing (교차)
선택 (1-3, 기본값 1): 1

✅ 항공로 'Y711' 생성 완료!
```

### Step 4: 향상된 평가 실행
```bash
python advanced_assessment.py
```

이제 대화형으로:
1. 항공로 선택 (Y711)
2. 평가 구간 선택 (웨이포인트 1-3 또는 전체)
3. 날짜 범위 설정 (최근 7일, 30일, 또는 사용자 지정)
4. 데이터 수집 및 평가

---

## 방법 2: 직접 Python 코드로 설정

### 2-1: 실제 좌표로 평가하기

```python
from airway_safety_assessment import AirwaySafetyAssessment
from airway_safety_assessment.data import OpenSkyClient, BoundingBoxHelper
from datetime import datetime, timedelta

# 1. 실제 Y711 항공로 웨이포인트 정의
# (예시: 인천공항 → 대구 → 김해공항)
waypoints = [
    {'name': 'RKSI', 'lat': 37.4692, 'lon': 126.4505},  # 인천공항
    {'name': 'DAEGU', 'lat': 35.8941, 'lon': 128.6592},  # 대구
    {'name': 'RKPK', 'lat': 35.1795, 'lon': 129.0353}   # 김해공항
]

# 2. Bounding box 생성
waypoint_coords = [(wp['lon'], wp['lat']) for wp in waypoints]
bbox = BoundingBoxHelper.create_route_bbox(waypoint_coords, buffer_nm=50)

print(f"Bounding Box: {bbox}")
# → (min_lat, max_lat, min_lon, max_lon)

# 3. 날짜 범위 설정
end_date = datetime.now()
start_date = end_date - timedelta(days=7)  # 최근 7일

print(f"데이터 수집 기간: {start_date} ~ {end_date}")

# 4. OpenSky에서 실제 데이터 수집
client = OpenSkyClient(username='your_username', password='your_password')

traffic_data = client.collect_route_traffic(
    route_bbox=bbox,
    start_datetime=start_date,
    end_datetime=end_date,
    interval_minutes=360  # 6시간 간격
)

# 5. 안전성 평가
assessment = AirwaySafetyAssessment('Y711')
# ... (데이터 처리 및 평가)
```

### 2-2: 특정 구간만 평가하기

```python
# 웨이포인트 1-2 구간만 평가 (RKSI → DAEGU)
segment_waypoints = waypoints[0:2]  # 인천공항 → 대구

waypoint_coords = [(wp['lon'], wp['lat']) for wp in segment_waypoints]
bbox = BoundingBoxHelper.create_route_bbox(waypoint_coords, buffer_nm=50)

# 데이터 수집 및 평가...
```

### 2-3: 특정 날짜 범위 설정

```python
from datetime import datetime

# 2024년 1월 1일 ~ 1월 31일 데이터
start_date = datetime(2024, 1, 1, 0, 0, 0)
end_date = datetime(2024, 1, 31, 23, 59, 59)

traffic_data = client.collect_route_traffic(
    route_bbox=bbox,
    start_datetime=start_date,
    end_datetime=end_date,
    interval_minutes=360
)
```

---

## 방법 3: JSON 설정 파일 직접 편집

### 파일 위치
```
airway_safety_assessment/config/custom_airways.json
```

### 파일 내용 (예시)
```json
{
  "Y711": {
    "name": "Y711",
    "description": "인천-대구-부산 국내선",
    "waypoints": [
      {
        "name": "RKSI",
        "lat": 37.4692,
        "lon": 126.4505
      },
      {
        "name": "DAEGU",
        "lat": 35.8941,
        "lon": 128.6592
      },
      {
        "name": "RKPK",
        "lat": 35.1795,
        "lon": 129.0353
      }
    ],
    "separation_nm": 160.0,
    "type": "parallel",
    "active": true,
    "created_at": "2024-02-02T10:30:00"
  }
}
```

---

## 실제 사용 예시 💡

### 시나리오: 인천-제주 항공로 평가

#### 1. 항공로 설정
```bash
python configure_airway.py
```

```
항공로 이름: ICN_CJU
설명: 인천-제주 노선

웨이포인트 1:
  이름: RKSI
  위도: 37.4692
  경도: 126.4505

웨이포인트 2:
  이름: JEJU
  위도: 33.5113
  경도: 126.4930

항공로 분리 거리: 160
```

#### 2. 평가 실행
```bash
python advanced_assessment.py
```

대화형 선택:
```
STEP 1: 항공로 선택
→ ICN_CJU 선택

STEP 2: 평가 구간 선택
→ 전체 항공로 평가 (y)

STEP 3: 데이터 수집 기간 설정
→ 최근 30일 선택 (3)

STEP 4: OpenSky Network 인증
→ 실제 데이터 사용 (y)
→ Username: your_opensky_id
→ Password: ********

STEP 5: 데이터 수집 및 평가
→ 자동 실행...
```

#### 3. 결과
```
✅ 데이터 수집 완료!
   스냅샷: 120개
   추적된 항공기: 4,523대

✅ 안전성 평가 완료
   충돌 위험: 2.34e-12 / 비행시간
   안전 여부: ✅ 안전
   안전 수준: Excellent

💾 보고서 저장: assessment_ICN_CJU_full_20240201_103045.txt
```

---

## 좌표 찾는 방법 🗺️

### 방법 1: Google Maps
1. Google Maps에서 위치 검색
2. 우클릭 → "이 위치의 좌표" 복사
3. 형식: 위도, 경도 (예: 37.4692, 126.4505)

### 방법 2: 항공 정보 사이트
- **SkyVector**: https://skyvector.com/
- **FlightAware**: https://flightaware.com/
- **OurAirports**: https://ourairports.com/

### 방법 3: AIP (Aeronautical Information Publication)
- 국토교통부 항공정보포털
- ICAO 웨이포인트 데이터베이스

---

## 설정 파일 우선순위

```
1. custom_airways.json (사용자 정의)
   ↓ 없으면
2. airways.py (기본 설정)
   ↓ 없으면
3. 수동 입력
```

---

## 요약 정리 📋

| 항목 | 설정 방법 |
|------|-----------|
| **항공로 위치** | 1. 대화형 도구로 웨이포인트 입력<br>2. Python 코드로 직접 설정<br>3. JSON 파일 편집 |
| **평가 구간** | 웨이포인트 인덱스 선택 (예: 1-3) |
| **날짜 범위** | 1. 최근 1/7/30일<br>2. 사용자 지정 (YYYY-MM-DD) |
| **데이터 소스** | OpenSky Network (실제) 또는 샘플 데이터 |

---

## 핵심 정리 🎯

**질문: Y711 평가할 때 위치나 날짜는 어떻게 알거나 설정됨?**

**답변:**
1. **위치 설정**: 
   - `configure_airway.py`로 대화형 입력 ✅
   - 또는 `custom_airways.json` 직접 편집
   - 웨이포인트 이름 + 위도/경도 지정

2. **날짜 설정**:
   - `advanced_assessment.py` 실행 시 대화형 선택 ✅
   - 최근 1/7/30일 또는 사용자 지정 날짜
   - Python 코드로 `datetime` 객체 전달

3. **구간 선택**:
   - 전체 항공로 또는 특정 웨이포인트 구간
   - 대화형 메뉴에서 선택 가능

**모든 설정을 사용자가 직접 입력하고 제어할 수 있습니다!** 🚀
