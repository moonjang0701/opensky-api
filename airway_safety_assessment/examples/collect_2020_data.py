"""
OpenSky Historical Data Collector for Y711 Route
2020년 Y711 항로 히스토리 데이터 수집기

Uses get_flights_from_interval() for historical data access
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../python'))

from opensky_api import OpenSkyApi
from datetime import datetime, timedelta
import time
import json

# 인증 정보
USERNAME = "wkdguswls022@gmail.com"
PASSWORD = "Fyrk1864!"

# Y711 항로 정보 (BULTI-MANGI)
Y711_WAYPOINTS = {
    'BULTI': {'lat': 36.7228, 'lon': 126.8250},
    'MANGI': {'lat': 35.5031, 'lon': 126.7422}
}

# Bounding box (Y711 주변)
Y711_BBOX = {
    'lat_min': 35.0,
    'lat_max': 37.2,
    'lon_min': 126.2,
    'lon_max': 127.3
}


def collect_2020_flights(start_date='2020-05-01', end_date='2020-05-07'):
    """
    2020년 Y711 영역의 비행 데이터 수집
    
    OpenSky API의 get_flights_from_interval() 사용
    - 최대 2시간 간격으로 제한
    - 인증 필요
    """
    print("="*70)
    print("  2020년 Y711 항로 히스토리 데이터 수집")
    print("="*70)
    print()
    print(f"🔐 OpenSky 인증: {USERNAME}")
    print(f"📅 기간: {start_date} ~ {end_date}")
    print(f"🗺️  Y711: BULTI(36.72, 126.83) - MANGI(35.50, 126.74)")
    print()
    
    # API 초기화
    api = OpenSkyApi(username=USERNAME, password=PASSWORD)
    
    # 날짜 파싱
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    all_flights = []
    current_dt = start_dt
    
    # 2시간씩 나눠서 수집 (API 제약)
    interval_hours = 2
    
    print("⏳ 데이터 수집 시작...")
    print(f"   (2시간 간격으로 나눠서 수집, API 제약)")
    print()
    
    request_count = 0
    
    while current_dt < end_dt:
        interval_end = min(current_dt + timedelta(hours=interval_hours), end_dt)
        
        begin_ts = int(current_dt.timestamp())
        end_ts = int(interval_end.timestamp())
        
        print(f"📡 수집 중: {current_dt.strftime('%Y-%m-%d %H:%M')} ~ {interval_end.strftime('%Y-%m-%d %H:%M')}")
        
        try:
            # get_flights_from_interval() 사용
            flights = api.get_flights_from_interval(begin_ts, end_ts)
            
            if flights:
                # Y711 영역 필터링
                filtered = []
                for flight in flights:
                    # 여기서는 모든 한국 비행을 수집
                    # (정확한 위치 필터링은 나중에)
                    if flight.estDepartureAirport and flight.estArrivalAirport:
                        # 한국 공항 코드 체크 (RK로 시작)
                        if (flight.estDepartureAirport.startswith('RK') or 
                            flight.estArrivalAirport.startswith('RK')):
                            filtered.append({
                                'icao24': flight.icao24,
                                'callsign': flight.callsign,
                                'departure': flight.estDepartureAirport,
                                'arrival': flight.estArrivalAirport,
                                'firstSeen': flight.firstSeen,
                                'lastSeen': flight.lastSeen
                            })
                
                all_flights.extend(filtered)
                print(f"   ✅ 수집: {len(flights)}편, Y711 영역: {len(filtered)}편")
            else:
                print(f"   ⚠️  데이터 없음")
            
            request_count += 1
            
            # Rate limiting (인증 사용자: ~4000 requests/day)
            # 안전하게 10초 대기
            if request_count % 5 == 0:
                print(f"   ⏸️  Rate limit 대기 중... (10초)")
                time.sleep(10)
            else:
                time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            time.sleep(15)  # 오류 시 더 길게 대기
        
        current_dt = interval_end
    
    print()
    print("="*70)
    print(f"✅ 수집 완료!")
    print(f"   총 비행 편수: {len(all_flights)}편")
    print(f"   요청 횟수: {request_count}회")
    print("="*70)
    print()
    
    # 결과 저장
    output_file = f"y711_flights_{start_date}_to_{end_date}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_flights, f, indent=2, ensure_ascii=False)
    
    print(f"💾 저장 완료: {output_file}")
    print()
    
    # 통계 출력
    if all_flights:
        print("📊 수집된 데이터 통계:")
        print(f"   기간: {start_date} ~ {end_date}")
        print(f"   총 비행: {len(all_flights)}편")
        
        # 공항별 통계
        departures = {}
        arrivals = {}
        for flight in all_flights:
            dep = flight['departure']
            arr = flight['arrival']
            departures[dep] = departures.get(dep, 0) + 1
            arrivals[arr] = arrivals.get(arr, 0) + 1
        
        print()
        print("   출발 공항 TOP 5:")
        for airport, count in sorted(departures.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {airport}: {count}편")
        
        print()
        print("   도착 공항 TOP 5:")
        for airport, count in sorted(arrivals.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {airport}: {count}편")
    
    return all_flights


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='2020년 Y711 항로 히스토리 데이터 수집',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 2020년 5월 1-7일 수집
  python collect_2020_data.py --start 2020-05-01 --end 2020-05-07
  
  # 2020년 5월 전체 수집 (시간 소요)
  python collect_2020_data.py --start 2020-05-01 --end 2020-05-31
  
주의:
  - API 제약: 2시간 간격으로 나눠서 수집
  - Rate limit: 10초 대기 (인증 사용자)
  - 7일 수집 예상 시간: 약 10-15분
        """
    )
    
    parser.add_argument('--start', type=str, default='2020-05-01',
                        help='시작 날짜 (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2020-05-07',
                        help='종료 날짜 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 수집 실행
    flights = collect_2020_flights(args.start, args.end)
    
    print()
    print("🎯 다음 단계:")
    print("   1. JSON 파일에서 궤적 데이터 추출")
    print("   2. Y711 항로 근처 비행만 필터링")
    print("   3. 안전성 평가 실행")
    print()
    print("💡 참고:")
    print("   - 수집된 데이터: y711_flights_*.json")
    print("   - 다음: python process_2020_data.py")


if __name__ == '__main__':
    main()
