# 간단 사용 가이드 (Quick Start)

## 🚀 가장 빠른 시작 방법

### 1️⃣ 설치 (1분)

```bash
cd airway_safety_assessment
pip install -r requirements.txt
```

### 2️⃣ 바로 실행 (인증 불필요!) ⭐

```bash
cd examples
python simple_assessment.py --airway Y711
```

**끝!** 그냥 이것만 실행하면 됩니다! 🎉

---

## 💡 OpenSky API 인증이 필요한가요?

### ❌ **아니요! 필요 없습니다.**

- OpenSky Network는 **무료 익명 접근** 제공
- 아이디/비밀번호 없이 바로 사용 가능
- 하루 제한: 약 ~100 requests (충분함)

### ✅ 인증 없이 바로 사용:

```python
from opensky_api import OpenSkyApi

# 인증 없이 생성
api = OpenSkyApi()  # ← 이게 끝!

# 데이터 바로 가져오기
states = api.get_states()
print(f"현재 추적 중: {len(states.states)}대")
```

### 🔐 인증이 필요한 경우 (선택사항):

- 더 많은 데이터가 필요할 때
- Rate limit을 높이고 싶을 때
- 하루 ~400 requests 이상 필요할 때

```python
# 선택사항: 더 높은 rate limit
api = OpenSkyApi(username='your_id', password='your_pw')
```

**하지만 대부분의 경우 인증 없이도 충분합니다!**

---

## 📋 사용 방법

### 기본 사용 (하드코딩된 설정 사용)

```bash
# Y711 평가 (실제 OpenSky 데이터, 최근 7일)
python simple_assessment.py --airway Y711

# Y571 평가 (제주-부산)
python simple_assessment.py --airway Y571

# 최근 30일 데이터로 평가
python simple_assessment.py --airway Y711 --days 30

# 빠른 테스트 (샘플 데이터)
python simple_assessment.py --airway Y711 --sample
```

### 출력 예시

```
╔══════════════════════════════════════════════════════════════════════╗
║           SIMPLE AIRWAY SAFETY ASSESSMENT                            ║
║           간단한 항공로 안전성 평가                                     ║
╚══════════════════════════════════════════════════════════════════════╝

평가 대상: Y711
데이터 소스: OpenSky Network (실제 데이터, 인증 불필요)
수집 기간: 최근 7일

📍 항공로 정보:
   이름: Y711
   설명: Domestic airway route
   웨이포인트: 3개

✅ OpenSky API 연결 (익명 접근)
📅 기간: 2024-01-26 ~ 2024-02-02
⏳ 데이터 수집 중...

✅ 수집 완료!
   스냅샷: 28개
   추적된 항공기: 1,247대

✅ 처리 완료:
   분석된 항공기: 1,247대
   횡적 중첩 확률: 0.000012
   평균 속도: 452.3 knots

======================================================================
                               🎯 평가 결과                                
======================================================================

충돌 위험도:  3.45e-12 (충돌/비행시간)
안전 기준:    5.00e-09 (ICAO TLS)
위험 비율:    0.07% of TLS

안전 상태:    ✅ 안전
안전 등급:    Excellent
안전 여유:    4.66e-09

💾 상세 보고서: assessment_Y711_20240202_103045.txt
```

---

## 🎯 3가지 사용 모드

### 1. 간단 모드 (권장) ⭐

```bash
python simple_assessment.py --airway Y711
```

- ✅ 하드코딩된 항공로 사용
- ✅ 인증 불필요
- ✅ 한 줄로 실행

### 2. 대화형 모드 (설정이 필요한 경우)

```bash
python advanced_assessment.py
```

- 항공로 위치 직접 입력
- 날짜 범위 선택
- 구간 선택

### 3. 항공로 설정 모드

```bash
python configure_airway.py
```

- 새 항공로 추가
- 웨이포인트 편집
- JSON 설정 파일 생성

---

## 📊 현재 하드코딩된 항공로

| 항공로 | 설명 | 웨이포인트 |
|--------|------|-----------|
| Y711 | Domestic airway | OLMEN, BULTI, GIKDO |
| Y571 | Jeju-Busan (Busan dir) | AKPON, ANROD |
| Y572 | Jeju-Busan (Jeju dir) | UPGOS, ENGOT |
| Y579 | Jeju-Busan (old) | MAKET, TOPAX |

**바로 사용 가능!**

---

## ❓ FAQ

### Q: OpenSky 계정이 필요한가요?
**A: 아니요!** 익명으로 바로 사용 가능합니다.

### Q: 하드코딩된 위치를 바꾸고 싶어요
**A:** 두 가지 방법:
1. `configure_airway.py` 실행 (대화형)
2. `config/custom_airways.json` 직접 편집

### Q: 날짜를 바꾸고 싶어요
**A:** `--days` 옵션 사용
```bash
python simple_assessment.py --airway Y711 --days 30
```

### Q: Rate limit에 걸렸어요
**A:** 세 가지 해결 방법:
1. 잠시 기다리기 (10분)
2. `--sample` 옵션으로 샘플 데이터 사용
3. OpenSky 계정 만들기 (무료)

### Q: 실제 Y711 좌표가 틀린데요?
**A:** 현재는 예시 좌표입니다. 실제 좌표로 바꾸려면:
```bash
python configure_airway.py
→ Y711 선택
→ 웨이포인트 편집
→ 실제 좌표 입력
```

---

## 🎉 요약

### 최소한의 단계:

```bash
# 1. 설치
pip install -r requirements.txt

# 2. 실행 (인증 불필요!)
python simple_assessment.py --airway Y711

# 끝!
```

**그냥 이것만 하면 됩니다!** 🚀

---

## 📚 추가 문서

더 자세한 내용은:
- `README.md` - 전체 문서
- `CONFIGURATION_GUIDE.md` - 설정 가이드
- `DATA_SOURCE_GUIDE.md` - 데이터 소스 가이드
