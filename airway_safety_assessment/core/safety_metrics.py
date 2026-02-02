"""
Safety Metrics Calculator
안전성 지표 계산 모듈
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class SafetyMetrics:
    """
    Calculate various safety metrics for airway assessment
    항공로 평가를 위한 다양한 안전성 지표 계산
    """
    
    # ICAO Target Level of Safety
    TLS = 5e-9  # collisions per flight hour
    
    @staticmethod
    def calculate_aircraft_dimensions(
        aircraft_types: List[str],
        counts: List[int]
    ) -> Dict[str, float]:
        """
        Calculate weighted average aircraft dimensions
        
        Parameters:
        -----------
        aircraft_types : List[str]
            List of aircraft type codes (e.g., ['B738', 'A321', ...])
        counts : List[int]
            Number of each aircraft type
            
        Returns:
        --------
        dict : Weighted average dimensions (length, wingspan, height) in nm
        """
        # Standard aircraft dimensions (in meters)
        # Based on common aircraft specifications
        aircraft_specs = {
            'B738': {'length': 39.5, 'wingspan': 35.8, 'height': 12.5},
            'B737': {'length': 39.5, 'wingspan': 35.8, 'height': 12.5},
            'A321': {'length': 44.5, 'wingspan': 35.8, 'height': 11.8},
            'A320': {'length': 37.6, 'wingspan': 35.8, 'height': 11.8},
            'B77W': {'length': 73.9, 'wingspan': 64.8, 'height': 18.5},
            'B777': {'length': 73.9, 'wingspan': 64.8, 'height': 18.5},
            'A333': {'length': 63.7, 'wingspan': 60.3, 'height': 16.9},
            'A330': {'length': 63.7, 'wingspan': 60.3, 'height': 16.9},
            'B789': {'length': 62.8, 'wingspan': 60.1, 'height': 17.0},
            'B787': {'length': 62.8, 'wingspan': 60.1, 'height': 17.0},
            'A359': {'length': 66.8, 'wingspan': 64.8, 'height': 17.1},
            'A350': {'length': 66.8, 'wingspan': 64.8, 'height': 17.1},
        }
        
        # Default for unknown aircraft types
        default_specs = {'length': 40.0, 'wingspan': 36.0, 'height': 12.0}
        
        total_count = sum(counts)
        if total_count == 0:
            return {
                'lambda_x': 0.0216,  # nm (40m)
                'lambda_y': 0.0194,  # nm (36m)
                'lambda_z': 0.0065   # nm (12m)
            }
        
        total_length = 0.0
        total_wingspan = 0.0
        total_height = 0.0
        
        for aircraft_type, count in zip(aircraft_types, counts):
            specs = aircraft_specs.get(aircraft_type, default_specs)
            total_length += specs['length'] * count
            total_wingspan += specs['wingspan'] * count
            total_height += specs['height'] * count
        
        avg_length = total_length / total_count
        avg_wingspan = total_wingspan / total_count
        avg_height = total_height / total_count
        
        # Convert meters to nautical miles (1 nm = 1852 m)
        return {
            'lambda_x': avg_length / 1852.0,
            'lambda_y': avg_wingspan / 1852.0,
            'lambda_z': avg_height / 1852.0
        }
    
    @staticmethod
    def calculate_ground_speed_stats(
        ground_speeds: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate ground speed statistics
        
        Parameters:
        -----------
        ground_speeds : np.ndarray
            Array of ground speeds in knots
            
        Returns:
        --------
        dict : Statistics including mean, median, std
        """
        if len(ground_speeds) == 0:
            return {
                'mean': 0.0,
                'median': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0
            }
        
        return {
            'mean': float(np.mean(ground_speeds)),
            'median': float(np.median(ground_speeds)),
            'std': float(np.std(ground_speeds)),
            'min': float(np.min(ground_speeds)),
            'max': float(np.max(ground_speeds))
        }
    
    @staticmethod
    def calculate_vertical_overlap_probability(
        altitude_deviations: Optional[np.ndarray] = None,
        use_standard: bool = True
    ) -> float:
        """
        Calculate vertical overlap probability Pz(0)
        
        Parameters:
        -----------
        altitude_deviations : np.ndarray, optional
            Observed altitude deviations (feet)
        use_standard : bool
            If True, use standard value from JASMA/BOBASMA (0.538)
            
        Returns:
        --------
        float : Vertical overlap probability
        """
        if use_standard or altitude_deviations is None:
            # Standard value from regional monitoring agencies
            # (JASMA, BOBASMA) as mentioned in the paper
            return 0.538
        
        # If custom calculation needed (not used in the paper)
        # Could implement custom Pz calculation here
        return 0.538
    
    @staticmethod
    def calculate_separation_minimum(
        route_type: str = 'parallel'
    ) -> float:
        """
        Get separation minimum for route type
        
        Parameters:
        -----------
        route_type : str
            Type of route ('parallel', 'crossing', etc.)
            
        Returns:
        --------
        float : Separation minimum in nautical miles
        """
        separation_standards = {
            'parallel': 160.0,  # nm (used in the paper)
            'crossing': 160.0,
            'converging': 160.0
        }
        
        return separation_standards.get(route_type, 160.0)
    
    @staticmethod
    def evaluate_safety_compliance(
        collision_risk: float,
        TLS: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Evaluate if collision risk meets safety standards
        
        Parameters:
        -----------
        collision_risk : float
            Calculated collision risk (per flight hour)
        TLS : float, optional
            Target Level of Safety (default: 5e-9)
            
        Returns:
        --------
        dict : Evaluation results
        """
        if TLS is None:
            TLS = SafetyMetrics.TLS
        
        ratio = collision_risk / TLS if TLS > 0 else float('inf')
        
        return {
            'collision_risk': collision_risk,
            'TLS': TLS,
            'ratio': ratio,
            'meets_safety': collision_risk < TLS,
            'safety_margin': TLS - collision_risk,
            'safety_level': SafetyMetrics._classify_safety_level(ratio)
        }
    
    @staticmethod
    def _classify_safety_level(ratio: float) -> str:
        """
        Classify safety level based on risk ratio
        
        Parameters:
        -----------
        ratio : float
            Ratio of collision risk to TLS
            
        Returns:
        --------
        str : Safety level classification
        """
        if ratio < 0.1:
            return 'Excellent'
        elif ratio < 0.5:
            return 'Good'
        elif ratio < 1.0:
            return 'Acceptable'
        else:
            return 'Unsafe'
    
    @staticmethod
    def calculate_traffic_density(
        aircraft_count: int,
        time_period_hours: float,
        route_length_nm: float
    ) -> Dict[str, float]:
        """
        Calculate traffic density metrics
        
        Parameters:
        -----------
        aircraft_count : int
            Number of aircraft
        time_period_hours : float
            Time period in hours
        route_length_nm : float
            Route length in nautical miles
            
        Returns:
        --------
        dict : Traffic density metrics
        """
        if time_period_hours == 0 or route_length_nm == 0:
            return {
                'aircraft_per_hour': 0.0,
                'aircraft_per_nm': 0.0,
                'density_index': 0.0
            }
        
        return {
            'aircraft_per_hour': aircraft_count / time_period_hours,
            'aircraft_per_nm': aircraft_count / route_length_nm,
            'density_index': aircraft_count / (time_period_hours * route_length_nm)
        }
    
    @staticmethod
    def compare_safety_scenarios(
        scenario1: Dict,
        scenario2: Dict,
        scenario1_name: str = 'Before',
        scenario2_name: str = 'After'
    ) -> Dict:
        """
        Compare safety metrics between two scenarios
        
        Parameters:
        -----------
        scenario1 : dict
            First scenario metrics
        scenario2 : dict
            Second scenario metrics
        scenario1_name : str
            Name of first scenario
        scenario2_name : str
            Name of second scenario
            
        Returns:
        --------
        dict : Comparison results
        """
        risk1 = scenario1.get('collision_risk', 0)
        risk2 = scenario2.get('collision_risk', 0)
        
        if risk1 == 0:
            improvement = float('inf') if risk2 < risk1 else 0
        else:
            improvement = ((risk1 - risk2) / risk1) * 100
        
        return {
            'scenarios': {
                scenario1_name: scenario1,
                scenario2_name: scenario2
            },
            'improvement_percentage': improvement,
            'safer_scenario': scenario1_name if risk1 < risk2 else scenario2_name,
            'both_safe': (
                scenario1.get('meets_safety', False) and 
                scenario2.get('meets_safety', False)
            )
        }
