"""
Airway Data Processor
항공로 데이터 처리기

Process ADS-B trajectory data for airway safety assessment
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import json


class AirwayDataProcessor:
    """
    Process ADS-B data for airway safety assessment
    항공로 안전성 평가를 위한 ADS-B 데이터 처리
    """
    
    def __init__(self, airway_config: Dict):
        """
        Initialize with airway configuration
        
        Parameters:
        -----------
        airway_config : dict
            Airway configuration including waypoints, separation, etc.
        """
        self.airway_config = airway_config
        self.waypoints = airway_config.get('waypoints', [])
        self.centerline = self._compute_centerline()
        
    def _compute_centerline(self) -> np.ndarray:
        """
        Compute route centerline from waypoints
        
        Returns:
        --------
        np.ndarray : Centerline coordinates (N, 2)
        """
        if not self.waypoints:
            return np.array([])
        
        return np.array([(wp['lon'], wp['lat']) for wp in self.waypoints])
    
    def filter_trajectories_by_route(
        self,
        trajectories: List[Dict],
        tolerance_nm: float = 10.0
    ) -> List[Dict]:
        """
        Filter trajectories that fly along the route
        
        Parameters:
        -----------
        trajectories : list
            List of trajectory dictionaries
        tolerance_nm : float
            Maximum distance from route to consider (nm)
        
        Returns:
        --------
        list : Filtered trajectories
        """
        from ..utils.statistics import DataAnalyzer
        
        filtered = []
        
        for traj in trajectories:
            # Check if trajectory passes near any waypoint
            passes_route = False
            
            for waypoint in self.waypoints:
                wp_coords = np.array([waypoint['lon'], waypoint['lat']])
                
                for i in range(len(traj.get('longitude', []))):
                    point = np.array([traj['longitude'][i], traj['latitude'][i]])
                    distance = DataAnalyzer._haversine_distance(point, wp_coords)
                    
                    if distance <= tolerance_nm:
                        passes_route = True
                        break
                
                if passes_route:
                    break
            
            if passes_route:
                filtered.append(traj)
        
        return filtered
    
    def extract_lateral_deviations(
        self,
        trajectories: List[Dict]
    ) -> np.ndarray:
        """
        Extract lateral deviations from route centerline
        
        Parameters:
        -----------
        trajectories : list
            List of trajectory dictionaries with 'longitude', 'latitude'
        
        Returns:
        --------
        np.ndarray : Lateral deviations in nautical miles
        """
        from ..utils.statistics import DataAnalyzer
        
        all_deviations = []
        
        for traj in trajectories:
            if 'longitude' not in traj or 'latitude' not in traj:
                continue
            
            traj_points = np.column_stack((
                traj['longitude'],
                traj['latitude']
            ))
            
            deviations = DataAnalyzer.calculate_lateral_deviations(
                traj_points,
                self.centerline
            )
            
            all_deviations.extend(deviations)
        
        return np.array(all_deviations)
    
    def extract_altitude_change_times(
        self,
        trajectories: List[Dict],
        altitude_threshold_ft: float = 100.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract altitude change times and total flight times
        
        Parameters:
        -----------
        trajectories : list
            List of trajectory dictionaries
        altitude_threshold_ft : float
            Threshold for detecting altitude change (feet)
        
        Returns:
        --------
        tuple : (altitude_change_times, total_flight_times) in seconds
        """
        altitude_change_times = []
        total_flight_times = []
        
        for traj in trajectories:
            if 'altitude' not in traj or 'time' not in traj:
                continue
            
            altitudes = np.array(traj['altitude'])  # meters
            times = np.array(traj['time'])
            
            # Convert meters to feet
            altitudes_ft = altitudes * 3.28084
            
            # Find altitude change periods
            alt_changing_time = 0
            
            for i in range(1, len(altitudes_ft)):
                alt_diff = abs(altitudes_ft[i] - altitudes_ft[i-1])
                time_diff = times[i] - times[i-1]
                
                if alt_diff > altitude_threshold_ft and time_diff > 0:
                    alt_changing_time += time_diff
            
            total_time = times[-1] - times[0] if len(times) > 1 else 0
            
            if total_time > 0:
                altitude_change_times.append(alt_changing_time)
                total_flight_times.append(total_time)
        
        return np.array(altitude_change_times), np.array(total_flight_times)
    
    def extract_ground_speeds(
        self,
        trajectories: List[Dict]
    ) -> np.ndarray:
        """
        Extract ground speeds from trajectories
        
        Parameters:
        -----------
        trajectories : list
            List of trajectory dictionaries
        
        Returns:
        --------
        np.ndarray : Ground speeds in knots
        """
        speeds = []
        
        for traj in trajectories:
            if 'velocity' in traj:
                # velocity is in m/s, convert to knots
                velocity_ms = traj['velocity']
                if isinstance(velocity_ms, (list, np.ndarray)):
                    speeds.extend([v * 1.94384 for v in velocity_ms if v is not None])
                elif velocity_ms is not None:
                    speeds.append(velocity_ms * 1.94384)
        
        return np.array(speeds)
    
    def extract_aircraft_types(
        self,
        trajectories: List[Dict]
    ) -> Tuple[List[str], List[int]]:
        """
        Extract aircraft type distribution
        
        Parameters:
        -----------
        trajectories : list
            List of trajectory dictionaries
        
        Returns:
        --------
        tuple : (aircraft_types, counts)
        """
        type_counts = {}
        
        for traj in trajectories:
            aircraft_type = traj.get('aircraft_type', 'unknown')
            type_counts[aircraft_type] = type_counts.get(aircraft_type, 0) + 1
        
        aircraft_types = list(type_counts.keys())
        counts = [type_counts[t] for t in aircraft_types]
        
        return aircraft_types, counts
    
    def calculate_waypoint_crossing_times(
        self,
        trajectories: List[Dict],
        waypoint_name: str,
        tolerance_nm: float = 5.0
    ) -> np.ndarray:
        """
        Calculate waypoint crossing times for trajectories
        
        Parameters:
        -----------
        trajectories : list
            List of trajectory dictionaries
        waypoint_name : str
            Name of waypoint
        tolerance_nm : float
            Tolerance for waypoint crossing (nm)
        
        Returns:
        --------
        np.ndarray : Array of crossing times (Unix timestamps)
        """
        from ..utils.statistics import DataAnalyzer
        
        # Find waypoint coordinates
        waypoint = None
        for wp in self.waypoints:
            if wp.get('name') == waypoint_name:
                waypoint = (wp['lon'], wp['lat'])
                break
        
        if waypoint is None:
            return np.array([])
        
        # Convert trajectories to required format
        traj_list = []
        for traj in trajectories:
            if 'longitude' in traj and 'latitude' in traj and 'time' in traj:
                traj_list.append({
                    'time': traj['time'],
                    'lon': traj['longitude'],
                    'lat': traj['latitude']
                })
        
        return DataAnalyzer.extract_waypoint_crossing_times(
            traj_list,
            waypoint,
            tolerance_nm
        )
    
    def export_processed_data(
        self,
        output_path: str,
        data: Dict
    ):
        """
        Export processed data to JSON file
        
        Parameters:
        -----------
        output_path : str
            Path to output file
        data : dict
            Processed data dictionary
        """
        # Convert numpy arrays to lists for JSON serialization
        serializable_data = {}
        
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                serializable_data[key] = value.tolist()
            elif isinstance(value, datetime):
                serializable_data[key] = value.isoformat()
            else:
                serializable_data[key] = value
        
        with open(output_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)
    
    def import_processed_data(
        self,
        input_path: str
    ) -> Dict:
        """
        Import processed data from JSON file
        
        Parameters:
        -----------
        input_path : str
            Path to input file
        
        Returns:
        --------
        dict : Processed data
        """
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        # Convert lists back to numpy arrays
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], (int, float)):
                    data[key] = np.array(value)
        
        return data
