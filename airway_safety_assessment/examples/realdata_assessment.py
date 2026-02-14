"""
Example: Airway Safety Assessment with Real OpenSky Data
실제 OpenSky Network 데이터를 사용한 항공로 안전성 평가

This example demonstrates how to collect real ADS-B data from OpenSky Network
and perform safety assessment.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from airway_safety_assessment import (
    AirwaySafetyAssessment,
    get_airway_config,
)
from airway_safety_assessment.data import OpenSkyClient, BoundingBoxHelper


def collect_real_data_from_opensky(
    airway_name: str,
    username: str = None,
    password: str = None,
    days_back: int = 7,
    sample_interval_hours: int = 6
):
    """
    Collect real ADS-B data from OpenSky Network
    
    Parameters:
    -----------
    airway_name : str
        Name of airway (e.g., 'Y711')
    username : str, optional
        OpenSky Network username (for authenticated access)
    password : str, optional
        OpenSky Network password
    days_back : int
        Number of days to look back for historical data
    sample_interval_hours : int
        Sampling interval in hours
    
    Returns:
    --------
    list : List of trajectory data
    """
    print(f"\n{'='*70}")
    print(f"COLLECTING REAL DATA FROM OPENSKY NETWORK".center(70))
    print(f"{'='*70}\n")
    
    # Get airway configuration
    config = get_airway_config(airway_name)
    waypoints = config.get('waypoints', [])
    
    if not waypoints:
        print(f"❌ No waypoints configured for {airway_name}")
        return []
    
    # Create bounding box around the route
    waypoint_coords = [(wp['lon'], wp['lat']) for wp in waypoints]
    bbox = BoundingBoxHelper.create_route_bbox(waypoint_coords, buffer_nm=50.0)
    
    print(f"Airway: {airway_name}")
    print(f"Waypoints: {len(waypoints)}")
    print(f"Bounding Box: {bbox}")
    print(f"Collection Period: Last {days_back} days")
    print(f"Sampling Interval: {sample_interval_hours} hours\n")
    
    # Initialize OpenSky client
    try:
        client = OpenSkyClient(username=username, password=password)
        print("✅ OpenSky API client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize OpenSky client: {e}")
        print("\n💡 Note: OpenSky API requires installation:")
        print("   cd /path/to/opensky-api")
        print("   pip install -e python/")
        return []
    
    # Set time range
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days_back)
    
    print(f"\n📅 Time Range:")
    print(f"   Start: {start_time.isoformat()}")
    print(f"   End:   {end_time.isoformat()}")
    
    # Collect traffic data
    try:
        print(f"\n🔄 Collecting data...")
        traffic_data = client.collect_route_traffic(
            route_bbox=bbox,
            start_datetime=start_time,
            end_datetime=end_time,
            interval_minutes=sample_interval_hours * 60
        )
        
        print(f"\n✅ Data collection complete!")
        print(f"   Total snapshots: {len(traffic_data)}")
        
        # Convert to trajectory format
        trajectories = []
        for snapshot in traffic_data:
            for state in snapshot['states']:
                # Extract trajectory information
                if state.get('longitude') and state.get('latitude'):
                    trajectory = {
                        'flight_id': state.get('icao24', 'unknown'),
                        'callsign': state.get('callsign'),
                        'aircraft_type': 'unknown',  # OpenSky doesn't provide this directly
                        'longitude': [state['longitude']],
                        'latitude': [state['latitude']],
                        'altitude': [state['altitude']] if state.get('altitude') else [0],
                        'velocity': [state['velocity']] if state.get('velocity') else [0],
                        'time': [state['time_position']] if state.get('time_position') else [snapshot['timestamp']],
                        'heading': [state['heading']] if state.get('heading') else [0]
                    }
                    trajectories.append(trajectory)
        
        print(f"   Total aircraft tracked: {len(trajectories)}")
        return trajectories
        
    except Exception as e:
        print(f"\n❌ Error collecting data: {e}")
        print("\n💡 Possible issues:")
        print("   1. OpenSky API rate limiting (try with authentication)")
        print("   2. No data available for specified time range")
        print("   3. Network connectivity issues")
        return []


def run_assessment_with_real_data(
    airway_name: str = 'Y711',
    opensky_username: str = None,
    opensky_password: str = None,
    use_real_data: bool = True
):
    """
    Run safety assessment with real or sample data
    
    Parameters:
    -----------
    airway_name : str
        Name of airway to assess
    opensky_username : str, optional
        OpenSky Network username
    opensky_password : str, optional
        OpenSky Network password
    use_real_data : bool
        If True, collect real data from OpenSky; if False, use sample data
    """
    print(f"\n{'='*70}")
    print(f"AIRWAY SAFETY ASSESSMENT: {airway_name}".center(70))
    print(f"{'='*70}\n")
    
    # Initialize assessment
    assessment = AirwaySafetyAssessment(airway_name)
    config = get_airway_config(airway_name)
    
    print(f"Airway Configuration:")
    print(f"  Name: {config.get('name')}")
    print(f"  Description: {config.get('description')}")
    print(f"  Type: {config.get('type')}")
    print(f"  Waypoints: {len(config.get('waypoints', []))}")
    
    # Collect or generate trajectory data
    if use_real_data:
        print(f"\n📡 Data Source: OpenSky Network (Real ADS-B Data)")
        trajectories = collect_real_data_from_opensky(
            airway_name=airway_name,
            username=opensky_username,
            password=opensky_password,
            days_back=7,
            sample_interval_hours=6
        )
        
        if not trajectories:
            print("\n⚠️  No real data collected. Falling back to sample data...")
            from basic_assessment import generate_sample_trajectories
            trajectories = generate_sample_trajectories(config, num_flights=100)
    else:
        print(f"\n📊 Data Source: Sample Data (Simulated)")
        from basic_assessment import generate_sample_trajectories
        trajectories = generate_sample_trajectories(config, num_flights=100)
    
    print(f"\n✅ Total trajectories: {len(trajectories)}")
    
    # Process trajectory data
    print(f"\n{'='*70}")
    print("DATA PROCESSING".center(70))
    print(f"{'='*70}\n")
    
    try:
        parameters = assessment.process_trajectory_data(trajectories)
        
        print("✅ Data processing complete:")
        print(f"   Aircraft count: {parameters['aircraft_count']}")
        print(f"   Best distribution: {parameters['best_distribution']}")
        print(f"   Lateral overlap probability: {parameters['Py_Sy']:.6f}")
        print(f"   Average ground speed: {parameters['speed_stats']['mean']:.2f} knots")
        print(f"   Altitude overlap rate: {parameters['Pi']:.4f}")
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return
    
    # Conduct safety assessment
    print(f"\n{'='*70}")
    print("SAFETY ASSESSMENT".center(70))
    print(f"{'='*70}\n")
    
    # Standard Reich CRM
    print("1️⃣  Standard Reich CRM (cruise phase)...")
    results_standard = assessment.assess_safety(parameters, use_modified=False)
    print(f"   Collision Risk: {results_standard['collision_risk']:.2e} per flight hour")
    print(f"   Safety Status: {'✅ SAFE' if results_standard['meets_safety'] else '❌ UNSAFE'}")
    print(f"   Safety Level: {results_standard.get('safety_level', 'N/A')}")
    
    # Modified Reich CRM
    print("\n2️⃣  Modified Reich CRM (with altitude changes)...")
    results_modified = assessment.assess_safety(parameters, use_modified=True)
    print(f"   Collision Risk: {results_modified['collision_risk']:.2e} per flight hour")
    print(f"   Safety Status: {'✅ SAFE' if results_modified['meets_safety'] else '❌ UNSAFE'}")
    print(f"   Safety Level: {results_modified.get('safety_level', 'N/A')}")
    
    # Generate detailed report
    print(f"\n{'='*70}")
    print("DETAILED REPORT".center(70))
    print(f"{'='*70}")
    
    report = assessment.generate_report()
    print(report)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    data_source = "realdata" if use_real_data else "sampledata"
    report_filename = f"safety_assessment_{airway_name}_{data_source}_{timestamp}.txt"
    report_path = os.path.join(os.path.dirname(__file__), report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Report saved: {report_filename}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Airway Safety Assessment with Real OpenSky Data'
    )
    parser.add_argument(
        '--airway',
        type=str,
        default='Y711',
        help='Airway name to assess (default: Y711)'
    )
    parser.add_argument(
        '--real-data',
        action='store_true',
        help='Use real OpenSky Network data (requires API access)'
    )
    parser.add_argument(
        '--username',
        type=str,
        default=None,
        help='OpenSky Network username (optional, for better rate limits)'
    )
    parser.add_argument(
        '--password',
        type=str,
        default=None,
        help='OpenSky Network password (optional)'
    )
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║         AIRWAY SAFETY ASSESSMENT SYSTEM v1.0                         ║
║         항공로 안전성 평가 시스템                                       ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    if args.real_data:
        print("🌐 Mode: Real OpenSky Network Data")
        if args.username:
            print(f"👤 Authenticated User: {args.username}")
        else:
            print("⚠️  Anonymous Access (limited rate)")
    else:
        print("📊 Mode: Sample Data (Simulated)")
    
    run_assessment_with_real_data(
        airway_name=args.airway,
        opensky_username=args.username,
        opensky_password=args.password,
        use_real_data=args.real_data
    )
    
    print(f"\n{'='*70}")
    print("✅ Assessment Complete!".center(70))
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
