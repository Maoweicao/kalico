#!/usr/bin/env python3
"""Simple test script for JSON config loading."""
import sys
import os
import pathlib

# Add the project root to the path
sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent / "test"))

from klippy_testing.shims import PrinterShim

def test_json_config():
    """Test JSON config loading."""
    config_dir = pathlib.Path(__file__).parent / "test" / "test_configs" / "json_config"
    start_args = {"config_file": str(config_dir / "printer.json")}
    
    print("Testing JSON config loading...")
    
    try:
        with PrinterShim(start_args) as printer:
            config = printer.load_config()
            
            # Test printer section
            printer_section = config.getsection("printer")
            print(f"printer.kinematics = {printer_section.get('kinematics')}")
            print(f"printer.max_velocity = {printer_section.getint('max_velocity')}")
            
            # Test stepper section
            stepper_x = config.getsection("stepper_x")
            print(f"stepper_x.step_pin = {stepper_x.get('step_pin')}")
            print(f"stepper_x.microsteps = {stepper_x.getint('microsteps')}")
            
            # Test extruder section
            extruder = config.getsection("extruder")
            print(f"extruder.rotation_distance = {extruder.getfloat('rotation_distance')}")
            print(f"extruder.nozzle_diameter = {extruder.getfloat('nozzle_diameter')}")
            
            # Test boolean conversion
            probe = config.getsection("probe")
            print(f"probe.drop_first_result = {probe.getboolean('drop_first_result')}")
            
            print("✓ JSON config loading test passed!")
            return True
            
    except Exception as e:
        print(f"✗ JSON config loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_config()
    sys.exit(0 if success else 1)
