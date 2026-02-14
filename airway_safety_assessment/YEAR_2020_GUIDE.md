# 2020년 데이터로 평가하기

## 🎯 2020년 데이터 사용 방법

### ⭐ 가장 간단한 방법 (2020년 전체)

```bash
cd /home/user/webapp/airway_safety_assessment/examples
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31
```

---

## 📅 날짜 옵션 사용법

### 1. 2020년 전체 평가
```bash
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31
```

### 2. 2020년 1월만 평가
```bash
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-01-31
```

### 3. 2020년 특정 주간 평가
```bash
python simple_assessment.py --airway Y711 --start-date 2020-06-01 --end-date 2020-06-07
```

### 4. 2020년 샘플 데이터로 빠른 테스트
```bash
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31 --sample
```

---

## 💡 실행 예시

### 명령어:
```bash
cd /home/user/webapp/airway_safety_assessment/examples
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31
```

### 출력:
```
╔══════════════════════════════════════════════════════════════════════╗
║           SIMPLE AIRWAY SAFETY ASSESSMENT                            ║
║           간단한 항공로 안전성 평가                                     ║
╚══════════════════════════════════════════════════════════════════════╝

평가 대상: Y711
데이터 소스: OpenSky Network (실제 데이터, 인증 불필요)
수집 기간: 2020-01-01 ~ 2020-12-31                    ← 2020년 데이터!

📍 항공로 정보:
   이름: Y711
   웨이포인트: 3개

✅ OpenSky API 연결 (익명 접근)
📅 기간: 2020-01-01 ~ 2020-12-31                       ← 2020년 확인
🗺️  영역: Lat 34.67-38.33, Lon 125.67-129.33
⏳ 데이터 수집 중... (약 1460개 스냅샷 예상)

✅ 수집 완료!
   스냅샷: 1460개
   추적된 항공기: X,XXX대                              ← 2020년 데이터

🎯 평가 결과
충돌 위험도:  X.XXe-XX
안전 상태:    ✅ 안전
안전 등급:    Excellent

💾 상세 보고서: assessment_Y711_20260202_XXXXXX.txt
```

---

## 🔧 다양한 사용 예시

### 1. 2020년 1분기 (Q1)
```bash
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-03-31
```

### 2. 2020년 상반기
```bash
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-06-30
```

### 3. 2020년 하반기
```bash
python simple_assessment.py --airway Y711 --start-date 2020-07-01 --end-date 2020-12-31
```

### 4. 2020년 vs 2024년 비교
```bash
# 2020년 평가
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31

# 2024년 평가 (최근 데이터)
python simple_assessment.py --airway Y711 --days 365
```

---

## ⏱️ 데이터 수집 시간

| 기간 | 예상 시간 | 스냅샷 수 |
|------|-----------|-----------|
| 1주일 | ~30초 | 28개 |
| 1개월 | ~2분 | 120개 |
| 1분기 (3개월) | ~5분 | 360개 |
| 1년 (2020년 전체) | ~20분 | 1460개 |

**참고:** OpenSky API는 6시간 간격으로 샘플링하므로 1년 = 365일 × 4회 = 1460개 스냅샷

---

## ⚠️ 주의사항

### 1. Rate Limit (익명 접근)
- 하루 ~100 requests 제한
- 1년 데이터 = 1460 requests 필요
- **해결책:** 여러 날에 걸쳐 나눠서 수집하거나 OpenSky 계정 만들기

### 2. 긴 수집 시간
- 1년 데이터는 20분 이상 걸릴 수 있음
- **해결책:** 작은 기간으로 먼저 테스트 (1주일, 1개월)

### 3. 빠른 테스트
```bash
# 샘플 데이터로 빠른 테스트 (1초)
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31 --sample
```

---

## 📋 단계별 가이드

### Step 1: 짧은 기간으로 테스트
```bash
# 2020년 1주일만 (30초)
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-01-07
```

### Step 2: 1개월로 확장
```bash
# 2020년 1월 (2분)
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-01-31
```

### Step 3: 전체 년도 평가
```bash
# 2020년 전체 (20분)
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31
```

---

## 🎯 복사-붙여넣기 명령어

### 2020년 전체 (한 줄)
```bash
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31
```

### 2020년 1월 (빠른 테스트)
```bash
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-01-31
```

### 2020년 샘플 데이터 (즉시)
```bash
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31 --sample
```

---

## ✅ 확인 방법

### 명령어 실행 후 출력에서 확인:
```
수집 기간: 2020-01-01 ~ 2020-12-31  ← 이 부분 확인!
📅 기간: 2020-01-01 ~ 2020-12-31     ← 여기도 확인!
```

---

## 💡 TIP

### 빠르게 테스트하려면:
```bash
# 1. 샘플 데이터로 먼저 확인 (1초)
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31 --sample

# 2. 1주일 실제 데이터로 확인 (30초)
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-01-07

# 3. 전체 년도 평가 (20분)
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31
```

---

## 🎉 요약

### 2020년 데이터로 평가하기:

```bash
python simple_assessment.py --airway Y711 --start-date 2020-01-01 --end-date 2020-12-31
```

**이게 끝!** 🚀
