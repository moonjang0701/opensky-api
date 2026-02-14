"""
Example: Airway Safety Assessment
항공로 안전성 평가 예제 프로그램

This example demonstrates how to use the Airway Safety Assessment System
to evaluate the safety of airway Y711 (or other configured airways).
"""

import sys
import os
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from airway_safety_assessment import (
    AirwaySafetyAssessment,
    get_airway_config,
    list_available_airways,
    get_active_airways
)


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")


def list_airways():
    """List all available airways"""
    print_header("AVAILABLE AIRWAYS")
    
    airways = list_available_airways()
    active = get_active_airways()
    
    for airway in airways:
        config = get_airway_config(airway)
        status = "✓ Active" if airway in active else "✗ Inactive"
        print(f"{airway:10} - {config.get('description', 'N/A'):40} [{status}]")


def generate_sample_trajectories(airway_config: dict, num_flights: int = 100) -> list:
    """
    Generate sample trajectory data for demonstration
    
    In real usage, this would be replaced with actual ADS-B data from OpenSky Network
    
    Parameters:
    -----------
    airway_config : dict
        Airway configuration
    num_flights : int
        Number of sample flights to generate
    
    Returns:
    --------
    list : Sample trajectory data
    """
    print(f"Generating {num_flights} sample trajectories...")
    
    trajectories = []
    waypoints = airway_config.get('waypoints', [])
    
    if len(waypoints) < 2:
        print("Warning: Insufficient waypoints in configuration")
        return []
    
    # Generate sample flights along the route
    for i in range(num_flights):
        # Generate trajectory points along route with some lateral deviation
        num_points = 50
        
        # Interpolate between waypoints
        lons = np.linspace(waypoints[0]['lon'], waypoints[-1]['lon'], num_points)
        lats = np.linspace(waypoints[0]['lat'], waypoints[-1]['lat'], num_points)
        
        # Add random lateral deviation (simulating real flight paths)
        # Using normal distribution with std dev of 0.05 nm
        lateral_noise = np.random.normal(0, 0.05, num_points)
        
        lons += lateral_noise
        lats += lateral_noise * 0.5
        
        # Generate altitudes (cruise altitude with some variation)
        base_altitude = 35000  # feet
        altitudes = np.ones(num_points) * base_altitude / 3.28084  # Convert to meters
        
        # Add altitude changes for some flights
        if i % 10 == 0:  # 10% of flights have altitude changes
            change_start = num_points // 3
            change_end = 2 * num_points // 3
            altitudes[change_start:change_end] += np.linspace(0, 2000, change_end - change_start)
        
        # Generate ground speeds (typical cruise speed with variation)
        base_speed = 450  # knots
        speeds = np.random.normal(base_speed, 20, num_points) / 1.94384  # Convert to m/s
        
        # Generate timestamps
        start_time = datetime(2024, 5, 1, 10, 0, 0) + timedelta(hours=i*0.5)
        times = [start_time + timedelta(seconds=j*10) for j in range(num_points)]
        times_unix = [int(t.timestamp()) for t in times]
        
        # Assign aircraft type (realistic distribution)
        aircraft_types = ['B738', 'A321', 'B77W', 'A333', 'B789']
        weights = [0.4, 0.3, 0.15, 0.1, 0.05]
        aircraft_type = np.random.choice(aircraft_types, p=weights)
        
        trajectory = {
            'flight_id': f'FL{i:04d}',
            'aircraft_type': aircraft_type,
            'longitude': lons.tolist(),
            'latitude': lats.tolist(),
            'altitude': altitudes.tolist(),
            'velocity': speeds.tolist(),
            'time': times_unix,
            'heading': np.random.uniform(0, 360, num_points).tolist()
        }
        
        trajectories.append(trajectory)
    
    print(f"✓ Generated {len(trajectories)} sample trajectories")
    return trajectories


def run_assessment_example(airway_name: str = 'Y711'):
    """
    Run complete safety assessment example
    
    Parameters:
    -----------
    airway_name : str
        Name of airway to assess (default: 'Y711')
    """
    print_header(f"SAFETY ASSESSMENT: {airway_name}")
    
    # Initialize assessment
    print(f"Initializing safety assessment for airway {airway_name}...")
    assessment = AirwaySafetyAssessment(airway_name)
    
    config = get_airway_config(airway_name)
    print(f"✓ Configuration loaded")
    print(f"  Route: {config.get('description', 'N/A')}")
    print(f"  Type: {config.get('type', 'N/A')}")
    print(f"  Waypoints: {len(config.get('waypoints', []))}")
    
    # Generate or load trajectory data
    print("\nStep 1: Loading trajectory data...")
    trajectories = generate_sample_trajectories(config, num_flights=100)
    print(f"✓ Loaded {len(trajectories)} trajectories")
    
    # Process trajectory data
    print("\nStep 2: Processing trajectory data...")
    try:
        parameters = assessment.process_trajectory_data(trajectories)
        print("✓ Data processing complete")
        print(f"  Aircraft count: {parameters['aircraft_count']}")
        print(f"  Best distribution model: {parameters['best_distribution']}")
        print(f"  Lateral overlap probability (Py_Sy): {parameters['Py_Sy']:.6f}")
        print(f"  Average ground speed: {parameters['speed_stats']['mean']:.2f} knots")
    except Exception as e:
        print(f"✗ Error processing data: {e}")
        return
    
    # Conduct safety assessment
    print("\nStep 3: Conducting safety assessment...")
    
    # Standard Reich CRM
    print("\n  3a. Standard Reich CRM...")
    results_standard = assessment.assess_safety(parameters, use_modified=False)
    print(f"     Collision Risk: {results_standard['collision_risk']:.2e} per flight hour")
    print(f"     Meets Safety: {'Yes' if results_standard['meets_safety'] else 'No'}")
    
    # Modified Reich CRM (for altitude changes)
    print("\n  3b. Modified Reich CRM (with altitude changes)...")
    results_modified = assessment.assess_safety(parameters, use_modified=True)
    print(f"     Collision Risk: {results_modified['collision_risk']:.2e} per flight hour")
    print(f"     Meets Safety: {'Yes' if results_modified['meets_safety'] else 'No'}")
    
    # Generate report
    print("\nStep 4: Generating report...")
    report = assessment.generate_report()
    print(report)
    
    # Save report to file
    report_filename = f"safety_assessment_{airway_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = os.path.join(os.path.dirname(__file__), report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Report saved to: {report_filename}")


def interactive_menu():
    """Interactive menu for airway selection"""
    print_header("AIRWAY SAFETY ASSESSMENT SYSTEM")
    print("항공로 안전성 평가 시스템")
    
    while True:
        print("\nMenu:")
        print("1. List available airways")
        print("2. Assess specific airway")
        print("3. Assess all active airways")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            list_airways()
        
        elif choice == '2':
            list_airways()
            airway = input("\nEnter airway name (e.g., Y711): ").strip().upper()
            
            if airway in list_available_airways():
                try:
                    run_assessment_example(airway)
                except Exception as e:
                    print(f"\n✗ Error during assessment: {e}")
            else:
                print(f"\n✗ Airway '{airway}' not found")
        
        elif choice == '3':
            active_airways = get_active_airways()
            print(f"\nAssessing {len(active_airways)} active airways...")
            
            for airway in active_airways:
                try:
                    run_assessment_example(airway)
                except Exception as e:
                    print(f"\n✗ Error assessing {airway}: {e}")
        
        elif choice == '4':
            print("\nExiting...")
            break
        
        else:
            print("\n✗ Invalid option. Please select 1-4.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Airway Safety Assessment System - Example'
    )
    parser.add_argument(
        '--airway',
        type=str,
        default=None,
        help='Airway name to assess (e.g., Y711)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available airways'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_airways()
    elif args.interactive:
        interactive_menu()
    elif args.airway:
        run_assessment_example(args.airway)
    else:
        # Default: run Y711 assessment
        run_assessment_example('Y711')


if __name__ == '__main__':
    main()
