# Airway Safety Assessment System
# 항공로 안전성 평가 시스템

A quantitative safety assessment system for air traffic service (ATS) routes based on the Reich Collision Risk Model (CRM) and ADS-B flight data.

## Overview

This system implements the methodology described in the research paper:
**"Quantitative Safety Assessment and Effectiveness Analysis for Duplication of ATS Routes"** (Park et al., 2024)

### Key Features

- **Reich Collision Risk Model (CRM)**: Standard and modified implementations
- **Statistical Analysis**: Multiple probability distribution fitting (DE, N, NN, DDE, NDE)
- **ADS-B Data Integration**: OpenSky Network API support
- **Configurable Airways**: Easy configuration for different routes
- **Comprehensive Reporting**: Detailed safety assessment reports

## Installation

### 1. Prerequisites

```bash
python >= 3.7
```

### 2. Install Dependencies

```bash
cd airway_safety_assessment
pip install -r requirements.txt
```

### 3. Install OpenSky API

```bash
cd /path/to/opensky-api
pip install -e python/
```

## Project Structure

```
airway_safety_assessment/
├── core/
│   ├── reich_crm.py          # Reich CRM implementations
│   └── safety_metrics.py     # Safety metrics calculations
├── data/
│   ├── opensky_client.py     # OpenSky Network API client
│   └── data_processor.py     # ADS-B data processing
├── utils/
│   └── statistics.py         # Statistical analysis tools
├── config/
│   └── airways.py            # Airway configurations
├── examples/
│   └── basic_assessment.py   # Example usage
├── tests/
│   └── test_*.py             # Unit tests
└── requirements.txt
```

## Quick Start

### Example 1: Use Sample Data (Demo)

```bash
cd examples
python basic_assessment.py --airway Y711
```

### Example 2: Use Real OpenSky Network Data ⭐

```bash
# With authentication (recommended - better rate limits)
python realdata_assessment.py --airway Y711 --real-data \
  --username YOUR_USERNAME --password YOUR_PASSWORD

# Without authentication (limited rate)
python realdata_assessment.py --airway Y711 --real-data
```

### Example 3: Python Code with Real Data

```python
from airway_safety_assessment import AirwaySafetyAssessment
from airway_safety_assessment.data import OpenSkyClient, BoundingBoxHelper

# Initialize OpenSky client
client = OpenSkyClient(username='your_username', password='your_password')

# Define route bounding box
waypoints = [(126.5, 37.5), (127.5, 36.5)]  # (lon, lat)
bbox = BoundingBoxHelper.create_route_bbox(waypoints, buffer_nm=50)

# Collect real ADS-B data
from datetime import datetime, timedelta
end_time = datetime.now()
start_time = end_time - timedelta(days=7)

traffic = client.collect_route_traffic(
    route_bbox=bbox,
    start_datetime=start_time,
    end_datetime=end_time,
    interval_minutes=360
)

# Process and assess
assessment = AirwaySafetyAssessment('Y711')
parameters = assessment.process_trajectory_data(trajectories)
results = assessment.assess_safety(parameters)

print(assessment.generate_report())
```

### Example 4: Interactive Demo

```bash
python basic_assessment.py --interactive
```

### Example 5: List Available Airways

```bash
python basic_assessment.py --list
```

## Configuration

### Adding New Airways

Edit `config/airways.py`:

```python
KOREAN_AIRWAYS = {
    'Y711': {
        'name': 'Y711',
        'description': 'Your route description',
        'waypoints': [
            {'name': 'WPT1', 'lat': 37.5, 'lon': 126.5},
            {'name': 'WPT2', 'lat': 36.5, 'lon': 127.5},
        ],
        'separation_nm': 160.0,
        'type': 'parallel',
        'active': True
    }
}
```

## Reich CRM Methodology

### Standard Reich Model

Calculates collision risk for parallel routes:

```
Nay = Py(Sy) × Pz(0) × (λx / Sx) × 
      [ E(same) × { |ΔV|/(2λx) + |ẏ|/(2λy) + |ż|/(2λz) } +
        E(opp) × { 2|V|/(2λx) + |ẏ|/(2λy) + |ż|/(2λz) } ]
```

### Modified Reich Model (with Altitude Changes)

Accounts for altitude changes during flight:

```
Nay = Pi × Py(Sy) × Pz(0) × (λx / Sx) × 
      E(opp) × { 2|V|/(2λx) + |ẏ|/(2λy) + |ż|/(2λz) }
```

### Parameters

- **Py(Sy)**: Lateral overlap probability
- **Pz(0)**: Vertical overlap probability (default: 0.538 from JASMA/BOBASMA)
- **λx, λy, λz**: Average aircraft dimensions
- **Sx**: Half of longitudinal separation
- **E(same), E(opp)**: Lateral occupancy
- **Pi**: Altitude overlap occurrence rate
- **TLS**: Target Level of Safety = 5×10⁻⁹ collisions per flight hour

## Data Sources

### 1. OpenSky Network (Real ADS-B Data) ⭐ **Recommended**

실제 항공기 ADS-B 데이터를 사용하여 정확한 안전성 평가를 수행합니다.

**장점:**
- ✅ 실제 비행 궤적 데이터
- ✅ 정확한 안전성 평가
- ✅ 역사적 데이터 분석 가능
- ✅ 실시간 모니터링 가능

**사용 방법:**
```python
from airway_safety_assessment.data import OpenSkyClient

# Initialize client (authentication recommended for better rate limits)
client = OpenSkyClient(username='your_username', password='your_password')

# Collect data for route
bbox = (min_lat, max_lat, min_lon, max_lon)
traffic = client.collect_route_traffic(bbox, start_date, end_date)
```

**OpenSky Network 가입:**
- Website: https://opensky-network.org/
- Free account: 익명 접근 가능 (제한된 rate limit)
- Registered account: 더 높은 rate limit, 더 많은 데이터 접근

**Rate Limits:**
- Anonymous: 매우 제한적 (시간당 ~100 requests)
- Registered: 시간당 ~400 requests
- Academic/Research: 추가 접근 권한 신청 가능

### 2. Sample Data (Simulation)

개발 및 테스트를 위한 시뮬레이션 데이터입니다.

**장점:**
- ✅ 빠른 테스트
- ✅ API 인증 불필요
- ✅ 일관된 결과

**단점:**
- ⚠️ 실제 데이터 아님
- ⚠️ 제한된 현실성

**사용 방법:**
```python
from airway_safety_assessment.examples.basic_assessment import generate_sample_trajectories

# Generate 100 sample flights
trajectories = generate_sample_trajectories(config, num_flights=100)
```

### 3. Alternative Data Sources (향후 지원 예정)

- **FlightRadar24**: 실시간 항공기 추적 (원 논문에서 사용)
- **ADS-B Exchange**: 크라우드소싱 ADS-B 데이터
- **Local ADS-B Receivers**: 자체 ADS-B 수신기 데이터
- **Historical Flight Archives**: 과거 비행 데이터 아카이브

## Safety Assessment Workflow

1. **Data Collection**: Gather ADS-B trajectory data
2. **Data Processing**: Extract parameters (deviations, speeds, aircraft types)
3. **Statistical Analysis**: Fit probability distributions
4. **CRM Calculation**: Compute collision risk
5. **Evaluation**: Compare against TLS (5×10⁻⁹)
6. **Reporting**: Generate comprehensive assessment report

## Testing

Run unit tests:

```bash
cd tests
pytest
```

Run with coverage:

```bash
pytest --cov=airway_safety_assessment
```

## References

**Primary Reference:**
Park, S., Park, S., & Kim, H. (2024). Quantitative Safety Assessment and Effectiveness Analysis for Duplication of ATS Routes. *Journal of Advanced Navigation Technology*, 28(4), 480-489.

**Key Methodology:**
- Reich Collision Risk Model
- Maximum Likelihood Estimation for distribution fitting
- Direct estimation from waypoint crossing for lateral occupancy
- ICAO safety standards (TLS = 5×10⁻⁹)

## License

This project is developed for academic and research purposes based on publicly available research methodology.

## Authors

Airway Safety Assessment Team

Based on research by:
- Park, Se-eun (Republic of Korea Air Force Academy)
- Park, Sun-min (Korea Aerospace University)
- Kim, Hui-yang (Korea Aerospace University)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For questions or issues, please open an issue on the GitHub repository.

---

**Note**: This is the initial version (1.0.0) focusing on the core Reich CRM algorithm implementation. Future versions will include:
- Enhanced OpenSky Network integration
- Real-time monitoring capabilities
- Web-based dashboard
- Additional safety metrics
- Comparative analysis tools
