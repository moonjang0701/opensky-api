"""
Simple Airway Safety Assessment - No Configuration Needed
간단한 항공로 안전성 평가 - 설정 없이 바로 실행

Just run: python simple_assessment.py --airway Y711
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from airway_safety_assessment import AirwaySafetyAssessment, get_airway_config
from airway_safety_assessment.data import OpenSkyClient
from airway_safety_assessment.data.opensky_client import BoundingBoxHelper


def simple_assessment(
    airway_name: str = 'Y711',
    use_real_data: bool = True,
    days_back: int = 7
):
    """
    Simple one-command assessment
    간단한 한 줄 평가
    
    Parameters:
    -----------
    airway_name : str
        Airway name (default: Y711)
    use_real_data : bool
        Use real OpenSky data (default: True, NO AUTH NEEDED!)
    days_back : int
        Days of data to collect (default: 7)
    """
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║           SIMPLE AIRWAY SAFETY ASSESSMENT                            ║
║           간단한 항공로 안전성 평가                                     ║
╚══════════════════════════════════════════════════════════════════════╝

평가 대상: {airway_name}
데이터 소스: {'OpenSky Network (실제 데이터, 인증 불필요)' if use_real_data else '샘플 데이터'}
수집 기간: 최근 {days_back}일
    """)
    
    # Get config
    config = get_airway_config(airway_name)
    if not config:
        print(f"❌ '{airway_name}' 항공로를 찾을 수 없습니다.")
        print("\n사용 가능한 항공로: Y711, Y571, Y572, Y579")
        return
    
    waypoints = config.get('waypoints', [])
    print(f"📍 항공로 정보:")
    print(f"   이름: {config.get('name')}")
    print(f"   설명: {config.get('description')}")
    print(f"   웨이포인트: {len(waypoints)}개")
    for i, wp in enumerate(waypoints, 1):
        print(f"      {i}. {wp['name']} ({wp['lat']:.3f}, {wp['lon']:.3f})")
    
    # Collect data
    if use_real_data:
        print(f"\n{'='*70}")
        print("실제 데이터 수집 중... (인증 불필요, 무료)".center(70))
        print(f"{'='*70}\n")
        
        try:
            # Initialize OpenSky API (NO AUTH NEEDED!)
            client = OpenSkyClient()  # ← 인증 없이 사용!
            print("✅ OpenSky API 연결 (익명 접근)")
            
            # Create bounding box
            waypoint_coords = [(wp['lon'], wp['lat']) for wp in waypoints]
            bbox = BoundingBoxHelper.create_route_bbox(waypoint_coords, buffer_nm=50)
            
            # Set date range
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days_back)
            
            print(f"📅 기간: {start_time.strftime('%Y-%m-%d')} ~ {end_time.strftime('%Y-%m-%d')}")
            print(f"🗺️  영역: Lat {bbox[0]:.2f}-{bbox[1]:.2f}, Lon {bbox[2]:.2f}-{bbox[3]:.2f}")
            print(f"\n⏳ 데이터 수집 중... (약 {days_back*4}개 스냅샷 예상)")
            
            # Collect data
            traffic_data = client.collect_route_traffic(
                route_bbox=bbox,
                start_datetime=start_time,
                end_datetime=end_time,
                interval_minutes=360  # 6시간 간격
            )
            
            print(f"\n✅ 수집 완료!")
            print(f"   스냅샷: {len(traffic_data)}개")
            
            # Convert to trajectories
            trajectories = []
            total_aircraft = 0
            
            for snapshot in traffic_data:
                total_aircraft += snapshot['aircraft_count']
                for state in snapshot['states']:
                    if state.get('longitude') and state.get('latitude'):
                        trajectory = {
                            'flight_id': state.get('icao24', 'unknown'),
                            'callsign': state.get('callsign'),
                            'aircraft_type': 'B738',  # Default
                            'longitude': [state['longitude']],
                            'latitude': [state['latitude']],
                            'altitude': [state['altitude']] if state.get('altitude') else [10000],
                            'velocity': [state['velocity']] if state.get('velocity') else [450],
                            'time': [state.get('time_position', snapshot['timestamp'])],
                            'heading': [state.get('heading', 0)]
                        }
                        trajectories.append(trajectory)
            
            print(f"   추적된 항공기: {total_aircraft}대")
            print(f"   처리된 궤적: {len(trajectories)}개")
            
            if len(trajectories) == 0:
                print("\n⚠️  수집된 데이터 없음. 샘플 데이터로 대체합니다.")
                from basic_assessment import generate_sample_trajectories
                trajectories = generate_sample_trajectories(config, num_flights=100)
        
        except Exception as e:
            print(f"\n⚠️  데이터 수집 실패: {e}")
            print("샘플 데이터로 대체합니다...")
            from basic_assessment import generate_sample_trajectories
            trajectories = generate_sample_trajectories(config, num_flights=100)
    
    else:
        print(f"\n{'='*70}")
        print("샘플 데이터 생성 중...".center(70))
        print(f"{'='*70}\n")
        from basic_assessment import generate_sample_trajectories
        trajectories = generate_sample_trajectories(config, num_flights=100)
        print(f"✅ {len(trajectories)}개 샘플 궤적 생성 완료")
    
    # Process and assess
    print(f"\n{'='*70}")
    print("안전성 평가 중...".center(70))
    print(f"{'='*70}\n")
    
    assessment = AirwaySafetyAssessment(airway_name)
    
    try:
        # Process data
        print("⏳ 데이터 처리 중...")
        parameters = assessment.process_trajectory_data(trajectories)
        
        print("✅ 처리 완료:")
        print(f"   분석된 항공기: {parameters['aircraft_count']}대")
        print(f"   통계 모델: {parameters['best_distribution']}")
        print(f"   횡적 중첩 확률: {parameters['Py_Sy']:.6f}")
        print(f"   평균 속도: {parameters['speed_stats']['mean']:.1f} knots")
        
        # Safety assessment
        print(f"\n⏳ 안전성 계산 중...")
        results = assessment.assess_safety(parameters, use_modified=True)
        
        print(f"\n{'='*70}")
        print("🎯 평가 결과".center(70))
        print(f"{'='*70}\n")
        
        risk = results['collision_risk']
        tls = results['TLS']
        safe = results['meets_safety']
        level = results.get('safety_level', 'N/A')
        
        print(f"충돌 위험도:  {risk:.2e} (충돌/비행시간)")
        print(f"안전 기준:    {tls:.2e} (ICAO TLS)")
        print(f"위험 비율:    {risk/tls*100:.2f}% of TLS")
        print(f"\n안전 상태:    {'✅ 안전' if safe else '❌ 위험'}")
        print(f"안전 등급:    {level}")
        print(f"안전 여유:    {(tls - risk):.2e}")
        
        # Generate report
        report = assessment.generate_report()
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"assessment_{airway_name}_{timestamp}.txt"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 상세 보고서: {filename}")
        
    except Exception as e:
        print(f"\n❌ 평가 오류: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Simple Airway Safety Assessment (No auth needed!)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Y711 평가 (실제 데이터, 최근 7일)
  python simple_assessment.py --airway Y711
  
  # 최근 30일 데이터로 평가
  python simple_assessment.py --airway Y711 --days 30
  
  # 샘플 데이터로 빠른 테스트
  python simple_assessment.py --airway Y711 --sample
  
  # 다른 항공로 평가
  python simple_assessment.py --airway Y571
        """
    )
    
    parser.add_argument(
        '--airway',
        type=str,
        default='Y711',
        help='Airway name (Y711, Y571, Y572, Y579)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Days of data to collect (default: 7)'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Use sample data instead of real OpenSky data'
    )
    
    args = parser.parse_args()
    
    simple_assessment(
        airway_name=args.airway,
        use_real_data=not args.sample,
        days_back=args.days
    )
    
    print(f"\n{'='*70}")
    print("평가 완료!".center(70))
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
