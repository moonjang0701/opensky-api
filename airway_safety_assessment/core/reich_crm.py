"""
Reich Collision Risk Model (CRM) Implementation
Reich 충돌 위험 모델 구현

Based on:
"Quantitative Safety Assessment and Effectiveness Analysis for Duplication of ATS Routes"
Park et al., 2024
"""

import numpy as np
from typing import Dict, Optional
from scipy import integrate


class ReichCRM:
    """
    Standard Reich Collision Risk Model
    표준 Reich 충돌 위험 모델
    
    Calculates collision risk per flight hour for parallel ATS routes
    평행 항공로에 대한 비행시간당 충돌 위험 계산
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Reich CRM with configuration
        
        Parameters:
        -----------
        config : dict, optional
            Configuration parameters for the model
        """
        self.config = config or {}
        
        # Target Level of Safety (TLS) - ICAO standard
        self.TLS = 5e-9  # collisions per flight hour
        
    def calculate_collision_risk(
        self,
        Py_Sy: float,
        Pz_0: float,
        lambda_x: float,
        lambda_y: float,
        lambda_z: float,
        Sx: float,
        E_same: float,
        E_opp: float,
        delta_V: float,
        V: float,
        y_dot: float = 75.0,  # knots
        z_dot: float = 1.5    # knots
    ) -> Dict[str, float]:
        """
        Calculate collision risk using standard Reich CRM
        
        Formula (Equation 1 from paper):
        Nay = Py(Sy) * Pz(0) * (λx / Sx) * 
              [ E(same) * { |ΔV| / (2λx) + |ẏ| / (2λy) + |ż| / (2λz) } +
                E(opp) * { 2|V| / (2λx) + |ẏ| / (2λy) + |ż| / (2λz) } ]
        
        Parameters:
        -----------
        Py_Sy : float
            Probability of lateral overlap
        Pz_0 : float
            Probability of vertical overlap
        lambda_x : float
            Average aircraft length (nm)
        lambda_y : float
            Average aircraft wingspan (nm)
        lambda_z : float
            Average aircraft height (nm)
        Sx : float
            Half of longitudinal separation minimum (nm)
        E_same : float
            Same-direction lateral occupancy
        E_opp : float
            Opposite-direction lateral occupancy
        delta_V : float
            Average relative speed for same direction (knots)
        V : float
            Average ground speed (knots)
        y_dot : float
            Average absolute relative cross-track speed (knots)
        z_dot : float
            Average absolute relative vertical speed (knots)
            
        Returns:
        --------
        dict : Dictionary containing collision risk and components
        """
        
        # Calculate longitudinal overlap probabilities
        Px_same = abs(delta_V) / (2 * lambda_x)
        Px_opp = 2 * abs(V) / (2 * lambda_x)
        
        # Calculate lateral overlap probability
        Py = abs(y_dot) / (2 * lambda_y)
        
        # Calculate vertical overlap probability
        Pz = abs(z_dot) / (2 * lambda_z)
        
        # Total overlap for same direction
        overlap_same = Px_same + Py + Pz
        
        # Total overlap for opposite direction
        overlap_opp = Px_opp + Py + Pz
        
        # Calculate collision risk (Nay)
        Nay = Py_Sy * Pz_0 * (lambda_x / Sx) * (
            E_same * overlap_same + E_opp * overlap_opp
        )
        
        return {
            'collision_risk': Nay,
            'TLS': self.TLS,
            'meets_safety': Nay < self.TLS,
            'components': {
                'Py_Sy': Py_Sy,
                'Pz_0': Pz_0,
                'lambda_x': lambda_x,
                'Sx': Sx,
                'E_same': E_same,
                'E_opp': E_opp,
                'overlap_same': overlap_same,
                'overlap_opp': overlap_opp
            }
        }


class ModifiedReichCRM(ReichCRM):
    """
    Modified Reich Collision Risk Model for Altitude Changes
    고도 변경을 고려한 수정된 Reich 충돌 위험 모델
    
    Used for opposite-direction traffic during altitude changes
    where aircraft may momentarily occupy the same flight level.
    """
    
    def calculate_collision_risk_with_altitude_change(
        self,
        Py_Sy: float,
        Pz_0: float,
        lambda_x: float,
        lambda_y: float,
        lambda_z: float,
        Sx: float,
        E_opp: float,
        Pi: float,  # Altitude overlap occurrence rate
        V: float,
        y_dot: float = 75.0,  # knots
        z_dot: float = 1.5    # knots
    ) -> Dict[str, float]:
        """
        Calculate collision risk using modified Reich CRM for altitude changes
        
        Formula (Equation 2 from paper):
        Nay = Pi * Py(Sy) * Pz(0) * (λx / Sx) * 
              E(opp) * { 2|V| / (2λx) + |ẏ| / (2λy) + |ż| / (2λz) }
        
        Parameters:
        -----------
        Pi : float
            Altitude overlap occurrence rate (Ti / Tn)
            - Ti: Total time spent changing altitudes
            - Tn: Total flight time
        ... (other parameters same as standard Reich CRM)
        
        Returns:
        --------
        dict : Dictionary containing collision risk and components
        """
        
        # Calculate longitudinal overlap probability (opposite direction)
        Px_opp = 2 * abs(V) / (2 * lambda_x)
        
        # Calculate lateral overlap probability
        Py = abs(y_dot) / (2 * lambda_y)
        
        # Calculate vertical overlap probability
        Pz = abs(z_dot) / (2 * lambda_z)
        
        # Total overlap for opposite direction
        overlap_opp = Px_opp + Py + Pz
        
        # Calculate collision risk with altitude change factor (Nay)
        Nay = Pi * Py_Sy * Pz_0 * (lambda_x / Sx) * E_opp * overlap_opp
        
        return {
            'collision_risk': Nay,
            'TLS': self.TLS,
            'meets_safety': Nay < self.TLS,
            'components': {
                'Pi': Pi,
                'Py_Sy': Py_Sy,
                'Pz_0': Pz_0,
                'lambda_x': lambda_x,
                'Sx': Sx,
                'E_opp': E_opp,
                'overlap_opp': overlap_opp
            }
        }
    
    def calculate_Pi(
        self,
        altitude_change_times: np.ndarray,
        total_flight_times: np.ndarray
    ) -> float:
        """
        Calculate altitude overlap occurrence rate (Pi)
        
        Formula (Equation 5 from paper):
        Pi = Ti / Tn
        
        Parameters:
        -----------
        altitude_change_times : np.ndarray
            Array of time spent changing altitudes for each flight (seconds)
        total_flight_times : np.ndarray
            Array of total flight times (seconds)
            
        Returns:
        --------
        float : Altitude overlap occurrence rate
        """
        Ti = np.sum(altitude_change_times)
        Tn = np.sum(total_flight_times)
        
        if Tn == 0:
            return 0.0
            
        return Ti / Tn


class LateralOverlapCalculator:
    """
    Calculator for lateral overlap probability Py(Sy)
    횡적 중첩 확률 계산기
    """
    
    @staticmethod
    def calculate_Py_Sy(
        lateral_deviations: np.ndarray,
        Sy: float,
        distribution_model: str = 'DDE'
    ) -> float:
        """
        Calculate probability of lateral overlap
        
        Formula (Equation 3 from paper):
        Py(Sy) ≈ 2λy * ∫[-∞,∞] fy(y1) * fy(Sy + y1) dy1
        
        Parameters:
        -----------
        lateral_deviations : np.ndarray
            Observed lateral deviations from route centerline (nm)
        Sy : float
            Lateral separation between parallel routes (nm)
        distribution_model : str
            Distribution model to use ('DE', 'N', 'NN', 'NDE', 'DDE')
            
        Returns:
        --------
        float : Lateral overlap probability
        """
        from ..utils.statistics import DistributionFitter
        
        fitter = DistributionFitter(lateral_deviations)
        pdf_func = fitter.fit_distribution(distribution_model)
        
        # Numerical integration for Py(Sy)
        def integrand(y1):
            return pdf_func(y1) * pdf_func(Sy + y1)
        
        # Calculate 2λy (approximate wingspan)
        lambda_y = np.std(lateral_deviations) if len(lateral_deviations) > 0 else 0.05
        
        result, _ = integrate.quad(
            integrand,
            -np.inf,
            np.inf,
            limit=100
        )
        
        return 2 * lambda_y * result


class LateralOccupancyCalculator:
    """
    Calculator for lateral occupancy (Ey)
    횡적 점유율 계산기
    """
    
    @staticmethod
    def calculate_Ey(
        proximate_pairs: int,
        total_aircraft: int
    ) -> float:
        """
        Calculate lateral occupancy using direct estimation method
        
        Formula (Equation 4 from paper):
        Ey = 2ny / n
        
        Parameters:
        -----------
        proximate_pairs : int
            Number of proximate aircraft pairs (ny)
        total_aircraft : int
            Total number of aircraft (n)
            
        Returns:
        --------
        float : Lateral occupancy
        """
        if total_aircraft == 0:
            return 0.0
            
        return (2 * proximate_pairs) / total_aircraft
    
    @staticmethod
    def find_proximate_pairs(
        waypoint_crossing_times: np.ndarray,
        threshold_minutes: float = 10.0
    ) -> int:
        """
        Find number of proximate aircraft pairs at waypoint
        
        Uses 'Direct estimation from the at waypoint crossing' method
        
        Parameters:
        -----------
        waypoint_crossing_times : np.ndarray
            Array of times when aircraft cross the waypoint (datetime or timestamp)
        threshold_minutes : float
            Time threshold for considering aircraft as proximate (minutes)
            
        Returns:
        --------
        int : Number of proximate pairs
        """
        if len(waypoint_crossing_times) < 2:
            return 0
        
        # Sort crossing times
        sorted_times = np.sort(waypoint_crossing_times)
        
        # Count proximate pairs
        proximate_count = 0
        threshold_seconds = threshold_minutes * 60
        
        for i in range(len(sorted_times) - 1):
            time_diff = sorted_times[i + 1] - sorted_times[i]
            if time_diff <= threshold_seconds:
                proximate_count += 1
                
        return proximate_count
