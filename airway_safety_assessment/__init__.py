"""
Airway Safety Assessment System
항공로 안전성 평가 시스템

Main module for conducting quantitative safety assessments of airways
using Reich Collision Risk Model based on ADS-B data
"""

from .core import ReichCRM, ModifiedReichCRM, SafetyMetrics
from .data import OpenSkyClient, AirwayDataProcessor
from .utils import DistributionFitter, DataAnalyzer
from .config import (
    get_airway_config,
    list_available_airways,
    get_active_airways,
    SAFETY_PARAMETERS
)

__version__ = '1.0.0'
__author__ = 'Airway Safety Assessment Team'

__all__ = [
    'ReichCRM',
    'ModifiedReichCRM',
    'SafetyMetrics',
    'OpenSkyClient',
    'AirwayDataProcessor',
    'DistributionFitter',
    'DataAnalyzer',
    'get_airway_config',
    'list_available_airways',
    'get_active_airways',
    'SAFETY_PARAMETERS',
    'AirwaySafetyAssessment'
]


class AirwaySafetyAssessment:
    """
    Main class for airway safety assessment
    항공로 안전성 평가 메인 클래스
    
    Integrates all modules for complete safety analysis workflow
    """
    
    def __init__(self, airway_name: str):
        """
        Initialize safety assessment for specific airway
        
        Parameters:
        -----------
        airway_name : str
            Name of the airway to assess (e.g., 'Y711')
        """
        self.airway_name = airway_name
        self.config = get_airway_config(airway_name)
        
        if not self.config:
            raise ValueError(f"Airway '{airway_name}' not found in configuration")
        
        self.processor = AirwayDataProcessor(self.config)
        self.crm = ReichCRM()
        self.modified_crm = ModifiedReichCRM()
        self.results = {}
        
    def process_trajectory_data(self, trajectories: list) -> dict:
        """
        Process trajectory data and extract required parameters
        
        Parameters:
        -----------
        trajectories : list
            List of trajectory dictionaries
        
        Returns:
        --------
        dict : Processed parameters for safety assessment
        """
        import numpy as np
        
        # Filter trajectories by route
        filtered_traj = self.processor.filter_trajectories_by_route(trajectories)
        
        if len(filtered_traj) == 0:
            raise ValueError("No trajectories found on specified route")
        
        # Extract lateral deviations
        lateral_deviations = self.processor.extract_lateral_deviations(filtered_traj)
        
        # Fit distribution and calculate Py(Sy)
        fitter = DistributionFitter(lateral_deviations)
        fitter.fit_all_distributions()
        best_model = fitter.select_best_model()
        
        from .core.reich_crm import LateralOverlapCalculator
        Py_Sy = LateralOverlapCalculator.calculate_Py_Sy(
            lateral_deviations,
            self.config.get('separation_nm', 6.0),
            best_model
        )
        
        # Extract ground speeds
        ground_speeds = self.processor.extract_ground_speeds(filtered_traj)
        speed_stats = SafetyMetrics.calculate_ground_speed_stats(ground_speeds)
        
        # Extract aircraft types
        aircraft_types, counts = self.processor.extract_aircraft_types(filtered_traj)
        dimensions = SafetyMetrics.calculate_aircraft_dimensions(aircraft_types, counts)
        
        # Extract altitude change times
        alt_change_times, total_times = self.processor.extract_altitude_change_times(filtered_traj)
        Pi = self.modified_crm.calculate_Pi(alt_change_times, total_times) if len(alt_change_times) > 0 else 0.1
        
        # Calculate lateral occupancy (example with waypoint crossing)
        from .core.reich_crm import LateralOccupancyCalculator
        
        # Simplified occupancy calculation
        E_opp = 0.1  # Placeholder - would need waypoint crossing analysis
        E_same = 0.05  # Placeholder
        
        return {
            'Py_Sy': Py_Sy,
            'Pz_0': SAFETY_PARAMETERS['Pz_0'],
            'lambda_x': dimensions['lambda_x'],
            'lambda_y': dimensions['lambda_y'],
            'lambda_z': dimensions['lambda_z'],
            'V': speed_stats['mean'],
            'Sx': SAFETY_PARAMETERS['Sx'],
            'E_opp': E_opp,
            'E_same': E_same,
            'Pi': Pi,
            'lateral_deviations': lateral_deviations,
            'best_distribution': best_model,
            'aircraft_count': len(filtered_traj),
            'speed_stats': speed_stats
        }
    
    def assess_safety(self, parameters: dict, use_modified: bool = False) -> dict:
        """
        Conduct safety assessment using Reich CRM
        
        Parameters:
        -----------
        parameters : dict
            Processed parameters from process_trajectory_data
        use_modified : bool
            If True, use Modified Reich CRM for altitude changes
        
        Returns:
        --------
        dict : Safety assessment results
        """
        if use_modified:
            # Use Modified Reich CRM
            result = self.modified_crm.calculate_collision_risk_with_altitude_change(
                Py_Sy=parameters['Py_Sy'],
                Pz_0=parameters['Pz_0'],
                lambda_x=parameters['lambda_x'],
                lambda_y=parameters['lambda_y'],
                lambda_z=parameters['lambda_z'],
                Sx=parameters['Sx'],
                E_opp=parameters['E_opp'],
                Pi=parameters['Pi'],
                V=parameters['V']
            )
        else:
            # Use Standard Reich CRM
            result = self.crm.calculate_collision_risk(
                Py_Sy=parameters['Py_Sy'],
                Pz_0=parameters['Pz_0'],
                lambda_x=parameters['lambda_x'],
                lambda_y=parameters['lambda_y'],
                lambda_z=parameters['lambda_z'],
                Sx=parameters['Sx'],
                E_same=parameters['E_same'],
                E_opp=parameters['E_opp'],
                delta_V=parameters['V'] * 0.1,  # Assume 10% speed difference
                V=parameters['V']
            )
        
        # Add evaluation
        evaluation = SafetyMetrics.evaluate_safety_compliance(result['collision_risk'])
        result.update(evaluation)
        
        self.results = result
        return result
    
    def generate_report(self) -> str:
        """
        Generate formatted safety assessment report
        
        Returns:
        --------
        str : Formatted report text
        """
        if not self.results:
            return "No assessment results available. Run assess_safety() first."
        
        report = f"""
{'='*70}
AIRWAY SAFETY ASSESSMENT REPORT
항공로 안전성 평가 보고서
{'='*70}

Airway: {self.airway_name}
Route Type: {self.config.get('type', 'N/A')}
Description: {self.config.get('description', 'N/A')}

{'='*70}
ASSESSMENT RESULTS
{'='*70}

Collision Risk: {self.results['collision_risk']:.2e} per flight hour
Target Level of Safety (TLS): {self.results['TLS']:.2e} per flight hour
Risk Ratio (Risk/TLS): {self.results.get('ratio', 0):.4f}

Safety Status: {'✓ MEETS SAFETY STANDARD' if self.results['meets_safety'] else '✗ DOES NOT MEET SAFETY STANDARD'}
Safety Level: {self.results.get('safety_level', 'N/A')}
Safety Margin: {self.results.get('safety_margin', 0):.2e}

{'='*70}
PARAMETERS USED
{'='*70}

"""
        
        if 'components' in self.results:
            for key, value in self.results['components'].items():
                if isinstance(value, float):
                    report += f"{key}: {value:.6f}\n"
                else:
                    report += f"{key}: {value}\n"
        
        report += f"\n{'='*70}\n"
        
        return report
    
    @staticmethod
    def list_available_airways() -> list:
        """Get list of available airways"""
        return list_available_airways()
    
    @staticmethod
    def get_active_airways() -> list:
        """Get list of active airways"""
        return get_active_airways()
