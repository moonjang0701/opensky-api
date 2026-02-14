# 빠른 시작 (5분 안에!) ⚡

## 📍 실행 위치

```bash
/home/user/webapp/airway_safety_assessment/examples/
```

## 🚀 실행 방법 (3단계)

### 1️⃣ 폴더로 이동
```bash
cd /home/user/webapp/airway_safety_assessment/examples
```

### 2️⃣ 프로그램 실행
```bash
python simple_assessment.py --airway Y711
```

### 3️⃣ 끝! 🎉

---

## 💻 한 줄로 실행 (복사-붙여넣기) ⭐

```bash
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y711
```

---

## 📊 실행 예시

```bash
$ cd /home/user/webapp/airway_safety_assessment/examples
$ python simple_assessment.py --airway Y711

╔══════════════════════════════════════════════════════════════════════╗
║           SIMPLE AIRWAY SAFETY ASSESSMENT                            ║
╚══════════════════════════════════════════════════════════════════════╝

평가 대상: Y711
데이터 소스: OpenSky Network (인증 불필요)
수집 기간: 최근 7일

✅ OpenSky API 연결 (익명 접근)
✅ 수집 완료! 추적된 항공기: 1,247대

🎯 평가 결과
충돌 위험도:  3.45e-12
안전 상태:    ✅ 안전
안전 등급:    Excellent

💾 상세 보고서: assessment_Y711_20240202_103045.txt
```

---

## 🎯 다른 옵션

```bash
# Y571 평가
python simple_assessment.py --airway Y571

# 30일 데이터
python simple_assessment.py --airway Y711 --days 30

# 빠른 테스트
python simple_assessment.py --airway Y711 --sample
```

---

## ❓ 자주 묻는 질문

### Q: OpenSky 계정 필요한가요?
**A: 아니요!** 익명으로 바로 사용 가능

### Q: 어디서 실행하나요?
**A:** `/home/user/webapp/airway_safety_assessment/examples/` 폴더에서

### Q: 설치가 필요한가요?
**A: 네**, 한 번만:
```bash
cd /home/user/webapp/airway_safety_assessment
pip install -r requirements.txt
```

---

## 📚 더 자세한 문서

- `WHERE_TO_RUN.md` - 실행 위치 상세 가이드
- `QUICK_START.md` - 빠른 시작 가이드
- `README.md` - 전체 문서

---

**가장 간단한 방법: 위의 한 줄 명령어를 복사해서 실행!** ⚡
