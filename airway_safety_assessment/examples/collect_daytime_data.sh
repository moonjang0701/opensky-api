#!/bin/bash
# Daytime Data Collection Script
# 낮 시간대 자동 데이터 수집 스크립트

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

LOG_FILE="data_collection_$(date +%Y%m%d_%H%M%S).log"

echo "╔══════════════════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║      Y711 낮 시간대 데이터 자동 수집 (OpenSky 인증)                   ║" | tee -a "$LOG_FILE"
echo "╚══════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 현재 시각 확인
CURRENT_HOUR=$(date +%H)
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

echo "⏰ 현재 시각: $CURRENT_TIME" | tee -a "$LOG_FILE"
echo "   시간: ${CURRENT_HOUR}시" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 낮 시간대 체크 (09:00 ~ 18:00 KST)
if [ $CURRENT_HOUR -lt 9 ] || [ $CURRENT_HOUR -gt 18 ]; then
    echo "⚠️  경고: 현재 심야/저녁 시간대입니다" | tee -a "$LOG_FILE"
    echo "   권장 시간: 09:00 ~ 18:00 KST" | tee -a "$LOG_FILE"
    echo "   항공 교통량이 낮아 데이터 수집이 제한적일 수 있습니다" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
fi

# 데이터 수집 실행
echo "🚀 데이터 수집 시작..." | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Python 스크립트 실행
python3 << 'PYTHON_SCRIPT' | tee -a "$LOG_FILE"
import sys
import os
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, '../../python')

from opensky_api import OpenSkyApi
from datetime import datetime, timedelta
import time
import json

USERNAME = "wkdguswls022@gmail.com"
PASSWORD = "Fyrk1864!"

print("🔐 OpenSky 인증 로그인...")
api = OpenSkyApi(username=USERNAME, password=PASSWORD)

# 한국 전체 영역
bbox = (33.0, 39.0, 124.0, 132.0)

print("✅ 인증 완료")
print()

# 1. 현재 실시간 데이터 수집
print("📡 1단계: 실시간 데이터 수집")
print("-" * 70)

try:
    states = api.get_states(bbox=bbox)
    
    if states and states.states:
        count = len(states.states)
        print(f"✅ 수집 성공: {count}대 항공기")
        
        # 저장
        realtime_data = []
        for s in states.states:
            realtime_data.append({
                'icao24': s.icao24,
                'callsign': s.callsign,
                'latitude': s.latitude,
                'longitude': s.longitude,
                'altitude': s.baro_altitude,
                'velocity': s.velocity,
                'heading': s.true_track,
                'timestamp': states.time
            })
        
        filename = f"realtime_korea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(realtime_data, f, indent=2)
        
        print(f"💾 저장: {filename}")
        
        # Y711 영역 필터링
        y711_count = sum(1 for s in states.states 
                        if s.latitude and s.longitude and
                        35 <= s.latitude <= 37.2 and 
                        126.2 <= s.longitude <= 127.3)
        print(f"🎯 Y711 영역: {y711_count}대")
        
    else:
        print("⚠️  현재 데이터 없음")
        
except Exception as e:
    print(f"❌ 오류: {e}")

print()
time.sleep(5)

# 2. 최근 2시간 비행 데이터 수집
print("📡 2단계: 최근 2시간 비행 데이터")
print("-" * 70)

now = datetime.now()
start = now - timedelta(hours=2)
begin_ts = int(start.timestamp())
end_ts = int(now.timestamp())

try:
    flights = api.get_flights_from_interval(begin_ts, end_ts)
    
    if flights:
        count = len(flights)
        print(f"✅ 수집 성공: {count}편")
        
        # 한국 관련 비행만 필터링
        korea_flights = []
        for f in flights:
            if f.estDepartureAirport and f.estArrivalAirport:
                if (f.estDepartureAirport.startswith('RK') or 
                    f.estArrivalAirport.startswith('RK')):
                    korea_flights.append({
                        'icao24': f.icao24,
                        'callsign': f.callsign,
                        'departure': f.estDepartureAirport,
                        'arrival': f.estArrivalAirport,
                        'firstSeen': f.firstSeen,
                        'lastSeen': f.lastSeen
                    })
        
        print(f"🇰🇷 한국 관련: {len(korea_flights)}편")
        
        if korea_flights:
            filename = f"korea_flights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(korea_flights, f, indent=2)
            print(f"💾 저장: {filename}")
            
            # 샘플 출력
            print()
            print("샘플 (최대 5편):")
            for i, f in enumerate(korea_flights[:5]):
                print(f"  {i+1}. {f['callsign']:10s} {f['departure']} → {f['arrival']}")
    else:
        print("⚠️  최근 2시간 데이터 없음")
        
except Exception as e:
    print(f"❌ 오류: {e}")

print()
print("=" * 70)
print("✅ 데이터 수집 완료")
print()

PYTHON_SCRIPT

echo "" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "📊 수집 결과" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 수집된 파일 목록
echo "📁 수집된 파일:" | tee -a "$LOG_FILE"
ls -lh realtime_korea_*.json korea_flights_*.json 2>/dev/null | tail -5 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "💾 로그 파일: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "💡 다음 단계:" | tee -a "$LOG_FILE"
echo "   1. 수집된 JSON 파일 확인" | tee -a "$LOG_FILE"
echo "   2. 데이터가 있으면 안전성 평가 실행" | tee -a "$LOG_FILE"
echo "   3. 데이터가 없으면 낮 시간대에 재시도" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Cron 설정 가이드
echo "⏰ Cron 자동 실행 설정 (선택사항):" | tee -a "$LOG_FILE"
echo "   매일 오후 2시 자동 실행:" | tee -a "$LOG_FILE"
echo "   0 14 * * * cd $SCRIPT_DIR && ./collect_daytime_data.sh" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
