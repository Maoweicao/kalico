#!/usr/bin/env python3
"""Simple test script for JSON to CFG conversion - standalone version."""
import sys
import re
import configparser

error = configparser.Error

def _json_value_to_string(value):
    """Convert a JSON value to a string suitable for CFG format."""
    if isinstance(value, bool):
        return "True" if value else "False"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        return ", ".join(str(item) for item in value)
    elif isinstance(value, dict):
        raise error("Nested JSON objects not supported in config conversion")
    elif value is None:
        return ""
    return str(value)


def _json_to_cfg(json_data, source_file=""):
    """Convert JSON configuration data to CFG format string."""
    lines = []

    if "include" in json_data:
        includes = json_data["include"]
        if isinstance(includes, str):
            includes = [includes]
        for include_path in includes:
            lines.append(f"[include {include_path}]")
        lines.append("")

    for section, values in json_data.items():
        if section == "include":
            continue

        if not isinstance(values, dict):
            lines.append(f"[printer]")
            lines.append(f"{section}: {_json_value_to_string(values)}")
            lines.append("")
            continue

        lines.append(f"[{section}]")
        for key, value in values.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    lines.append(
                        f"{key}_{sub_key}: {_json_value_to_string(sub_value)}"
                    )
            else:
                lines.append(f"{key}: {_json_value_to_string(value)}")
        lines.append("")

    return "\n".join(lines)


def test_json_to_cfg():
    """Test JSON to CFG conversion."""
    print("Testing JSON to CFG conversion...")

    json_data = {
        "include": ["other.cfg"],
        "printer": {
            "kinematics": "cartesian",
            "max_velocity": 300,
            "max_accel": 3000
        },
        "extruder": {
            "step_pin": "PA4",
            "microsteps": 16,
            "rotation_distance": 33.5,
            "nozzle_diameter": 0.4
        },
        "probe": {
            "pin": "PH6",
            "z_offset": 1.15,
            "drop_first_result": True
        }
    }

    expected_cfg = """[include other.cfg]

[printer]
kinematics: cartesian
max_velocity: 300
max_accel: 3000

[extruder]
step_pin: PA4
microsteps: 16
rotation_distance: 33.5
nozzle_diameter: 0.4

[probe]
pin: PH6
z_offset: 1.15
drop_first_result: True"""

    try:
        result = _json_to_cfg(json_data)

        print("Generated CFG:")
        print(result)
        print("\nExpected CFG:")
        print(expected_cfg)

        result_lines = [line.strip() for line in result.split('\n') if line.strip()]
        expected_lines = [line.strip() for line in expected_cfg.split('\n') if line.strip()]

        if result_lines == expected_lines:
            print("\n[PASS] JSON to CFG conversion test passed!")
            return True
        else:
            print("\n[FAIL] JSON to CFG conversion test failed!")
            print(f"  Result lines ({len(result_lines)}): {result_lines}")
            print(f"  Expected lines ({len(expected_lines)}): {expected_lines}")
            for i in range(max(len(result_lines), len(expected_lines))):
                r = result_lines[i] if i < len(result_lines) else "<missing>"
                e = expected_lines[i] if i < len(expected_lines) else "<missing>"
                if r != e:
                    print(f"  Line {i}: '{r}' != '{e}'")
            return False

    except Exception as e:
        print(f"[FAIL] JSON to CFG conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_value_conversion():
    """Test JSON value conversion."""
    print("\nTesting JSON value conversion...")

    test_cases = [
        (True, "True"),
        (False, "False"),
        (42, "42"),
        (3.14, "3.14"),
        ("hello", "hello"),
        ([1, 2, 3], "1, 2, 3"),
        (None, ""),
    ]

    all_passed = True
    for value, expected in test_cases:
        result = _json_value_to_string(value)
        if result == expected:
            print(f"  [PASS] {repr(value)} -> {repr(result)}")
        else:
            print(f"  [FAIL] {repr(value)} -> {repr(result)} (expected {repr(expected)})")
            all_passed = False

    if all_passed:
        print("[PASS] JSON value conversion test passed!")
    else:
        print("[FAIL] JSON value conversion test failed!")
    return all_passed


def test_json_include_single_string():
    """Test that a single string include is wrapped into a list."""
    print("\nTesting single string include...")

    json_data = {
        "include": "single_file.cfg",
        "printer": {"kinematics": "cartesian"}
    }

    result = _json_to_cfg(json_data)
    if "[include single_file.cfg]" in result:
        print("[PASS] Single string include handled correctly!")
        return True
    else:
        print(f"[FAIL] Single string include not found in output:\n{result}")
        return False


def test_nested_object_flattening():
    """Test that nested JSON objects are flattened with underscore."""
    print("\nTesting nested object flattening...")

    json_data = {
        "display": {
            "lcd": {
                "rs_pin": "PA0",
                "e_pin": "PA1"
            }
        }
    }

    result = _json_to_cfg(json_data)
    if "lcd_rs_pin: PA0" in result and "lcd_e_pin: PA1" in result:
        print("[PASS] Nested object flattening works correctly!")
        return True
    else:
        print(f"[FAIL] Nested flattening failed:\n{result}")
        return False


def test_json_file_parse():
    """Test loading and converting an actual JSON file."""
    print("\nTesting JSON file parsing...")

    import json
    import os
    test_file = os.path.join(
        os.path.dirname(__file__),
        "test", "test_configs", "json_config", "printer.json"
    )

    if not os.path.exists(test_file):
        print(f"[SKIP] Test file not found: {test_file}")
        return True

    try:
        with open(test_file, "r") as f:
            json_data = json.load(f)

        result = _json_to_cfg(json_data, test_file)
        lines = [l for l in result.split('\n') if l.strip()]

        print(f"  Converted {len(json_data)} top-level keys to {len(lines)} CFG lines")

        # Verify key sections exist
        if "[printer]" in result and "[extruder]" in result and "[mcu]" in result:
            print("[PASS] JSON file parsed and converted correctly!")
            return True
        else:
            print(f"[FAIL] Missing expected sections in output")
            return False

    except Exception as e:
        print(f"[FAIL] JSON file parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    results = [
        test_json_to_cfg(),
        test_json_value_conversion(),
        test_json_include_single_string(),
        test_nested_object_flattening(),
        test_json_file_parse(),
    ]

    if all(results):
        print(f"\n[PASS] All {len(results)} tests passed!")
        sys.exit(0)
    else:
        failed = sum(1 for r in results if not r)
        print(f"\n[FAIL] {failed} of {len(results)} tests failed!")
        sys.exit(1)
