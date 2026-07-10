#!/usr/bin/env python3
# Test script for new features: dummy thermistor, cold extruder, and new kinematics

import sys
import os
import unittest

# Add klippy to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestDummyThermistor(unittest.TestCase):
    """Test dummy thermistor sensor functionality."""
    
    def test_import(self):
        """Test that dummy_thermistor module can be imported."""
        try:
            from klippy.extras import dummy_thermistor
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import dummy_thermistor: {e}")
    
    def test_sensor_factory(self):
        """Test that dummy_thermistor registers as a sensor factory."""
        try:
            from klippy.extras import dummy_thermistor
            # Check that load_config function exists
            self.assertTrue(hasattr(dummy_thermistor, 'load_config'))
        except Exception as e:
            self.fail(f"Failed to check sensor factory: {e}")

class TestNullHeater(unittest.TestCase):
    """Test null heater for cold extruders."""
    
    def test_import(self):
        """Test that NullHeater can be imported."""
        try:
            from klippy.extras.heaters import NullHeater
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import NullHeater: {e}")
    
    def test_null_heater_attributes(self):
        """Test NullHeater has required attributes."""
        try:
            from klippy.extras.heaters import NullHeater
            heater = NullHeater()
            
            # Check required attributes
            self.assertTrue(heater.can_extrude)
            self.assertTrue(heater.cold_extrude)
            self.assertEqual(heater.min_temp, 0.0)
            self.assertEqual(heater.max_temp, 100.0)
        except Exception as e:
            self.fail(f"Failed to test NullHeater attributes: {e}")

class TestKinematics(unittest.TestCase):
    """Test new kinematics modules."""
    
    def test_scara_import(self):
        """Test SCARA kinematics can be imported."""
        try:
            from klippy.kinematics import scara
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import scara kinematics: {e}")
    
    def test_tpara_import(self):
        """Test TPARA kinematics can be imported."""
        try:
            from klippy.kinematics import tpara
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import tpara kinematics: {e}")
    
    def test_polargraph_import(self):
        """Test Polargraph kinematics can be imported."""
        try:
            from klippy.kinematics import polargraph
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import polargraph kinematics: {e}")
    
    def test_belt_import(self):
        """Test Belt kinematics can be imported."""
        try:
            from klippy.kinematics import belt
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import belt kinematics: {e}")
    
    def test_robot_arm_import(self):
        """Test Robot Arm kinematics can be imported."""
        try:
            from klippy.kinematics import robot_arm
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import robot_arm kinematics: {e}")
    
    def test_foam_cutter_import(self):
        """Test Foam Cutter kinematics can be imported."""
        try:
            from klippy.kinematics import foam_cutter
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import foam_cutter kinematics: {e}")
    
    def test_core_variants_import(self):
        """Test Core kinematics variants can be imported."""
        try:
            from klippy.kinematics import coreyz
            from klippy.kinematics import coreyx
            from klippy.kinematics import corezx
            from klippy.kinematics import corezy
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import core kinematics variants: {e}")

if __name__ == '__main__':
    unittest.main()
