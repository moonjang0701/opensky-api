# 왜 자꾸 샘플 데이터만 나올까요?

## 🔍 문제 진단

OpenSky API에서 실제 데이터를 가져오려고 시도하지만, **데이터가 없어서** 자동으로 샘플 데이터로 대체됩니다.

### 실제 로그 확인:
```
✅ OpenSky API 연결 (익명 접근)
⏳ 데이터 수집 중...
Fetching data for 2026-02-01T03:11:55... Found 0 aircraft  ← 0대!
Fetching data for 2026-02-01T09:11:55... Found 0 aircraft  ← 0대!

✅ 수집 완료!
   추적된 항공기: 0대                                    ← 데이터 없음!

⚠️  수집된 데이터 없음. 샘플 데이터로 대체합니다.     ← 자동 대체
```

---

## ❓ 왜 데이터가 없을까요?

### 이유 1: 현재 하드코딩된 좌표가 **임시 좌표**
```python
# config/airways.py 현재 설정
'Y711': {
    'waypoints': [
        {'name': 'OLMEN', 'lat': 37.5, 'lon': 126.5},   ← 임시 좌표!
        {'name': 'BULTI', 'lat': 36.5, 'lon': 127.5},   ← 실제 항로 아님
        {'name': 'GIKDO', 'lat': 35.5, 'lon': 128.5},
    ]
}
```
이 좌표들은 **실제 항공로가 아니라 예시 좌표**입니다.

### 이유 2: 시간대 문제
- 현재 시각: 2026-02-02 03:11 (새벽 3시)
- 한국 시간: 새벽 시간대 → 비행기 적음
- 확인: 현재 전 세계 5,919대 추적 중이지만 **한국 주변 0대**

### 이유 3: 미래 날짜
- 수집 날짜: 2026-02-01 ~ 2026-02-02 (미래!)
- OpenSky는 **과거 데이터**만 제공
- 현재(실시간) 또는 과거 날짜를 사용해야 함

---

## ✅ 해결 방법

### 방법 1: 실제 항공로 좌표 사용 (권장) ⭐

실제 인천-제주 항로 좌표로 테스트:

```bash
cd /home/user/webapp/airway_safety_assessment/examples
python configure_airway.py
```

```
항공로 이름: ICN_CJU
설명: 인천-제주 항로

웨이포인트 1:
  이름: RKSI
  위도: 37.4692    ← 인천공항 실제 좌표
  경도: 126.4505

웨이포인트 2:
  이름: RKPC
  위도: 33.5113    ← 제주공항 실제 좌표
  경도: 126.4930
```

그 다음 평가:
```bash
python simple_assessment.py --airway ICN_CJU --days 7
```

### 방법 2: 과거 날짜 사용 (2020년 등)

```bash
# 2020년 데이터 (확실히 과거)
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-01-31
```

### 방법 3: 전 세계 주요 항로로 테스트

**미국 로스앤젤레스 - 뉴욕** (항공기 많음):
```bash
python configure_airway.py
```

```
항공로 이름: LAX_JFK
웨이포인트 1:
  이름: KLAX
  위도: 33.9425
  경도: -118.4081

웨이포인트 2:
  이름: KJFK
  위도: 40.6413
  경도: -73.7781
```

### 방법 4: 샘플 데이터로 알고리즘 테스트 (빠름)

알고리즘이 제대로 작동하는지만 확인:
```bash
python simple_assessment.py --airway Y711 --sample
```

---

## 🧪 실제 데이터 확인 방법

### 1. OpenSky API 직접 테스트

```bash
cd /home/user/webapp
python -c "
import sys
sys.path.insert(0, 'python')
from opensky_api import OpenSkyApi

api = OpenSkyApi()
states = api.get_states()
print(f'현재 추적 중: {len(states.states)}대')

# 특정 지역 확인 (인천-제주)
count = 0
for s in states.states:
    if s.latitude and s.longitude:
        if 33 < s.latitude < 38 and 126 < s.longitude < 127:
            count += 1
            print(f'{s.callsign} at ({s.latitude:.2f}, {s.longitude:.2f}), {s.baro_altitude}m')

print(f'한국 주변: {count}대')
"
```

### 2. 웹에서 확인

OpenSky Network 웹사이트에서 확인:
- https://opensky-network.org/network/explorer
- 실시간 항공기 위치 확인
- 한국 주변에 항공기가 있는지 확인

---

## 📊 데이터 존재 여부 확인

| 조건 | 데이터 존재 | 설명 |
|------|-----------|------|
| 실제 주요 항로 | ✅ | LAX-JFK, LHR-JFK 등 |
| 한국 항로 (낮 시간) | ✅ | 오전 8시~오후 10시 |
| 한국 항로 (새벽) | ❌ | 비행기 적음 |
| 임시 좌표 | ❌ | 실제 항로 아님 |
| 미래 날짜 | ❌ | 데이터 없음 |
| 과거 날짜 (2020년 등) | ✅ | 역사적 데이터 |

---

## 🎯 추천 해결 순서

### Step 1: 과거 날짜로 테스트 (가장 빠름)
```bash
python simple_assessment.py --airway Y711 --start-date 2020-06-01 --end-date 2020-06-07
```

**이유:** 2020년 6월은 확실히 과거이고, 여름 시즌이라 비행기가 많음

### Step 2: 실제 좌표 설정
```bash
python configure_airway.py
```
인천공항 (37.4692, 126.4505) → 제주공항 (33.5113, 126.4930)

### Step 3: 실제 좌표로 평가
```bash
python simple_assessment.py --airway ICN_CJU --start-date 2020-06-01 --end-date 2020-06-30
```

---

## 💡 즉시 확인 방법

### 빠른 확인: 주요 국제 항로 테스트

```bash
# 1. 항로 추가
cd /home/user/webapp/airway_safety_assessment/examples
python -c "
import json
config = {
    'TEST_ROUTE': {
        'name': 'TEST_ROUTE',
        'description': 'Test route with real traffic',
        'waypoints': [
            {'name': 'LAX', 'lat': 33.9425, 'lon': -118.4081},  # Los Angeles
            {'name': 'JFK', 'lat': 40.6413, 'lon': -73.7781}    # New York
        ],
        'separation_nm': 160.0,
        'type': 'parallel',
        'active': True
    }
}
with open('../config/custom_airways.json', 'w') as f:
    json.dump(config, f, indent=2)
print('✅ TEST_ROUTE 생성 완료')
"

# 2. 평가 실행 (2020년 데이터)
python simple_assessment.py --airway TEST_ROUTE --start-date 2020-06-01 --end-date 2020-06-07
```

---

## 🎉 요약

### Q: "자꾸 샘플데이터만 만들어서 하는데 진짜 데이터가 없어서 그런거임?"

### A: **부분적으로 맞습니다!**

**이유:**
1. ❌ 하드코딩된 좌표가 **임시 좌표** (실제 항로 아님)
2. ❌ 현재 시각이 **새벽** (한국 주변 비행기 적음)
3. ❌ 수집 날짜가 **미래** (2026년 - OpenSky는 미래 데이터 없음)

**해결책:**
```bash
# 2020년 과거 데이터로 평가 (즉시 해결!)
python simple_assessment.py --airway Y711 --start-date 2020-06-01 --end-date 2020-06-07
```

또는

```bash
# 실제 좌표로 변경 후 평가
python configure_airway.py  # 인천-제주 실제 좌표 입력
python simple_assessment.py --airway ICN_CJU --start-date 2020-06-01 --end-date 2020-06-30
```

**OpenSky에 실제 데이터는 있습니다! (전 세계 5,919대 추적 중)**
**하지만 현재 설정으로는 데이터를 못 찾는 것입니다.** ✅
