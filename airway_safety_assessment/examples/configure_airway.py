"""
Interactive Airway Configuration Tool
대화형 항공로 설정 도구

Allows users to:
1. Add new airways with custom waypoints
2. Edit existing airway configurations
3. Set evaluation date ranges
4. Select specific route segments
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from airway_safety_assessment.config import airways


class AirwayConfigurator:
    """
    Interactive tool for configuring airways
    항공로 대화형 설정 도구
    """
    
    def __init__(self):
        self.custom_airways = {}
        self.custom_config_path = os.path.join(
            os.path.dirname(__file__), 
            '../config/custom_airways.json'
        )
        self.load_custom_airways()
    
    def load_custom_airways(self):
        """Load custom airway configurations from file"""
        if os.path.exists(self.custom_config_path):
            try:
                with open(self.custom_config_path, 'r', encoding='utf-8') as f:
                    self.custom_airways = json.load(f)
                print(f"✅ Loaded {len(self.custom_airways)} custom airway(s)")
            except Exception as e:
                print(f"⚠️  Error loading custom airways: {e}")
                self.custom_airways = {}
    
    def save_custom_airways(self):
        """Save custom airway configurations to file"""
        try:
            os.makedirs(os.path.dirname(self.custom_config_path), exist_ok=True)
            with open(self.custom_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.custom_airways, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {len(self.custom_airways)} custom airway(s)")
        except Exception as e:
            print(f"❌ Error saving custom airways: {e}")
    
    def add_new_airway(self):
        """Add a new airway with custom configuration"""
        print("\n" + "="*70)
        print("ADD NEW AIRWAY".center(70))
        print("="*70 + "\n")
        
        # Get airway name
        airway_name = input("항공로 이름 (예: Y711, MY001): ").strip().upper()
        
        if not airway_name:
            print("❌ 항공로 이름을 입력해야 합니다.")
            return
        
        # Check if already exists
        if airway_name in airways.KOREAN_AIRWAYS or airway_name in self.custom_airways:
            print(f"⚠️  '{airway_name}' 이미 존재합니다. 덮어쓸까요? (y/n): ", end='')
            if input().strip().lower() != 'y':
                return
        
        # Get description
        description = input("설명 (예: 서울-부산 항공로): ").strip()
        
        # Get waypoints
        print("\n웨이포인트 입력 (최소 2개 필요):")
        print("각 웨이포인트마다 이름, 위도, 경도를 입력하세요.")
        print("입력 완료 시 빈 줄 입력\n")
        
        waypoints = []
        while True:
            wp_num = len(waypoints) + 1
            print(f"웨이포인트 {wp_num}:")
            
            name = input(f"  이름 (예: OLMEN): ").strip()
            if not name:
                if len(waypoints) >= 2:
                    break
                else:
                    print("  ⚠️  최소 2개의 웨이포인트가 필요합니다.")
                    continue
            
            try:
                lat = float(input(f"  위도 (예: 37.5): ").strip())
                lon = float(input(f"  경도 (예: 126.5): ").strip())
                
                waypoints.append({
                    'name': name.upper(),
                    'lat': lat,
                    'lon': lon
                })
                print(f"  ✅ {name} 추가됨 ({lat}, {lon})")
            except ValueError:
                print("  ❌ 위도/경도는 숫자여야 합니다.")
        
        # Get separation
        try:
            separation = float(input("\n항공로 분리 거리 (nm, 기본값 160): ").strip() or "160")
        except ValueError:
            separation = 160.0
        
        # Get type
        print("\n항공로 유형:")
        print("  1. parallel (평행)")
        print("  2. single (단선)")
        print("  3. crossing (교차)")
        route_type = input("선택 (1-3, 기본값 1): ").strip() or "1"
        type_map = {'1': 'parallel', '2': 'single', '3': 'crossing'}
        route_type = type_map.get(route_type, 'parallel')
        
        # Create configuration
        config = {
            'name': airway_name,
            'description': description or f'{airway_name} route',
            'waypoints': waypoints,
            'separation_nm': separation,
            'type': route_type,
            'active': True,
            'created_at': datetime.now().isoformat()
        }
        
        # Save
        self.custom_airways[airway_name] = config
        self.save_custom_airways()
        
        print(f"\n✅ 항공로 '{airway_name}' 생성 완료!")
        self.display_airway_info(airway_name, config)
    
    def edit_airway_waypoints(self):
        """Edit waypoints of existing airway"""
        print("\n" + "="*70)
        print("EDIT AIRWAY WAYPOINTS".center(70))
        print("="*70 + "\n")
        
        # List airways
        self.list_all_airways()
        
        airway_name = input("\n편집할 항공로 이름: ").strip().upper()
        
        # Get config
        if airway_name in self.custom_airways:
            config = self.custom_airways[airway_name]
        elif airway_name in airways.KOREAN_AIRWAYS:
            config = airways.KOREAN_AIRWAYS[airway_name].copy()
            print("⚠️  기본 항공로를 수정하면 custom_airways.json에 복사됩니다.")
        else:
            print(f"❌ '{airway_name}' 항공로를 찾을 수 없습니다.")
            return
        
        # Display current waypoints
        print(f"\n현재 웨이포인트 ({len(config['waypoints'])}개):")
        for i, wp in enumerate(config['waypoints'], 1):
            print(f"  {i}. {wp['name']:10} - Lat: {wp['lat']:7.3f}, Lon: {wp['lon']:7.3f}")
        
        # Edit options
        print("\n편집 옵션:")
        print("  1. 웨이포인트 추가")
        print("  2. 웨이포인트 수정")
        print("  3. 웨이포인트 삭제")
        print("  4. 모두 다시 입력")
        
        choice = input("선택 (1-4): ").strip()
        
        if choice == '1':
            # Add waypoint
            name = input("이름: ").strip().upper()
            lat = float(input("위도: ").strip())
            lon = float(input("경도: ").strip())
            config['waypoints'].append({'name': name, 'lat': lat, 'lon': lon})
            print(f"✅ {name} 추가됨")
        
        elif choice == '2':
            # Edit waypoint
            idx = int(input("수정할 웨이포인트 번호: ").strip()) - 1
            if 0 <= idx < len(config['waypoints']):
                wp = config['waypoints'][idx]
                print(f"현재: {wp['name']} ({wp['lat']}, {wp['lon']})")
                name = input(f"새 이름 (Enter=유지): ").strip().upper() or wp['name']
                lat = input(f"새 위도 (Enter=유지): ").strip()
                lon = input(f"새 경도 (Enter=유지): ").strip()
                config['waypoints'][idx] = {
                    'name': name,
                    'lat': float(lat) if lat else wp['lat'],
                    'lon': float(lon) if lon else wp['lon']
                }
                print("✅ 수정 완료")
        
        elif choice == '3':
            # Delete waypoint
            idx = int(input("삭제할 웨이포인트 번호: ").strip()) - 1
            if 0 <= idx < len(config['waypoints']):
                removed = config['waypoints'].pop(idx)
                print(f"✅ {removed['name']} 삭제됨")
        
        elif choice == '4':
            # Re-enter all
            config['waypoints'] = []
            print("\n새 웨이포인트 입력 (빈 줄로 종료):")
            while True:
                name = input(f"웨이포인트 {len(config['waypoints'])+1} 이름: ").strip()
                if not name:
                    break
                lat = float(input("  위도: ").strip())
                lon = float(input("  경도: ").strip())
                config['waypoints'].append({'name': name.upper(), 'lat': lat, 'lon': lon})
        
        # Save
        self.custom_airways[airway_name] = config
        self.save_custom_airways()
        print(f"\n✅ '{airway_name}' 업데이트 완료!")
    
    def select_route_segment(self, airway_name: str) -> Tuple[int, int]:
        """
        Select specific segment of route for evaluation
        
        Returns:
        --------
        tuple : (start_waypoint_index, end_waypoint_index)
        """
        # Get config
        if airway_name in self.custom_airways:
            config = self.custom_airways[airway_name]
        else:
            config = airways.get_airway_config(airway_name)
        
        if not config:
            return (0, -1)
        
        waypoints = config.get('waypoints', [])
        
        print(f"\n{airway_name} 웨이포인트:")
        for i, wp in enumerate(waypoints):
            print(f"  {i+1}. {wp['name']:10} - ({wp['lat']:.3f}, {wp['lon']:.3f})")
        
        print("\n평가할 구간 선택:")
        try:
            start = int(input(f"시작 웨이포인트 번호 (1-{len(waypoints)}): ").strip()) - 1
            end = int(input(f"종료 웨이포인트 번호 (1-{len(waypoints)}): ").strip()) - 1
            
            if 0 <= start < len(waypoints) and 0 <= end < len(waypoints) and start < end:
                print(f"✅ 구간 선택: {waypoints[start]['name']} → {waypoints[end]['name']}")
                return (start, end)
        except (ValueError, IndexError):
            pass
        
        print("⚠️  잘못된 입력. 전체 구간을 사용합니다.")
        return (0, len(waypoints) - 1)
    
    def set_date_range(self) -> Tuple[datetime, datetime]:
        """
        Set date range for data collection
        
        Returns:
        --------
        tuple : (start_datetime, end_datetime)
        """
        print("\n" + "="*70)
        print("SET DATE RANGE".center(70))
        print("="*70 + "\n")
        
        print("데이터 수집 기간 설정:")
        print("  1. 최근 1일")
        print("  2. 최근 7일 (기본)")
        print("  3. 최근 30일")
        print("  4. 사용자 지정")
        
        choice = input("\n선택 (1-4, 기본값 2): ").strip() or "2"
        
        end_time = datetime.now()
        
        if choice == '1':
            start_time = end_time - timedelta(days=1)
        elif choice == '2':
            start_time = end_time - timedelta(days=7)
        elif choice == '3':
            start_time = end_time - timedelta(days=30)
        elif choice == '4':
            print("\n시작 날짜 입력 (YYYY-MM-DD):")
            start_str = input("  예: 2024-01-01: ").strip()
            print("종료 날짜 입력 (YYYY-MM-DD, Enter=오늘):")
            end_str = input("  예: 2024-02-01: ").strip()
            
            try:
                start_time = datetime.strptime(start_str, '%Y-%m-%d')
                if end_str:
                    end_time = datetime.strptime(end_str, '%Y-%m-%d')
            except ValueError:
                print("❌ 날짜 형식 오류. 기본값 사용 (최근 7일)")
                start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(days=7)
        
        print(f"\n✅ 기간 설정:")
        print(f"   시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   기간: {(end_time - start_time).days}일")
        
        return (start_time, end_time)
    
    def list_all_airways(self):
        """List all available airways"""
        print("\n기본 항공로:")
        for name, config in airways.KOREAN_AIRWAYS.items():
            status = "✓" if config.get('active') else "✗"
            wp_count = len(config.get('waypoints', []))
            print(f"  [{status}] {name:10} - {config['description']:40} ({wp_count}개 웨이포인트)")
        
        if self.custom_airways:
            print("\n사용자 정의 항공로:")
            for name, config in self.custom_airways.items():
                wp_count = len(config.get('waypoints', []))
                created = config.get('created_at', 'N/A')[:10]
                print(f"  [✓] {name:10} - {config['description']:40} ({wp_count}개 웨이포인트) [{created}]")
    
    def display_airway_info(self, name: str, config: Dict):
        """Display detailed airway information"""
        print(f"\n{'='*70}")
        print(f"AIRWAY: {name}".center(70))
        print(f"{'='*70}")
        print(f"\n설명: {config.get('description', 'N/A')}")
        print(f"유형: {config.get('type', 'N/A')}")
        print(f"분리 거리: {config.get('separation_nm', 'N/A')} nm")
        print(f"\n웨이포인트 ({len(config.get('waypoints', []))}개):")
        for i, wp in enumerate(config.get('waypoints', []), 1):
            print(f"  {i}. {wp['name']:10} - Lat: {wp['lat']:8.4f}, Lon: {wp['lon']:8.4f}")
        print(f"{'='*70}\n")
    
    def interactive_menu(self):
        """Interactive configuration menu"""
        while True:
            print("\n" + "="*70)
            print("AIRWAY CONFIGURATION TOOL".center(70))
            print("항공로 설정 도구".center(70))
            print("="*70)
            
            print("\n메뉴:")
            print("  1. 모든 항공로 보기")
            print("  2. 새 항공로 추가")
            print("  3. 항공로 웨이포인트 편집")
            print("  4. 항공로 정보 보기")
            print("  5. 평가 날짜 범위 설정")
            print("  6. 평가 구간 선택")
            print("  0. 종료")
            
            choice = input("\n선택 (0-6): ").strip()
            
            if choice == '1':
                self.list_all_airways()
            
            elif choice == '2':
                self.add_new_airway()
            
            elif choice == '3':
                self.edit_airway_waypoints()
            
            elif choice == '4':
                self.list_all_airways()
                name = input("\n항공로 이름: ").strip().upper()
                config = self.custom_airways.get(name) or airways.get_airway_config(name)
                if config:
                    self.display_airway_info(name, config)
                else:
                    print(f"❌ '{name}' 항공로를 찾을 수 없습니다.")
            
            elif choice == '5':
                start, end = self.set_date_range()
            
            elif choice == '6':
                self.list_all_airways()
                name = input("\n항공로 이름: ").strip().upper()
                self.select_route_segment(name)
            
            elif choice == '0':
                print("\n종료합니다.")
                break
            
            else:
                print("❌ 잘못된 선택입니다.")


def main():
    """Main entry point"""
    configurator = AirwayConfigurator()
    configurator.interactive_menu()


if __name__ == '__main__':
    main()
