# Code for handling the kinematics of polargraph robots
#
# Polargraph (also known as wall plotter or cable-driven plotter)
# uses two motors mounted at the top corners to control a pen/gripper
# via strings/cables.
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math

from klippy import stepper


class PolargraphKinematics:
    """Polargraph (wall plotter) kinematics.
    
    Configuration example:
    [printer]
    kinematics: polargraph
    
    [polargraph]
    # Distance between the two motor centers (mm)
    motor_distance_x: 1000.0
    # Y offset from motor center to home position (mm)
    motor_offset_y: 50.0
    # Maximum belt/cable length (mm)
    max_belt_length: 1200.0
    # Segments per second for smooth curves
    segments_per_second: 5
    
    [stepper_left]   # Left motor
    ...
    
    [stepper_right]  # Right motor
    ...
    
    [stepper_z]      # Z axis (optional, for pen lift)
    ...
    """

    def __init__(self, toolhead, config):
        self.printer = config.get_printer()
        
        # Read polargraph configuration
        pg_config = config.getsection("polargraph")
        self.motor_distance_x = pg_config.getfloat("motor_distance_x", above=0.0)
        self.motor_offset_y = pg_config.getfloat("motor_offset_y", 0.0)
        self.max_belt_length = pg_config.getfloat(
            "max_belt_length", self.motor_distance_x * 1.2, above=0.0
        )
        self.segments_per_second = pg_config.getfloat(
            "segments_per_second", 5.0, above=0.0
        )
        
        # Setup steppers (left, right, and optional Z)
        self.stepper_left = stepper.LookupMultiRail(
            config.getsection("stepper_left")
        )
        self.stepper_right = stepper.LookupMultiRail(
            config.getsection("stepper_right")
        )
        
        # Z stepper is optional
        self.stepper_z = None
        if config.has_section("stepper_z"):
            self.stepper_z = stepper.LookupMultiRail(
                config.getsection("stepper_z")
            )
        
        self.steppers = [self.stepper_left, self.stepper_right]
        if self.stepper_z:
            self.steppers.append(self.stepper_z)
        
        # Configure stepper kinematics
        ffi_main, ffi_lib = chelper.get_ffi()
        for s in self.steppers:
            sk = ffi_main.gc(
                ffi_lib.cartesian_stepper_alloc(b"z"), ffi_lib.free
            )
            s.set_stepper_kinematics(sk)
            s.set_trapq(toolhead.get_trapq())
            toolhead.register_step_generator(s.generate_steps)
        
        self.printer.register_event_handler(
            "stepper_enable:motor_off", self._motor_off
        )
        
        # Calculate home position (center bottom)
        self.home_x = self.motor_distance_x / 2.0
        self.home_y = -self.motor_offset_y
        
        # Calculate maximum reach
        half_x = self.motor_distance_x / 2.0
        max_y = math.sqrt(self.max_belt_length ** 2 - half_x ** 2) - self.motor_offset_y
        
        # Axis limits
        self.axes_min = toolhead.Coord(0.0, self.home_y, 0.0, 0.0)
        self.axes_max = toolhead.Coord(
            self.motor_distance_x,
            max_y,
            config.getfloat("max_z", 300.0, above=0.0) if self.stepper_z else 0.0,
            0.0
        )
        
        self.need_home = True
        self.supports_dual_carriage = False
        
        logging.info(
            "Polargraph: distance=%.1f offset_y=%.1f max_belt=%.1f",
            self.motor_distance_x, self.motor_offset_y, self.max_belt_length
        )

    def get_steppers(self):
        return [s for rail in self.steppers for s in rail.get_steppers()]

    def _cartesian_to_belts(self, x, y):
        """Convert Cartesian position to belt lengths."""
        # Left motor at (0, 0), right motor at (motor_distance_x, 0)
        left_len = math.sqrt(x ** 2 + (y + self.motor_offset_y) ** 2)
        right_len = math.sqrt(
            (self.motor_distance_x - x) ** 2 + (y + self.motor_offset_y) ** 2
        )
        return left_len, right_len

    def _belts_to_cartesian(self, left_len, right_len):
        """Convert belt lengths to Cartesian position."""
        # Using law of cosines to find x position
        d = self.motor_distance_x
        cos_angle = (left_len ** 2 + d ** 2 - right_len ** 2) / (2 * left_len * d)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        
        x = left_len * cos_angle
        y = math.sqrt(left_len ** 2 - x ** 2) - self.motor_offset_y
        
        return x, y

    def calc_position(self, stepper_positions):
        """Calculate Cartesian position from stepper positions."""
        left_pos = stepper_positions[self.stepper_left.get_name()]
        right_pos = stepper_positions[self.stepper_right.get_name()]
        
        # Convert stepper positions to belt lengths
        left_len = left_pos  # Already in mm
        right_len = right_pos
        
        x, y = self._belts_to_cartesian(left_len, right_len)
        z = stepper_positions[self.stepper_z.get_name()] if self.stepper_z else 0.0
        
        return [x, y, z]

    def set_position(self, newpos, homing_axes):
        """Set position for each rail."""
        for rail in self.steppers:
            rail.set_position(newpos)
        if 0 in homing_axes or 1 in homing_axes or 2 in homing_axes:
            self.need_home = False

    def clear_homing_state(self, axes):
        """Clear homing state for specified axes."""
        if 0 in axes or 1 in axes or 2 in axes:
            self.need_home = True

    def home(self, homing_state):
        """Home polargraph axes."""
        # Move to center position
        home_x = self.home_x
        home_y = self.home_y
        
        # Calculate belt lengths at home position
        left_len, right_len = self._cartesian_to_belts(home_x, home_y)
        
        # Set home position
        self.stepper_left.set_position([left_len, 0, 0])
        self.stepper_right.set_position([right_len, 0, 0])
        
        if self.stepper_z:
            # Home Z axis normally
            z_hi = self.stepper_z.get_homing_info()
            homepos = [None, None, z_hi.position_endstop, None]
            forcepos = list(homepos)
            if z_hi.positive_dir:
                forcepos[2] -= 1.5 * (z_hi.position_endstop - self.stepper_z.get_range()[0])
            else:
                forcepos[2] += 1.5 * (self.stepper_z.get_range()[1] - z_hi.position_endstop)
            homing_state.home_rails([self.stepper_z], forcepos, homepos)
        
        self.need_home = False
        self.printer.lookup_object("toolhead").set_position(
            [home_x, home_y, 0, 0]
        )

    def _motor_off(self, print_time):
        self.clear_homing_state((0, 1, 2))

    def check_move(self, move):
        """Validate move and apply constraints."""
        end_pos = move.end_pos
        
        # Check if homed
        if self.need_home:
            raise move.move_error("Must home polargraph first")
        
        # Check X limits
        if end_pos[0] < self.axes_min[0] or end_pos[0] > self.axes_max[0]:
            raise move.move_error()
        
        # Check Y limits
        if end_pos[1] < self.axes_min[1] or end_pos[1] > self.axes_max[1]:
            raise move.move_error()
        
        # Check belt lengths
        left_len, right_len = self._cartesian_to_belts(end_pos[0], end_pos[1])
        if left_len > self.max_belt_length or right_len > self.max_belt_length:
            raise move.move_error()
        
        # Check Z limits if Z stepper exists
        if self.stepper_z:
            if end_pos[2] < self.axes_min[2] or end_pos[2] > self.axes_max[2]:
                raise move.move_error()
            
            # Limit Z speed
            if move.axes_d[2]:
                z_ratio = move.move_d / abs(move.axes_d[2])
                move.limit_speed(
                    self.max_z_velocity * z_ratio, self.max_z_accel * z_ratio
                )

    def get_status(self, eventtime):
        axes = "xyz" if not self.need_home else ""
        return {
            "homed_axes": axes,
            "axis_minimum": self.axes_min,
            "axis_maximum": self.axes_max,
            "motor_distance_x": self.motor_distance_x,
            "motor_offset_y": self.motor_offset_y,
        }


def load_kinematics(toolhead, config):
    return PolargraphKinematics(toolhead, config)
