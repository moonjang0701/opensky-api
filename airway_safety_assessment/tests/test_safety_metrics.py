"""
Unit Tests for Safety Metrics Module
"""

import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from airway_safety_assessment.core.safety_metrics import SafetyMetrics


class TestSafetyMetrics(unittest.TestCase):
    """Test cases for Safety Metrics"""
    
    def test_calculate_aircraft_dimensions(self):
        """Test aircraft dimensions calculation"""
        aircraft_types = ['B738', 'A321', 'B77W']
        counts = [50, 30, 20]
        
        dimensions = SafetyMetrics.calculate_aircraft_dimensions(
            aircraft_types, counts
        )
        
        self.assertIn('lambda_x', dimensions)
        self.assertIn('lambda_y', dimensions)
        self.assertIn('lambda_z', dimensions)
        self.assertGreater(dimensions['lambda_x'], 0)
        self.assertGreater(dimensions['lambda_y'], 0)
        self.assertGreater(dimensions['lambda_z'], 0)
    
    def test_calculate_ground_speed_stats(self):
        """Test ground speed statistics"""
        speeds = np.array([400, 420, 450, 480, 500])
        
        stats = SafetyMetrics.calculate_ground_speed_stats(speeds)
        
        self.assertIn('mean', stats)
        self.assertIn('median', stats)
        self.assertIn('std', stats)
        self.assertEqual(stats['mean'], 450.0)
        self.assertEqual(stats['median'], 450.0)
    
    def test_calculate_vertical_overlap_probability(self):
        """Test vertical overlap probability"""
        Pz = SafetyMetrics.calculate_vertical_overlap_probability()
        
        # Should return standard value
        self.assertEqual(Pz, 0.538)
    
    def test_evaluate_safety_compliance_safe(self):
        """Test safety evaluation - safe scenario"""
        result = SafetyMetrics.evaluate_safety_compliance(
            collision_risk=1e-10,
            TLS=5e-9
        )
        
        self.assertTrue(result['meets_safety'])
        self.assertEqual(result['safety_level'], 'Excellent')
        self.assertGreater(result['safety_margin'], 0)
    
    def test_evaluate_safety_compliance_unsafe(self):
        """Test safety evaluation - unsafe scenario"""
        result = SafetyMetrics.evaluate_safety_compliance(
            collision_risk=1e-8,
            TLS=5e-9
        )
        
        self.assertFalse(result['meets_safety'])
        self.assertEqual(result['safety_level'], 'Unsafe')
        self.assertLess(result['safety_margin'], 0)
    
    def test_calculate_traffic_density(self):
        """Test traffic density calculation"""
        density = SafetyMetrics.calculate_traffic_density(
            aircraft_count=100,
            time_period_hours=24.0,
            route_length_nm=200.0
        )
        
        self.assertIn('aircraft_per_hour', density)
        self.assertIn('aircraft_per_nm', density)
        self.assertAlmostEqual(density['aircraft_per_hour'], 100/24)
        self.assertAlmostEqual(density['aircraft_per_nm'], 100/200)
    
    def test_compare_safety_scenarios(self):
        """Test scenario comparison"""
        scenario1 = {
            'collision_risk': 2e-9,
            'meets_safety': True
        }
        scenario2 = {
            'collision_risk': 1e-9,
            'meets_safety': True
        }
        
        comparison = SafetyMetrics.compare_safety_scenarios(
            scenario1, scenario2,
            'Before', 'After'
        )
        
        self.assertIn('improvement_percentage', comparison)
        self.assertEqual(comparison['safer_scenario'], 'After')
        self.assertTrue(comparison['both_safe'])
        self.assertGreater(comparison['improvement_percentage'], 0)


if __name__ == '__main__':
    unittest.main()
