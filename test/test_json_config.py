import pathlib
import typing

import pytest
from klippy_testing import PrinterShim


def test_json_config_loading(
    config_root: typing.Annotated[pathlib.Path, "test_configs/json_config"],
):
    """Test that JSON config files can be loaded correctly."""
    start_args = {"config_file": str(config_root / "printer.json")}
    with PrinterShim(start_args) as printer:
        config = printer.load_config()
        
        # Test that printer section is loaded correctly
        printer_section = config.getsection("printer")
        assert printer_section.get("kinematics") == "cartesian"
        assert printer_section.getint("max_velocity") == 300
        assert printer_section.getint("max_accel") == 3000
        
        # Test that stepper sections are loaded correctly
        stepper_x = config.getsection("stepper_x")
        assert stepper_x.get("step_pin") == "PF0"
        assert stepper_x.getint("microsteps") == 16
        assert stepper_x.getint("position_max") == 200
        
        # Test that extruder section is loaded correctly
        extruder = config.getsection("extruder")
        assert extruder.getfloat("rotation_distance") == 33.5
        assert extruder.getfloat("nozzle_diameter") == 0.4
        assert extruder.get("sensor_type") == "EPCOS 100K B57560G104F"
        
        # Test that boolean values are converted correctly
        probe = config.getsection("probe")
        assert probe.getboolean("drop_first_result") is True
        
        # Test that constants section works
        constants = config.getsection("constants")
        assert constants.get("false") == "False"


def test_json_config_autosave(
    config_root: typing.Annotated[pathlib.Path, "test_configs/json_config"],
):
    """Test that JSON config autosave works correctly."""
    start_args = {"config_file": str(config_root / "printer.json")}
    with PrinterShim(start_args) as printer:
        pconfig = printer.lookup_object("configfile")
        config = printer.load_config()
        
        # Test initial value
        assert (
            config.getsection("printer").getint("max_velocity") == 300
        )
        
        # Set a new value
        pconfig.set("printer", "max_velocity", "500")
        assert pconfig.status_save_pending == {
            "printer": {"max_velocity": "500"}
        }
        
        # Save config
        with pytest.raises(Restart):
            printer.call("SAVE_CONFIG")
    
    # Verify autosave file was created
    autosave_path = config_root / "printer.autosave.json"
    assert autosave_path.exists()
    
    # Reload and verify the saved value
    with PrinterShim(start_args) as printer:
        config = printer.load_config()
        assert (
            config.getsection("printer").getint("max_velocity") == 500
        )
    
    # Clean up autosave file
    if autosave_path.exists():
        autosave_path.unlink()
