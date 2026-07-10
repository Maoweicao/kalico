# Code for handling the kinematics of belt printers
#
# Belt printers have an infinite Z axis (conveyor belt bed)
# and typically tilted at 45 degrees.
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math

from klippy import stepper


class BeltKinematics:
    """Belt printer (infinite Z) kinematics.
    
    Configuration example:
    [printer]
    kinematics: belt
    
    [belt]
    # Bed tilt angle in degrees (typically 45)
    bed_tilt: 45.0
    # Bed rotation axis (x or y)
    bed_rotation_axis: y
    # Segments per second for smooth curves
    segments_per_second: 10
    
    [stepper_x]
    ...
    
    [stepper_y]
    ...
    
    [stepper_z]   # This is the conveyor belt motor
    ...
    """

    def __init__(self, toolhead, config):
        self.printer = config.get_printer()
        
        # Read belt printer configuration
        belt_config = config.getsection("belt")
        self.bed_tilt = belt_config.getfloat("bed_tilt", 45.0)
        self.bed_rotation_axis = belt_config.getchoice(
            "bed_rotation_axis", {"x": "x", "y": "y"}, default="y"
        )
        self.segments_per_second = belt_config.getfloat(
            "segments_per_second", 10.0, above=0.0
        )
        
        # Convert tilt to radians for calculations
        self.tilt_rad = math.radians(self.bed_tilt)
        self.cos_tilt = math.cos(self.tilt_rad)
        self.sin_tilt = math.sin(self.tilt_rad)
        
        # Setup steppers (X, Y, Z/belt)
        self.steppers = [
            stepper.LookupMultiRail(config.getsection("stepper_" + n))
            for n in "xyz"
        ]
        
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
        
        # Setup boundary checks
        max_velocity, max_accel = toolhead.get_max_velocity()
        self.max_z_velocity = config.getfloat(
            "max_z_velocity", max_velocity, above=0.0, maxval=max_velocity
        )
        self.max_z_accel = config.getfloat(
            "max_z_accel", max_accel, above=0.0, maxval=max_accel
        )
        
        # Axis limits
        ranges = [r.get_range() for r in self.steppers]
        self.axes_min = toolhead.Coord(*[r[0] for r in ranges], e=0.0)
        self.axes_max = toolhead.Coord(*[r[1] for r in ranges], e=0.0)
        
        # Z is unlimited (infinite belt)
        self.axes_min = toolhead.Coord(self.axes_min[0], self.axes_min[1], -999999.0, 0.0)
        self.axes_max = toolhead.Coord(self.axes_max[0], self.axes_max[1], 999999.0, 0.0)
        
        self.limits = [(1.0, -1.0)] * 3
        self.need_home = True
        self.supports_dual_carriage = False
        
        logging.info(
            "Belt printer: tilt=%.1f° rotation_axis=%s",
            self.bed_tilt, self.bed_rotation_axis
        )

    def get_steppers(self):
        return [s for rail in self.steppers for s in rail.get_steppers()]

    def _apply_tilt_transform(self, pos):
        """Apply bed tilt transformation to position."""
        x, y, z = pos[0], pos[1], pos[2]
        
        if self.bed_rotation_axis == "y":
            # Rotate around Y axis
            new_x = x * self.cos_tilt + z * self.sin_tilt
            new_y = y
            new_z = -x * self.sin_tilt + z * self.cos_tilt
        else:
            # Rotate around X axis
            new_x = x
            new_y = y * self.cos_tilt - z * self.sin_tilt
            new_z = y * self.sin_tilt + z * self.cos_tilt
        
        return [new_x, new_y, new_z]

    def _remove_tilt_transform(self, pos):
        """Remove bed tilt transformation from position."""
        x, y, z = pos[0], pos[1], pos[2]
        
        if self.bed_rotation_axis == "y":
            # Inverse rotate around Y axis
            new_x = x * self.cos_tilt - z * self.sin_tilt
            new_y = y
            new_z = x * self.sin_tilt + z * self.cos_tilt
        else:
            # Inverse rotate around X axis
            new_x = x
            new_y = y * self.cos_tilt + z * self.sin_tilt
            new_z = -y * self.sin_tilt + z * self.cos_tilt
        
        return [new_x, new_y, new_z]

    def calc_position(self, stepper_positions):
        """Calculate Cartesian position from stepper positions."""
        raw_pos = [
            stepper_positions[rail.get_name()]
            for rail in self.steppers
        ]
        return self._remove_tilt_transform(raw_pos)

    def update_limits(self, i, range):
        l, h = self.limits[i]
        if l <= h:
            self.limits[i] = range

    def set_position(self, newpos, homing_axes):
        for i, rail in enumerate(self.steppers):
            rail.set_position(newpos)
        for axis in homing_axes:
            self.limits[axis] = self.steppers[axis].get_range()
        if homing_axes:
            self.need_home = False

    def note_z_not_homed(self):
        self.clear_homing_state([2])

    def clear_homing_state(self, axes):
        for i, _ in enumerate(self.limits):
            if i in axes:
                self.limits[i] = (1.0, -1.0)

    def home(self, homing_state):
        # Home X and Y normally
        for axis in homing_state.get_axes():
            if axis < 2:  # X or Y
                rail = self.steppers[axis]
                hi = rail.get_homing_info()
                position_min, position_max = rail.get_range()
                homepos = [None, None, None, None]
                homepos[axis] = hi.position_endstop
                forcepos = list(homepos)
                if hi.positive_dir:
                    forcepos[axis] -= 1.5 * (hi.position_endstop - position_min)
                else:
                    forcepos[axis] += 1.5 * (position_max - hi.position_endstop)
                homing_state.home_rails([rail], forcepos, homepos)
        
        # Z doesn't need homing (infinite belt)
        if 2 in homing_state.get_axes():
            self.set_position([0, 0, 0, 0], [2])
            homing_state.set_axes([])

    def _motor_off(self, print_time):
        self.clear_homing_state((0, 1, 2))

    def check_move(self, move):
        end_pos = move.end_pos
        
        # Check X and Y limits
        if (end_pos[0] < self.limits[0][0] or end_pos[0] > self.limits[0][1] or
            end_pos[1] < self.limits[1][0] or end_pos[1] > self.limits[1][1]):
            if self.limits[0][0] > self.limits[0][1] or self.limits[1][0] > self.limits[1][1]:
                raise move.move_error("Must home axis first")
            raise move.move_error()
        
        # Z is unlimited on belt printers
        # But we still need to apply tilt transformation for speed limiting
        
        # Calculate effective Z movement considering tilt
        if move.axes_d[2]:
            z_ratio = move.move_d / abs(move.axes_d[2])
            move.limit_speed(
                self.max_z_velocity * z_ratio, self.max_z_accel * z_ratio
            )

    def get_status(self, eventtime):
        axes = [a for a, (l, h) in zip("xyz", self.limits) if l <= h]
        return {
            "homed_axes": "".join(axes),
            "axis_minimum": self.axes_min,
            "axis_maximum": self.axes_max,
            "bed_tilt": self.bed_tilt,
        }


def load_kinematics(toolhead, config):
    return BeltKinematics(toolhead, config)
