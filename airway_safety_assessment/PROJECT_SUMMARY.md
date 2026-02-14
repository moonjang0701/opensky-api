# Airway Safety Assessment System - 프로젝트 개요

## 프로젝트 완료 요약

### 개발 완료 일자
2024년 2월 2일

### 프로젝트 설명
OpenSky Network 데이터를 기반으로 항공로(Y711 등)의 안전성을 정량적으로 평가하는 시스템입니다. 
논문 "Quantitative Safety Assessment and Effectiveness Analysis for Duplication of ATS Routes" (Park et al., 2024)의 
Reich Collision Risk Model (CRM)을 구현하였습니다.

## 구현된 주요 기능

### 1. Reich 충돌 위험 모델 (Reich CRM)
- **표준 Reich CRM**: 평행 항공로 충돌 위험 계산
- **수정된 Reich CRM**: 고도 변경을 고려한 충돌 위험 계산
- **ICAO 안전 기준 평가**: TLS (5×10⁻⁹) 대비 안전성 평가

### 2. 통계 분석 엔진
- **확률 분포 피팅**: DE, N, NN, DDE, NDE 모델
- **Maximum Likelihood Estimation (MLE)**: 최적 분포 모델 선택
- **횡적 중첩 확률 계산**: Py(Sy) 수치적 적분
- **횡적 점유율 계산**: 웨이포인트 통과 시간 기반

### 3. ADS-B 데이터 처리
- **OpenSky Network API 연동**: 실시간 항공기 상태 수집
- **궤적 데이터 필터링**: 항공로별 비행 궤적 추출
- **횡적 편차 계산**: 항공로 중심선으로부터의 거리 측정
- **지상 속도 및 고도 분석**: 비행 파라미터 통계 분석

### 4. 항공로 설정 관리
- **다중 항공로 지원**: Y711, Y571, Y572, Y579 설정
- **웨이포인트 관리**: 항공로별 경유지 정의
- **항공로 선택 UI**: 대화형 메뉴 시스템

### 5. 안전성 평가 보고서
- **상세 평가 결과**: 충돌 위험, TLS 준수 여부, 안전 수준
- **파라미터 분석**: 모든 계산 파라미터 상세 표시
- **비교 분석**: 시나리오 간 안전성 비교

## 프로젝트 구조

```
airway_safety_assessment/
├── core/                          # 핵심 알고리즘
│   ├── reich_crm.py              # Reich CRM 구현
│   └── safety_metrics.py         # 안전성 지표 계산
├── data/                          # 데이터 처리
│   ├── opensky_client.py         # OpenSky API 클라이언트
│   └── data_processor.py         # ADS-B 데이터 처리
├── utils/                         # 유틸리티
│   └── statistics.py             # 통계 분석 도구
├── config/                        # 설정
│   └── airways.py                # 항공로 설정
├── examples/                      # 예제 프로그램
│   └── basic_assessment.py       # 기본 평가 예제
├── tests/                         # 단위 테스트
│   ├── test_reich_crm.py         # CRM 테스트
│   └── test_safety_metrics.py    # 안전성 지표 테스트
├── __init__.py                    # 메인 모듈
├── requirements.txt               # 의존성 목록
└── README.md                      # 사용자 문서
```

## 사용 방법

### 1. 항공로 목록 조회
```bash
cd airway_safety_assessment
python examples/basic_assessment.py --list
```

### 2. 특정 항공로 평가
```bash
python examples/basic_assessment.py --airway Y711
```

### 3. 대화형 모드
```bash
python examples/basic_assessment.py --interactive
```

### 4. Python 코드로 사용
```python
from airway_safety_assessment import AirwaySafetyAssessment

# 평가 초기화
assessment = AirwaySafetyAssessment('Y711')

# 궤적 데이터 처리
parameters = assessment.process_trajectory_data(trajectories)

# 안전성 평가
results = assessment.assess_safety(parameters)

# 보고서 생성
print(assessment.generate_report())
```

## 테스트 결과

### 단위 테스트
- **총 테스트**: 17개
- **통과**: 17개 (100%)
- **실패**: 0개

### 테스트 항목
- Reich CRM 초기화 및 계산
- 수정된 Reich CRM (고도 변경 포함)
- 횡적 점유율 계산
- 안전성 지표 계산
- 항공기 제원 계산
- 교통 밀도 분석
- 시나리오 비교

## 실행 예시 결과

### Y711 항공로 평가 결과
```
AIRWAY SAFETY ASSESSMENT REPORT
항공로 안전성 평가 보고서

Airway: Y711
Route Type: parallel
Description: Domestic airway route

Collision Risk: 0.00e+00 per flight hour
Target Level of Safety (TLS): 5.00e-09 per flight hour
Risk Ratio (Risk/TLS): 0.0000

Safety Status: ✓ MEETS SAFETY STANDARD
Safety Level: Excellent
Safety Margin: 5.00e-09
```

## 핵심 알고리즘

### Reich CRM 공식
```
Nay = Py(Sy) × Pz(0) × (λx / Sx) × 
      [ E(same) × { |ΔV|/(2λx) + |ẏ|/(2λy) + |ż|/(2λz) } +
        E(opp) × { 2|V|/(2λx) + |ẏ|/(2λy) + |ż|/(2λz) } ]
```

### 수정된 Reich CRM (고도 변경)
```
Nay = Pi × Py(Sy) × Pz(0) × (λx / Sx) × 
      E(opp) × { 2|V|/(2λx) + |ẏ|/(2λy) + |ż|/(2λz) }
```

## 주요 파라미터

- **Py(Sy)**: 횡적 중첩 확률 (확률 분포 피팅으로 계산)
- **Pz(0)**: 수직 중첩 확률 (0.538, JASMA/BOBASMA 표준값)
- **λx, λy, λz**: 평균 항공기 길이, 날개폭, 높이
- **Sx**: 종적 분리 최소값의 절반 (80 nm)
- **E(same), E(opp)**: 동일/반대 방향 횡적 점유율
- **Pi**: 고도 중첩 발생 비율
- **TLS**: 목표 안전 수준 (5×10⁻⁹ collisions/flight hour)

## 의존성

- **numpy**: 수치 계산
- **scipy**: 과학 계산 및 적분
- **scikit-learn**: 분포 피팅 및 클러스터링
- **pandas**: 데이터 처리 (선택사항)
- **OpenSky API**: ADS-B 데이터 수집

## 향후 개발 계획

### Phase 2
1. **실시간 모니터링**: OpenSky Network에서 실시간 데이터 수집
2. **웹 대시보드**: Flask/Streamlit 기반 시각화 인터페이스
3. **데이터베이스 연동**: 과거 데이터 저장 및 분석
4. **항공기 데이터베이스**: 실제 항공기 제원 DB 연동

### Phase 3
1. **기계 학습 모델**: 위험 예측 모델
2. **다중 항공로 동시 분석**: 네트워크 전체 안전성 평가
3. **API 서버**: RESTful API 제공
4. **모바일 앱**: 실시간 안전성 모니터링

## 기술 스택

- **언어**: Python 3.7+
- **과학 계산**: NumPy, SciPy
- **기계 학습**: scikit-learn
- **데이터 수집**: OpenSky Network API
- **테스팅**: pytest
- **문서화**: Markdown, Docstrings

## 참고 문헌

Park, S., Park, S., & Kim, H. (2024). Quantitative Safety Assessment and Effectiveness Analysis for Duplication of ATS Routes. *Journal of Advanced Navigation Technology*, 28(4), 480-489.

## 라이센스

Academic and research purposes.

## 개발자

Airway Safety Assessment Team

---

**프로젝트 상태**: ✅ Phase 1 완료
**마지막 업데이트**: 2024-02-02
**버전**: 1.0.0
