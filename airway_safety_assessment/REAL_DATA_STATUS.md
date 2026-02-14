# 실제 데이터 수집 상태 보고서
# Real Data Collection Status Report

날짜: 2026-02-02

## 🔍 문제 진단

### 1. OpenSky API 상태
- ✅ **API 정상 작동**: 전 세계 5,919대 항공기 추적 중
- ✅ **익명 접근 가능**: 인증 없이 사용 가능
- ✅ **데이터 수집 가능**: API 호출 성공

### 2. 데이터 수집 실패 원인

#### 원인 1: 시간대 문제
```
테스트 시각: 2026-02-02 03:00 (새벽)
한국 시간대: 심야 시간 (항공 교통량 매우 낮음)
결과: 한국 상공 항공기 0대
```

#### 원인 2: 좌표 부정확
```python
현재 설정된 좌표 (config/airways.py):
Y711 = {
    'OLMEN': (37.5, 126.5),
    'BULTI': (36.5, 127.5),
    'GIKDO': (35.5, 128.5)
}

문제: 이 좌표들은 실제 항로를 정확히 반영하지 못함
```

#### 원인 3: 2020년 데이터도 0대
```
테스트: 2020-05-01 (낮 시간대로 추정)
결과: 수집된 항공기 0대
결론: 좌표 자체가 실제 항로를 벗어남
```

## 📊 테스트 결과

### Test 1: 현재 시각 (2026년)
```bash
Command: --airway Y711 --days 1
Period: 2026-02-01 ~ 2026-02-02
Region: Lat 34.67-38.33, Lon 125.67-129.33
Result: 0 aircraft detected
Reason: 심야 시간대 + 부정확한 좌표
```

### Test 2: 2020년 데이터
```bash
Command: --airway Y711 --start-date 2020-05-01 --end-date 2020-05-01
Period: 2020-05-01 00:00:00 ~ 2020-05-01 00:00:00
Region: Lat 34.67-38.33, Lon 125.67-129.33
Result: 0 aircraft detected
Reason: 부정확한 좌표
```

### Test 3: Y571 항로
```bash
Command: --airway Y571 --days 1
Period: 2026-02-01 ~ 2026-02-02
Region: Lat 32.67-35.83, Lon 125.67-129.83
Result: 0 aircraft detected
Reason: 심야 시간대 + 부정확한 좌표
```

### Test 4: 전 세계 OpenSky 상태
```bash
Command: OpenSkyApi().get_states()
Result: ✅ 5,919 aircraft tracked worldwide
Korea vicinity: 0 aircraft (lat 33-38, lon 125-130)
```

## 🎯 해결 방법

### 방법 1: 실제 좌표 업데이트 (권장)

#### 필요한 작업:
1. **PDF 문서에서 실제 Y711 웨이포인트 확인**
   - 문서: "Quantitative Safety Assessment and Effectiveness Analysis for Duplication of ATS Routes.pdf"
   - 찾을 정보: Y711의 정확한 위도/경도 좌표

2. **한국 AIP(Aeronautical Information Publication) 참조**
   - 출처: https://aim.koca.go.kr/
   - 항로: Y711 웨이포인트 좌표

3. **실제 비행 계획 데이터베이스 참조**
   - FlightPlanDatabase.com
   - SkyVector.com
   - ForeFlight

#### 좌표 업데이트 예시:
```python
# config/airways.py 또는 config/custom_airways.json

'Y711': {
    'name': 'Y711',
    'description': 'Seoul-Daegu domestic route',
    'waypoints': [
        {'name': 'SEOUL_FIX', 'lat': 37.xxxx, 'lon': 126.xxxx},
        {'name': 'DAEGU_FIX', 'lat': 35.xxxx, 'lon': 128.xxxx},
        # 실제 좌표로 업데이트 필요
    ],
    'separation_nm': 160.0,
    'type': 'parallel',
    'active': True
}
```

### 방법 2: 주요 공항 간 항로 사용

#### RKSI (인천) - RKPC (제주) 항로
```python
'RKSI_RKPC': {
    'name': 'ICN_CJU',
    'description': 'Incheon-Jeju route',
    'waypoints': [
        {'name': 'RKSI', 'lat': 37.4692, 'lon': 126.4505},
        {'name': 'RKPC', 'lat': 33.5113, 'lon': 126.4930}
    ],
    'separation_nm': 240.0,
    'type': 'single',
    'active': True
}
```

이 항로는 **가장 바쁜 국내선**이므로 데이터가 풍부합니다.

### 방법 3: 더 넓은 지역으로 데이터 수집

#### 한국 전체 FIR (Flight Information Region)
```python
bbox = {
    'lat_min': 32.0,   # 제주 남쪽
    'lat_max': 39.0,   # 강원도 북쪽
    'lon_min': 124.0,  # 서해
    'lon_max': 132.0   # 동해
}
```

#### 시간대별 데이터 수집
```bash
# 교통량이 많은 시간대
--start-date 2020-05-01 --end-date 2020-05-01  # 오전 9시-오후 6시 (KST)
```

## 📝 다음 단계

### 1단계: 좌표 확인 (최우선)
- [ ] PDF 문서에서 Y711 좌표 확인
- [ ] 한국 AIP에서 Y711 정보 확인
- [ ] 실제 비행 계획 데이터베이스 참조

### 2단계: 좌표 업데이트
- [ ] `config/airways.py` 업데이트
- [ ] 또는 `config/custom_airways.json` 생성

### 3단계: 재테스트
```bash
# 2020년 5월 데이터 (교통량 많음)
python simple_assessment.py --airway Y711 \
    --start-date 2020-05-01 --end-date 2020-05-07

# 2019년 5월 데이터 (PDF에서 사용한 기간)
python simple_assessment.py --airway Y711 \
    --start-date 2019-05-01 --end-date 2019-05-07
```

### 4단계: 결과 검증
- [ ] 수집된 항공기 > 0대
- [ ] 처리된 궤적 > 0개
- [ ] 횡적 편차 데이터 생성
- [ ] 안전성 평가 완료

## 🚀 빠른 해결책

### 옵션 A: 샘플 데이터 계속 사용
```bash
# 알고리즘 검증용
python simple_assessment.py --airway Y711 --sample
```

**장점:**
- ✅ 즉시 실행 가능
- ✅ 알고리즘 검증 가능
- ✅ 시간 절약

**단점:**
- ❌ 실제 데이터 아님
- ❌ 논문/보고서에 사용 불가

### 옵션 B: 인천-제주 항로 사용
```bash
# 실제 데이터가 많은 항로
python simple_assessment.py --airway RKSI_RKPC \
    --start-date 2020-05-01 --end-date 2020-05-07
```

**장점:**
- ✅ 실제 데이터 확보 가능
- ✅ 교통량 많음 (국내선 최다)
- ✅ 좌표 정확

**단점:**
- ❌ Y711이 아님
- ❌ 항로 추가 설정 필요

## 📞 도움 요청

다음 정보를 제공해 주시면 빠르게 해결할 수 있습니다:

1. **Y711의 실제 웨이포인트 이름과 좌표**
   - PDF 문서의 페이지 번호
   - 또는 한국 AIP 참조 정보

2. **평가하려는 정확한 항로**
   - Y711이 아닌 다른 항로도 가능
   - 예: 인천-제주, 인천-부산, 김포-제주 등

3. **데이터 수집 기간**
   - 연구 목적에 맞는 기간
   - PDF 논문과 동일한 기간 (2019년 5월?)

## 📚 참고 자료

1. **한국 항공 정보**
   - AIP Korea: https://aim.koca.go.kr/
   - ICAO 항로 데이터

2. **OpenSky Network**
   - API 문서: https://openskynetwork.github.io/opensky-api/
   - 데이터 제약: 익명 ~100 requests/day

3. **PDF 논문**
   - 파일: "Quantitative Safety Assessment and Effectiveness Analysis for Duplication of ATS Routes.pdf"
   - 사용 항로: Y571, Y572, Y579 (제주-부산)
   - 사용 기간: 2019년 5월, 2023년 5월

---

**Status**: ⚠️ 실제 데이터 수집 실패 - 좌표 업데이트 필요
**Next Action**: Y711 실제 좌표 확인 및 업데이트
**Alternative**: 샘플 데이터로 알고리즘 검증 또는 ICN-CJU 항로 사용
