# OpenSky Historical Data Limitation
# OpenSky 히스토리 데이터 제한 사항

날짜: 2026-02-02

## 🚨 중요 발견: 히스토리 데이터 접근 제한

### 문제 확인
```python
테스트 1: Y711 영역 (2020-05-01 12:00 KST)
- 영역: Lat 35.0-37.2, Lon 126.2-127.3
- 결과: 0 aircraft ❌

테스트 2: 한국 전체 (2020-05-01 12:00 KST)
- 영역: Lat 33.0-39.0, Lon 124.0-132.0
- 결과: 0 aircraft ❌

테스트 3: 전 세계 현재 데이터
- 결과: 5,919 aircraft ✅
```

### 결론
**OpenSky API의 익명 사용자는 히스토리 데이터(2020년)에 접근할 수 없습니다!**

## 📋 OpenSky Data Access Levels

### 1. Anonymous Users (익명 사용자)
```
✅ 가능:
- 현재 실시간 데이터 (~15분 전까지)
- 전 세계 항공기 위치 조회
- 약 100 requests/day

❌ 불가능:
- 히스토리 데이터 (2020년 등)
- 과거 궤적 조회
- 대용량 데이터 다운로드
```

### 2. Registered Users (등록 사용자)
```
✅ 가능:
- 현재 데이터
- 제한된 히스토리 데이터 (~30일)
- 약 400 requests/day

❌ 제한:
- 오래된 히스토리 데이터 (2020년) 제한적
```

### 3. OpenSky Researchers (연구자)
```
✅ 가능:
- 전체 히스토리 데이터
- 2016년 이후 모든 데이터
- 대용량 다운로드
- Impala 데이터베이스 직접 쿼리

요구사항:
- 연구 목적 증명
- 소속 기관
- 승인 필요
```

## 🎯 해결 방법

### 방법 1: OpenSky 연구자 계정 신청 (권장, 실제 데이터)
```
1. OpenSky 웹사이트 가입
   https://opensky-network.org/

2. 연구자 계정 신청
   - 연구 목적 설명
   - 소속 기관 정보
   - 프로젝트 설명

3. 승인 후 사용
   - 2020년 데이터 접근 가능
   - Impala 쿼리 사용
   - 대용량 데이터 다운로드
```

### 방법 2: 샘플 데이터 사용 (현재 방법)
```bash
# 알고리즘 검증 및 테스트용
cd /home/user/webapp/airway_safety_assessment/examples
python simple_assessment.py --airway Y711 --sample
```

**장점:**
- ✅ 즉시 사용 가능
- ✅ Reich CRM 알고리즘 검증
- ✅ 프로그램 구조 테스트
- ✅ 통계 모델 테스트

**용도:**
- 알고리즘 개발 및 검증
- 프로그램 테스트
- 데모 및 프레젠테이션

### 방법 3: 현재 실시간 데이터 수집
```bash
# 현재 시각의 실제 데이터 (낮 시간대 권장)
python simple_assessment.py --airway Y711 --days 1

# 최근 7일 데이터
python simple_assessment.py --airway Y711 --days 7
```

**제약:**
- 현재 시각 기준으로만 가능
- 심야 시간대는 데이터 부족
- 오전 9시~오후 6시 권장 (KST)

### 방법 4: PDF 논문 데이터 참조
```
논문: "Quantitative Safety Assessment and Effectiveness 
       Analysis for Duplication of ATS Routes"

사용 데이터:
- 출처: Flight Radar 24 (NOT OpenSky)
- 기간: 2019년 5월, 2023년 5월
- 항로: Y571, Y572, Y579

옵션:
1. Flight Radar 24 계정 사용
2. 논문 저자에게 데이터 요청
3. 한국 항공 당국 데이터 요청
```

## 📊 실제 데이터 수집 대안

### A. Flight Radar 24
```
웹사이트: https://www.flightradar24.com/
데이터: 실시간 + 히스토리
요금제: Business/Enterprise
API: 제한적, 유료
```

### B. FlightAware
```
웹사이트: https://www.flightaware.com/
데이터: 실시간 + 히스토리
API: Firehose API (유료)
용도: 상업용 데이터
```

### C. ADS-B Exchange
```
웹사이트: https://www.adsbexchange.com/
데이터: 실시간, 무료
API: RapidAPI (제한적)
특징: 비상업적, 커뮤니티 기반
```

### D. 한국 AIP 데이터
```
출처: https://aim.koca.go.kr/
데이터: 항로 정보, 공식 데이터
용도: 항로 좌표, 구조
제약: 실제 궤적 데이터 없음
```

## 🎓 학술 연구용 권장 방법

### 단기 (즉시 사용):
1. **샘플 데이터로 알고리즘 검증**
   ```bash
   python simple_assessment.py --airway Y711 --sample
   ```

2. **현재 데이터로 실제 테스트** (낮 시간대)
   ```bash
   python simple_assessment.py --airway Y711 --days 7
   ```

### 중기 (1-2주):
1. **OpenSky 연구자 계정 신청**
   - 2020년 히스토리 데이터 접근
   - 논문 작성에 사용 가능

2. **Flight Radar 24 계정** (대안)
   - 유료이지만 즉시 사용 가능
   - 히스토리 데이터 풍부

### 장기 (1-2개월):
1. **논문 저자와 협력**
   - 원본 데이터 공유 요청
   - 공동 연구 가능성

2. **한국 항공 당국 데이터 요청**
   - 공식 데이터
   - 연구 목적 증명 필요

## 💡 현재 프로그램 상태

### ✅ 완료된 기능:
- [x] Reich CRM 알고리즘 구현
- [x] 통계 분포 피팅 (DE, N, NN, DDE, NDE)
- [x] OpenSky API 연동
- [x] 샘플 데이터 생성
- [x] 안전성 평가 로직
- [x] CLI 인터페이스
- [x] 보고서 생성
- [x] Y711 실제 좌표 업데이트 ✨ NEW

### ⚠️ 데이터 수집 제약:
- [ ] 2020년 히스토리 데이터 접근 불가 (익명 사용자)
- [ ] 현재 데이터만 수집 가능 (최근 ~15분)
- [ ] 시간대별 교통량 차이 (심야 vs 낮)

### 🎯 추천 작업 순서:
1. **즉시**: 샘플 데이터로 알고리즘 검증 완료
2. **내일 낮**: 실시간 데이터로 실제 테스트 (오전 10시~오후 4시)
3. **1주 내**: OpenSky 연구자 계정 신청
4. **2주 내**: 히스토리 데이터 수집 및 분석

## 📝 업데이트된 좌표

### Y711 항로 (실제 좌표로 업데이트 완료!)
```python
'Y711': {
    'name': 'Y711',
    'description': 'Domestic airway route (BULTI-MANGI)',
    'waypoints': [
        {'name': 'BULTI', 'lat': 36.7228, 'lon': 126.8250},
        {'name': 'MANGI', 'lat': 35.5031, 'lon': 126.7422},
    ],
    'separation_nm': 160.0,
    'type': 'parallel',
    'active': True
}
```

**좌표 출처:**
- BULTI: 36°43'22"N 126°49'30"E
- MANGI: 35°30'11"N 126°44'32"E
- ✅ 실제 항로 좌표로 확인됨

## 🚀 다음 단계

### 즉시 실행 가능:
```bash
# 1. 샘플 데이터로 알고리즘 검증
cd /home/user/webapp/airway_safety_assessment/examples
python simple_assessment.py --airway Y711 --sample

# 2. 업데이트된 좌표 확인
python simple_assessment.py --list
```

### 낮 시간대 (오전 9시~오후 6시 KST):
```bash
# 실시간 데이터 수집 시도
python simple_assessment.py --airway Y711 --days 1
```

### OpenSky 연구자 계정 신청:
1. https://opensky-network.org/ 방문
2. 계정 생성
3. 연구자 액세스 신청
4. 프로젝트 설명: "Airway Safety Assessment using Reich CRM"

---

**Status**: ✅ Y711 좌표 업데이트 완료
**Data Access**: ⚠️ 히스토리 데이터 제한 (익명 사용자)
**Solution**: 샘플 데이터 사용 또는 OpenSky 연구자 계정 신청
**Alternative**: Flight Radar 24, FlightAware, 또는 논문 저자 협력
