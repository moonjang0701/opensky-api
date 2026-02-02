"""
Advanced Airway Safety Assessment
향상된 항공로 안전성 평가

Features:
- Custom airway configuration
- User-defined date ranges
- Route segment selection
- Interactive waypoint selection
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from airway_safety_assessment import AirwaySafetyAssessment, get_airway_config
from airway_safety_assessment.data import OpenSkyClient, BoundingBoxHelper
from configure_airway import AirwayConfigurator


def collect_data_with_config(
    airway_name: str,
    segment: tuple = None,
    date_range: tuple = None,
    username: str = None,
    password: str = None
):
    """
    Collect data with user configuration
    
    Parameters:
    -----------
    airway_name : str
        Name of airway
    segment : tuple, optional
        (start_wp_index, end_wp_index) for route segment
    date_range : tuple, optional
        (start_datetime, end_datetime)
    username : str, optional
        OpenSky username
    password : str, optional
        OpenSky password
    
    Returns:
    --------
    list : Trajectory data
    """
    print(f"\n{'='*70}")
    print(f"DATA COLLECTION: {airway_name}".center(70))
    print(f"{'='*70}\n")
    
    # Get airway config
    config = get_airway_config(airway_name)
    if not config:
        print(f"❌ 항공로 '{airway_name}'을(를) 찾을 수 없습니다.")
        print("💡 'python configure_airway.py'로 항공로를 먼저 설정하세요.")
        return []
    
    # Extract waypoints for segment
    waypoints = config.get('waypoints', [])
    if segment:
        start_idx, end_idx = segment
        waypoints = waypoints[start_idx:end_idx+1]
        print(f"📍 선택된 구간: {waypoints[0]['name']} → {waypoints[-1]['name']}")
    else:
        print(f"📍 전체 항공로: {waypoints[0]['name']} → {waypoints[-1]['name']}")
    
    print(f"   웨이포인트 {len(waypoints)}개")
    
    # Set date range
    if not date_range:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        date_range = (start_time, end_time)
    
    start_time, end_time = date_range
    days = (end_time - start_time).days
    
    print(f"\n📅 데이터 수집 기간:")
    print(f"   시작: {start_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   종료: {end_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   기간: {days}일")
    
    # Create bounding box
    waypoint_coords = [(wp['lon'], wp['lat']) for wp in waypoints]
    bbox = BoundingBoxHelper.create_route_bbox(waypoint_coords, buffer_nm=50)
    
    print(f"\n🗺️  Bounding Box:")
    print(f"   Min Lat: {bbox[0]:.4f}, Max Lat: {bbox[1]:.4f}")
    print(f"   Min Lon: {bbox[2]:.4f}, Max Lon: {bbox[3]:.4f}")
    
    # Initialize OpenSky client
    try:
        client = OpenSkyClient(username=username, password=password)
        print("\n✅ OpenSky API 클라이언트 초기화 완료")
        
        if username:
            print(f"   인증 사용자: {username}")
        else:
            print("   ⚠️  익명 접근 (제한된 rate limit)")
    
    except Exception as e:
        print(f"\n❌ OpenSky 클라이언트 초기화 실패: {e}")
        print("\n💡 샘플 데이터로 대체합니다...")
        from basic_assessment import generate_sample_trajectories
        return generate_sample_trajectories(config, num_flights=100)
    
    # Collect data
    print(f"\n🔄 데이터 수집 중...")
    print(f"   샘플링 간격: 6시간")
    print(f"   예상 스냅샷: {days * 4}개")
    
    try:
        traffic_data = client.collect_route_traffic(
            route_bbox=bbox,
            start_datetime=start_time,
            end_datetime=end_time,
            interval_minutes=360  # 6 hours
        )
        
        print(f"\n✅ 데이터 수집 완료!")
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
                        'aircraft_type': 'unknown',
                        'longitude': [state['longitude']],
                        'latitude': [state['latitude']],
                        'altitude': [state['altitude']] if state.get('altitude') else [0],
                        'velocity': [state['velocity']] if state.get('velocity') else [0],
                        'time': [state['time_position']] if state.get('time_position') else [snapshot['timestamp']],
                        'heading': [state['heading']] if state.get('heading') else [0]
                    }
                    trajectories.append(trajectory)
        
        print(f"   추적된 항공기: {total_aircraft}대")
        print(f"   변환된 궤적: {len(trajectories)}개")
        
        return trajectories
        
    except Exception as e:
        print(f"\n❌ 데이터 수집 오류: {e}")
        print("\n💡 샘플 데이터로 대체합니다...")
        from basic_assessment import generate_sample_trajectories
        return generate_sample_trajectories(config, num_flights=100)


def run_advanced_assessment():
    """Run advanced assessment with user configuration"""
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║      ADVANCED AIRWAY SAFETY ASSESSMENT SYSTEM v1.1                   ║
║      향상된 항공로 안전성 평가 시스템                                   ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    configurator = AirwayConfigurator()
    
    # Step 1: Select or configure airway
    print("\n" + "="*70)
    print("STEP 1: 항공로 선택".center(70))
    print("="*70 + "\n")
    
    configurator.list_all_airways()
    
    print("\n옵션:")
    print("  1. 기존 항공로 선택")
    print("  2. 새 항공로 추가")
    
    choice = input("\n선택 (1-2): ").strip()
    
    if choice == '2':
        configurator.add_new_airway()
        configurator.list_all_airways()
    
    airway_name = input("\n평가할 항공로 이름: ").strip().upper()
    
    config = get_airway_config(airway_name)
    if not config:
        print(f"❌ '{airway_name}' 항공로를 찾을 수 없습니다.")
        return
    
    configurator.display_airway_info(airway_name, config)
    
    # Step 2: Select route segment
    print("\n" + "="*70)
    print("STEP 2: 평가 구간 선택".center(70))
    print("="*70 + "\n")
    
    print("전체 항공로를 평가할까요? (y/n): ", end='')
    if input().strip().lower() == 'y':
        segment = None
    else:
        segment = configurator.select_route_segment(airway_name)
    
    # Step 3: Set date range
    print("\n" + "="*70)
    print("STEP 3: 데이터 수집 기간 설정".center(70))
    print("="*70)
    
    date_range = configurator.set_date_range()
    
    # Step 4: OpenSky authentication
    print("\n" + "="*70)
    print("STEP 4: OpenSky Network 인증".center(70))
    print("="*70 + "\n")
    
    print("실제 OpenSky 데이터를 사용할까요? (y/n): ", end='')
    use_real_data = input().strip().lower() == 'y'
    
    username = None
    password = None
    
    if use_real_data:
        print("\nOpenSky Network 계정 (선택사항 - Enter로 건너뛰기):")
        username = input("  Username: ").strip() or None
        if username:
            password = input("  Password: ").strip() or None
    
    # Step 5: Collect data and assess
    print("\n" + "="*70)
    print("STEP 5: 데이터 수집 및 안전성 평가".center(70))
    print("="*70)
    
    # Collect data
    if use_real_data:
        trajectories = collect_data_with_config(
            airway_name=airway_name,
            segment=segment,
            date_range=date_range,
            username=username,
            password=password
        )
    else:
        print("\n📊 샘플 데이터 생성 중...")
        from basic_assessment import generate_sample_trajectories
        trajectories = generate_sample_trajectories(config, num_flights=100)
        print(f"✅ {len(trajectories)}개 샘플 궤적 생성 완료")
    
    if not trajectories:
        print("❌ 데이터 수집 실패. 프로그램을 종료합니다.")
        return
    
    # Process and assess
    print(f"\n{'='*70}")
    print("데이터 처리 및 분석".center(70))
    print(f"{'='*70}\n")
    
    assessment = AirwaySafetyAssessment(airway_name)
    
    try:
        parameters = assessment.process_trajectory_data(trajectories)
        
        print("✅ 데이터 처리 완료:")
        print(f"   항공기 수: {parameters['aircraft_count']}대")
        print(f"   최적 분포 모델: {parameters['best_distribution']}")
        print(f"   횡적 중첩 확률: {parameters['Py_Sy']:.6f}")
        print(f"   평균 지상 속도: {parameters['speed_stats']['mean']:.2f} knots")
        print(f"   고도 중첩 비율: {parameters['Pi']:.4f}")
        
        # Conduct safety assessment
        print(f"\n{'='*70}")
        print("안전성 평가".center(70))
        print(f"{'='*70}\n")
        
        # Standard CRM
        print("1️⃣  표준 Reich CRM...")
        results_standard = assessment.assess_safety(parameters, use_modified=False)
        print(f"   충돌 위험: {results_standard['collision_risk']:.2e} / 비행시간")
        print(f"   안전 여부: {'✅ 안전' if results_standard['meets_safety'] else '❌ 위험'}")
        print(f"   안전 수준: {results_standard.get('safety_level', 'N/A')}")
        
        # Modified CRM
        print("\n2️⃣  수정 Reich CRM (고도 변경 포함)...")
        results_modified = assessment.assess_safety(parameters, use_modified=True)
        print(f"   충돌 위험: {results_modified['collision_risk']:.2e} / 비행시간")
        print(f"   안전 여부: {'✅ 안전' if results_modified['meets_safety'] else '❌ 위험'}")
        print(f"   안전 수준: {results_modified.get('safety_level', 'N/A')}")
        
        # Generate report
        print(f"\n{'='*70}")
        print("상세 보고서".center(70))
        print(f"{'='*70}")
        
        report = assessment.generate_report()
        print(report)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        segment_str = f"_{segment[0]}-{segment[1]}" if segment else "_full"
        date_str = date_range[0].strftime('%Y%m%d')
        report_filename = f"assessment_{airway_name}{segment_str}_{date_str}_{timestamp}.txt"
        report_path = os.path.join(os.path.dirname(__file__), report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"평가 대상: {airway_name}\n")
            if segment:
                f.write(f"평가 구간: WP{segment[0]+1} ~ WP{segment[1]+1}\n")
            f.write(f"데이터 기간: {date_range[0].strftime('%Y-%m-%d')} ~ {date_range[1].strftime('%Y-%m-%d')}\n")
            f.write(f"데이터 소스: {'OpenSky Network' if use_real_data else '샘플 데이터'}\n")
            f.write(f"\n{report}")
        
        print(f"\n💾 보고서 저장: {report_filename}")
        
    except Exception as e:
        print(f"\n❌ 평가 오류: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Advanced Airway Safety Assessment with Custom Configuration'
    )
    parser.add_argument(
        '--configure-only',
        action='store_true',
        help='Only run configuration tool'
    )
    
    args = parser.parse_args()
    
    if args.configure_only:
        configurator = AirwayConfigurator()
        configurator.interactive_menu()
    else:
        run_advanced_assessment()
    
    print(f"\n{'='*70}")
    print("프로그램 종료".center(70))
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
