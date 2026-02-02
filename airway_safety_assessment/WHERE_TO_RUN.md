# 실행 위치 및 방법 가이드

## 📍 어디서 실행해야 하나요?

### 현재 프로젝트 위치
```
/home/user/webapp/
├── airway_safety_assessment/    ← 여기가 프로젝트 폴더
│   ├── examples/                 ← 여기서 실행!
│   │   ├── simple_assessment.py     ⭐ 가장 간단
│   │   ├── basic_assessment.py
│   │   └── advanced_assessment.py
│   ├── core/
│   ├── data/
│   └── ...
├── python/                       ← OpenSky API
└── ...
```

---

## 🚀 실행 방법 (3단계)

### 1️⃣ 프로젝트 폴더로 이동
```bash
cd /home/user/webapp/airway_safety_assessment
```

### 2️⃣ examples 폴더로 이동
```bash
cd examples
```

### 3️⃣ 프로그램 실행
```bash
python simple_assessment.py --airway Y711
```

---

## 💡 한 번에 실행 (권장)

### 방법 1: 한 줄로 실행 ⭐
```bash
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y711
```

### 방법 2: 절대 경로 사용
```bash
python /home/user/webapp/airway_safety_assessment/examples/simple_assessment.py --airway Y711
```

---

## 📝 상세 단계별 가이드

### Step 1: 터미널 열기
```bash
# 터미널을 엽니다
```

### Step 2: 프로젝트 위치 확인
```bash
pwd
# 출력: /home/user (또는 다른 위치)
```

### Step 3: 프로젝트로 이동
```bash
cd /home/user/webapp/airway_safety_assessment/examples
```

### Step 4: 위치 확인 (선택사항)
```bash
pwd
# 출력: /home/user/webapp/airway_safety_assessment/examples

ls
# 출력: simple_assessment.py, basic_assessment.py, ...
```

### Step 5: 실행!
```bash
python simple_assessment.py --airway Y711
```

---

## 🎯 실행 가능한 프로그램들

현재 위치: `/home/user/webapp/airway_safety_assessment/examples/`

| 파일 | 난이도 | 설명 | 실행 명령 |
|------|--------|------|-----------|
| `simple_assessment.py` | ⭐ 쉬움 | 가장 간단, 인증 불필요 | `python simple_assessment.py --airway Y711` |
| `basic_assessment.py` | ⭐⭐ 보통 | 대화형 메뉴 | `python basic_assessment.py --interactive` |
| `advanced_assessment.py` | ⭐⭐⭐ 어려움 | 모든 설정 가능 | `python advanced_assessment.py` |
| `configure_airway.py` | ⭐⭐ 보통 | 항공로 설정 | `python configure_airway.py` |
| `realdata_assessment.py` | ⭐⭐ 보통 | 실제 데이터 강조 | `python realdata_assessment.py --airway Y711` |

---

## 💻 복사-붙여넣기 가능한 명령어

### 가장 빠른 실행 (Y711 평가)
```bash
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y711
```

### Y571 평가 (제주-부산)
```bash
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y571
```

### 30일 데이터로 평가
```bash
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y711 --days 30
```

### 빠른 테스트 (샘플 데이터)
```bash
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y711 --sample
```

### 대화형 메뉴
```bash
cd /home/user/webapp/airway_safety_assessment/examples && python basic_assessment.py --interactive
```

---

## 🔧 문제 해결

### 문제 1: "No such file or directory"
```bash
# 해결: 정확한 경로로 이동
cd /home/user/webapp/airway_safety_assessment/examples
```

### 문제 2: "ModuleNotFoundError"
```bash
# 해결: 의존성 설치
cd /home/user/webapp/airway_safety_assessment
pip install -r requirements.txt
```

### 문제 3: "cannot import name 'OpenSkyApi'"
```bash
# 해결: OpenSky API 설치
cd /home/user/webapp
pip install -e python/
```

### 문제 4: 현재 위치를 모르겠어요
```bash
# 현재 위치 확인
pwd

# 프로젝트 폴더로 이동
cd /home/user/webapp/airway_safety_assessment/examples
```

---

## 📊 실행 예시 (전체 과정)

```bash
$ cd /home/user/webapp/airway_safety_assessment/examples
$ pwd
/home/user/webapp/airway_safety_assessment/examples

$ ls
advanced_assessment.py  configure_airway.py  simple_assessment.py
basic_assessment.py     realdata_assessment.py

$ python simple_assessment.py --airway Y711

╔══════════════════════════════════════════════════════════════════════╗
║           SIMPLE AIRWAY SAFETY ASSESSMENT                            ║
║           간단한 항공로 안전성 평가                                     ║
╚══════════════════════════════════════════════════════════════════════╝

평가 대상: Y711
데이터 소스: OpenSky Network (실제 데이터, 인증 불필요)
수집 기간: 최근 7일

✅ OpenSky API 연결 (익명 접근)
⏳ 데이터 수집 중...
✅ 수집 완료!

충돌 위험도:  3.45e-12
안전 상태:    ✅ 안전
안전 등급:    Excellent

💾 상세 보고서: assessment_Y711_20240202_103045.txt

======================================================================
                                평가 완료!                                
======================================================================
```

---

## 🎯 핵심 요약

### Q: 어디서 실행해야 함?

### A: 두 가지 방법

#### 방법 1: 디렉토리 이동 후 실행 ⭐
```bash
cd /home/user/webapp/airway_safety_assessment/examples
python simple_assessment.py --airway Y711
```

#### 방법 2: 절대 경로로 바로 실행
```bash
python /home/user/webapp/airway_safety_assessment/examples/simple_assessment.py --airway Y711
```

---

## 📋 체크리스트

실행 전 확인:
- [ ] 터미널이 열려있나요?
- [ ] 현재 위치를 확인했나요? (`pwd`)
- [ ] examples 폴더로 이동했나요? (`cd /home/user/webapp/airway_safety_assessment/examples`)
- [ ] 파일이 있나요? (`ls`)
- [ ] Python이 설치되어 있나요? (`python --version`)
- [ ] 의존성이 설치되어 있나요? (`pip list | grep numpy`)

실행:
- [ ] `python simple_assessment.py --airway Y711`

---

## 🚀 가장 쉬운 방법 (복사하세요!)

```bash
# 이 명령어를 복사해서 터미널에 붙여넣기!
cd /home/user/webapp/airway_safety_assessment/examples && python simple_assessment.py --airway Y711
```

**끝!** 🎉
