"""
Enhanced Sample Data Generator Based on 2020 Statistics
2020년 통계 기반 개선된 샘플 데이터 생성기

Based on:
- Park et al. (2024) paper statistics
- Y711 route characteristics
- Realistic traffic patterns
"""

import numpy as np
from datetime import datetime, timedelta
import json


class RealisticSampleGenerator:
    """2020년 통계 기반 현실적인 샘플 데이터 생성"""
    
    def __init__(self, airway_name='Y711'):
        self.airway_name = airway_name
        
        # 2020년 5월 통계 (Park et al. 논문 기반)
        self.statistics_2020 = {
            'Y711': {
                'daily_traffic': 150,  # 추정 (Y571/Y572 합: 약 420편/일)
                'peak_hours': [9, 10, 11, 14, 15, 16, 17],  # 오전/오후 피크
                'aircraft_types': {
                    'B738': 0.35,  # Boeing 737-800
                    'A321': 0.25,  # Airbus A321
                    'A320': 0.20,  # Airbus A320
                    'B77W': 0.10,  # Boeing 777-300ER
                    'A333': 0.10,  # Airbus A330-300
                },
                'speed_mean': 450,  # knots
                'speed_std': 25,
                'altitude_mean': 35000,  # feet
                'altitude_std': 2000,
                'lateral_deviation_std': 0.15,  # NM (논문 기반)
            }
        }
    
    def generate_realistic_trajectories(
        self, 
        waypoints, 
        n_aircraft=100,
        date_str='2020-05-01',
        time_distribution='realistic'
    ):
        """
        현실적인 궤적 생성
        
        Parameters:
        -----------
        waypoints : list
            항로 웨이포인트
        n_aircraft : int
            생성할 항공기 수
        date_str : str
            기준 날짜
        time_distribution : str
            'realistic' - 피크 시간대 반영
            'uniform' - 균등 분포
        """
        stats = self.statistics_2020.get(self.airway_name, self.statistics_2020['Y711'])
        
        trajectories = []
        base_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        for i in range(n_aircraft):
            # 시간 할당
            if time_distribution == 'realistic':
                # 피크 시간대 60%, 비피크 40%
                if np.random.random() < 0.6:
                    hour = np.random.choice(stats['peak_hours'])
                else:
                    hour = np.random.randint(6, 23)
            else:
                hour = np.random.randint(6, 23)
            
            minute = np.random.randint(0, 60)
            timestamp = base_date + timedelta(hours=int(hour), minutes=int(minute))
            
            # 항공기 타입
            aircraft_type = np.random.choice(
                list(stats['aircraft_types'].keys()),
                p=list(stats['aircraft_types'].values())
            )
            
            # 속도 (현실적인 분포)
            velocity = np.random.normal(stats['speed_mean'], stats['speed_std'])
            velocity = max(400, min(500, velocity))  # 400-500 knots 범위
            
            # 고도
            altitude = np.random.normal(stats['altitude_mean'], stats['altitude_std'])
            altitude = max(30000, min(40000, altitude))  # 30000-40000 feet
            
            # 궤적 생성 (웨이포인트 기반)
            positions = []
            for wp in waypoints:
                # 횡적 편차 (정규 분포)
                lateral_dev = np.random.normal(0, stats['lateral_deviation_std'])
                
                # 위치 계산 (위도/경도에 편차 추가)
                lat = wp['lat'] + lateral_dev * 0.01  # ~0.6 NM per 0.01 deg
                lon = wp['lon'] + np.random.normal(0, 0.005)
                
                positions.append({
                    'latitude': lat,
                    'longitude': lon,
                    'altitude': altitude + np.random.normal(0, 500),  # 고도 변화
                    'velocity': velocity + np.random.normal(0, 10),
                })
            
            trajectory = {
                'icao24': f'7c{i:04x}',  # 한국 항공기 코드 (7Cxxxx)
                'callsign': f'{aircraft_type}{i:03d}',
                'aircraft_type': aircraft_type,
                'timestamp': int(timestamp.timestamp()),
                'time_str': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'positions': positions,
                'statistics': {
                    'mean_velocity': velocity,
                    'mean_altitude': altitude,
                    'lateral_deviation': lateral_dev
                }
            }
            
            trajectories.append(trajectory)
        
        return trajectories
    
    def generate_daily_pattern(self, waypoints, date_str='2020-05-01'):
        """하루 24시간 패턴 생성"""
        stats = self.statistics_2020.get(self.airway_name, self.statistics_2020['Y711'])
        daily_traffic = stats['daily_traffic']
        
        return self.generate_realistic_trajectories(
            waypoints,
            n_aircraft=daily_traffic,
            date_str=date_str,
            time_distribution='realistic'
        )
    
    def save_to_json(self, trajectories, filename):
        """JSON 파일로 저장"""
        output = {
            'airway': self.airway_name,
            'source': 'realistic_sample_2020_statistics',
            'reference': 'Park et al. (2024)',
            'generated_at': datetime.now().isoformat(),
            'count': len(trajectories),
            'trajectories': trajectories
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return filename


def main():
    """테스트 및 사용 예시"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='2020년 통계 기반 현실적인 샘플 데이터 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # Y711 2020년 5월 1일 하루 패턴 (150편)
  python generate_realistic_samples.py --airway Y711 --date 2020-05-01 --daily
  
  # 100편 샘플 생성
  python generate_realistic_samples.py --airway Y711 --count 100
  
  # 7일간 데이터 생성
  python generate_realistic_samples.py --airway Y711 --date 2020-05-01 --days 7
        """
    )
    
    parser.add_argument('--airway', type=str, default='Y711',
                        help='항로 이름 (기본: Y711)')
    parser.add_argument('--date', type=str, default='2020-05-01',
                        help='기준 날짜 (YYYY-MM-DD)')
    parser.add_argument('--count', type=int, default=100,
                        help='생성할 항공기 수 (기본: 100)')
    parser.add_argument('--daily', action='store_true',
                        help='하루 패턴 생성 (피크 시간대 반영)')
    parser.add_argument('--days', type=int, default=1,
                        help='생성할 일수 (기본: 1)')
    parser.add_argument('--output', type=str, default=None,
                        help='출력 파일명')
    
    args = parser.parse_args()
    
    # 항로 정보 로드
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    from airway_safety_assessment import get_airway_config
    
    config = get_airway_config(args.airway)
    if not config:
        print(f"❌ '{args.airway}' 항로를 찾을 수 없습니다.")
        return
    
    waypoints = config.get('waypoints', [])
    
    print("="*70)
    print("  2020년 통계 기반 현실적인 샘플 데이터 생성")
    print("="*70)
    print()
    print(f"📍 항로: {args.airway}")
    print(f"   웨이포인트: {len(waypoints)}개")
    for i, wp in enumerate(waypoints, 1):
        print(f"      {i}. {wp['name']} ({wp['lat']:.3f}, {wp['lon']:.3f})")
    print()
    
    generator = RealisticSampleGenerator(args.airway)
    
    all_trajectories = []
    
    for day in range(args.days):
        date = datetime.strptime(args.date, '%Y-%m-%d') + timedelta(days=day)
        date_str = date.strftime('%Y-%m-%d')
        
        print(f"📅 생성 중: {date_str}")
        
        if args.daily:
            trajectories = generator.generate_daily_pattern(waypoints, date_str)
        else:
            trajectories = generator.generate_realistic_trajectories(
                waypoints, 
                n_aircraft=args.count // args.days,
                date_str=date_str
            )
        
        all_trajectories.extend(trajectories)
        print(f"   ✅ 생성: {len(trajectories)}편")
    
    print()
    print(f"📊 총 생성: {len(all_trajectories)}편")
    print()
    
    # 통계 출력
    if all_trajectories:
        velocities = [t['statistics']['mean_velocity'] for t in all_trajectories]
        altitudes = [t['statistics']['mean_altitude'] for t in all_trajectories]
        lateral_devs = [t['statistics']['lateral_deviation'] for t in all_trajectories]
        
        print("통계:")
        print(f"   평균 속도: {np.mean(velocities):.1f} ± {np.std(velocities):.1f} knots")
        print(f"   평균 고도: {np.mean(altitudes):.0f} ± {np.std(altitudes):.0f} feet")
        print(f"   횡적 편차: {np.mean(lateral_devs):.3f} ± {np.std(lateral_devs):.3f} NM")
    
    # 저장
    if args.output is None:
        filename = f"realistic_samples_{args.airway}_{args.date}_{len(all_trajectories)}.json"
    else:
        filename = args.output
    
    generator.save_to_json(all_trajectories, filename)
    print()
    print(f"💾 저장: {filename}")
    print()
    print("✅ 완료!")


if __name__ == '__main__':
    main()
