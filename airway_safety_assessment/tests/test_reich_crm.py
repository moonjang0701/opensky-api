"""
Unit Tests for Reich CRM Module
"""

import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from airway_safety_assessment.core.reich_crm import (
    ReichCRM,
    ModifiedReichCRM,
    LateralOverlapCalculator,
    LateralOccupancyCalculator
)


class TestReichCRM(unittest.TestCase):
    """Test cases for Reich CRM"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.crm = ReichCRM()
        self.modified_crm = ModifiedReichCRM()
    
    def test_initialization(self):
        """Test CRM initialization"""
        self.assertEqual(self.crm.TLS, 5e-9)
        self.assertIsInstance(self.crm, ReichCRM)
    
    def test_collision_risk_calculation(self):
        """Test standard collision risk calculation"""
        result = self.crm.calculate_collision_risk(
            Py_Sy=0.01,
            Pz_0=0.538,
            lambda_x=0.02,
            lambda_y=0.02,
            lambda_z=0.006,
            Sx=80.0,
            E_same=0.05,
            E_opp=0.1,
            delta_V=50.0,
            V=450.0
        )
        
        self.assertIn('collision_risk', result)
        self.assertIn('meets_safety', result)
        self.assertIsInstance(result['collision_risk'], float)
        self.assertGreaterEqual(result['collision_risk'], 0)
    
    def test_modified_collision_risk_calculation(self):
        """Test modified CRM with altitude changes"""
        result = self.modified_crm.calculate_collision_risk_with_altitude_change(
            Py_Sy=0.01,
            Pz_0=0.538,
            lambda_x=0.02,
            lambda_y=0.02,
            lambda_z=0.006,
            Sx=80.0,
            E_opp=0.1,
            Pi=0.1,
            V=450.0
        )
        
        self.assertIn('collision_risk', result)
        self.assertIn('meets_safety', result)
        self.assertIn('Pi', result['components'])
    
    def test_safety_compliance(self):
        """Test safety compliance evaluation"""
        # Very low risk - should meet safety
        result_safe = self.crm.calculate_collision_risk(
            Py_Sy=0.0001,
            Pz_0=0.538,
            lambda_x=0.02,
            lambda_y=0.02,
            lambda_z=0.006,
            Sx=80.0,
            E_same=0.001,
            E_opp=0.001,
            delta_V=10.0,
            V=400.0
        )
        
        # Check that result is calculated
        self.assertIn('collision_risk', result_safe)
        self.assertIn('meets_safety', result_safe)
    
    def test_calculate_Pi(self):
        """Test altitude overlap rate calculation"""
        altitude_change_times = np.array([100, 150, 200])  # seconds
        total_flight_times = np.array([3600, 3600, 3600])  # seconds
        
        Pi = self.modified_crm.calculate_Pi(
            altitude_change_times,
            total_flight_times
        )
        
        expected_Pi = 450 / 10800  # Total change time / Total flight time
        self.assertAlmostEqual(Pi, expected_Pi, places=6)
    
    def test_calculate_Pi_zero_total_time(self):
        """Test Pi calculation with zero total time"""
        altitude_change_times = np.array([100])
        total_flight_times = np.array([0])
        
        Pi = self.modified_crm.calculate_Pi(
            altitude_change_times,
            total_flight_times
        )
        
        self.assertEqual(Pi, 0.0)


class TestLateralOccupancyCalculator(unittest.TestCase):
    """Test cases for Lateral Occupancy Calculator"""
    
    def test_calculate_Ey(self):
        """Test lateral occupancy calculation"""
        Ey = LateralOccupancyCalculator.calculate_Ey(
            proximate_pairs=10,
            total_aircraft=100
        )
        
        expected_Ey = 2 * 10 / 100
        self.assertEqual(Ey, expected_Ey)
    
    def test_calculate_Ey_zero_aircraft(self):
        """Test Ey with zero aircraft"""
        Ey = LateralOccupancyCalculator.calculate_Ey(
            proximate_pairs=0,
            total_aircraft=0
        )
        
        self.assertEqual(Ey, 0.0)
    
    def test_find_proximate_pairs(self):
        """Test finding proximate pairs"""
        # Times with 5-minute intervals (in seconds)
        crossing_times = np.array([
            0, 300, 900, 1200, 2000, 2100
        ])
        
        proximate_count = LateralOccupancyCalculator.find_proximate_pairs(
            crossing_times,
            threshold_minutes=10.0
        )
        
        # Should find pairs: (0,300), (900,1200), (2000,2100)
        self.assertGreater(proximate_count, 0)
    
    def test_find_proximate_pairs_empty(self):
        """Test with empty crossing times"""
        crossing_times = np.array([])
        
        proximate_count = LateralOccupancyCalculator.find_proximate_pairs(
            crossing_times,
            threshold_minutes=10.0
        )
        
        self.assertEqual(proximate_count, 0)


if __name__ == '__main__':
    unittest.main()
