# Code for handling the kinematics of foam cutters
#
# Foam cutters use a hot wire to cut foam, typically with
# 4 axes: X, Y (wire top) and U, V (wire bottom).
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math

from klippy import stepper


class FoamCutterKinematics:
    """Foam cutter (XYUV) kinematics.
    
    Foam cutters use a hot wire with two endpoints controlled
    independently. This allows cutting complex 3D shapes from foam.
    
    Configuration example:
    [printer]
    kinematics: foam_cutter
    
    [foam_cutter]
    # Wire length (mm)
    wire_length: 500.0
    # Segments per second for smooth curves
    segments_per_second: 10
    
    [stepper_x]   # Wire top X
    ...
    
    [stepper_y]   # Wire top Y
    ...
    
    [stepper_u]   # Wire bottom X
    ...
    
    [stepper_v]   # Wire bottom Y
    ...
    """

    def __init__(self, toolhead, config):
        self.printer = config.get_printer()
        
        # Read foam cutter configuration
        fc_config = config.getsection("foam_cutter")
        self.wire_length = fc_config.getfloat("wire_length", 500.0, above=0.0)
        self.segments_per_second = fc_config.getfloat(
            "segments_per_second", 10.0, above=0.0
        )
        
        # Setup steppers (X, Y for top, U, V for bottom)
        self.steppers = [
            stepper.LookupMultiRail(config.getsection("stepper_" + n))
            for n in "xyuv"
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
        
        # Axis limits
        ranges = [r.get_range() for r in self.steppers]
        self.axes_min = toolhead.Coord(*[r[0] for r in ranges], e=0.0)
        self.axes_max = toolhead.Coord(*[r[1] for r in ranges], e=0.0)
        
        self.limits = [(1.0, -1.0)] * 4
        self.need_home = True
        self.supports_dual_carriage = False
        
        logging.info(
            "Foam cutter: wire_length=%.1f", self.wire_length
        )

    def get_steppers(self):
        return [s for rail in self.steppers for s in rail.get_steppers()]

    def calc_position(self, stepper_positions):
        """Calculate Cartesian position from stepper positions."""
        # For foam cutter, we return the average of top and bottom positions
        x_top = stepper_positions[self.steppers[0].get_name()]
        y_top = stepper_positions[self.steppers[1].get_name()]
        x_bot = stepper_positions[self.steppers[2].get_name()]
        y_bot = stepper_positions[self.steppers[3].get_name()]
        
        # Average position
        x = (x_top + x_bot) / 2
        y = (y_top + y_bot) / 2
        z = 0.0  # Z is not used in foam cutting
        
        return [x, y, z]

    def update_limits(self, i, range):
        l, h = self.limits[i]
        if l <= h:
            self.limits[i] = range

    def set_position(self, newpos, homing_axes):
        for i, rail in enumerate(self.steppers):
            rail.set_position(newpos)
        for axis in homing_axes:
            if axis < 4:
                self.limits[axis] = self.steppers[axis].get_range()
        if homing_axes:
            self.need_home = False

    def clear_homing_state(self, axes):
        for i, _ in enumerate(self.limits):
            if i in axes:
                self.limits[i] = (1.0, -1.0)

    def home(self, homing_state):
        """Home foam cutter axes."""
        # Home all axes independently
        for axis in homing_state.get_axes():
            if axis < 4:
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

    def _motor_off(self, print_time):
        self.clear_homing_state((0, 1, 2, 3))

    def check_move(self, move):
        end_pos = move.end_pos
        
        # Check all axis limits
        for i in range(4):
            if (end_pos[i] < self.limits[i][0] or 
                end_pos[i] > self.limits[i][1]):
                if self.limits[i][0] > self.limits[i][1]:
                    raise move.move_error("Must home axis first")
                raise move.move_error()
        
        # Calculate wire length and check it doesn't exceed maximum
        x_top = end_pos[0]
        y_top = end_pos[1]
        x_bot = end_pos[2]
        y_bot = end_pos[3]
        
        dx = x_top - x_bot
        dy = y_top - y_bot
        wire_len = math.sqrt(dx * dx + dy * dy)
        
        if wire_len > self.wire_length:
            raise move.move_error("Wire length exceeded")

    def get_status(self, eventtime):
        axes = [a for a, (l, h) in zip("xyuv", self.limits) if l <= h]
        return {
            "homed_axes": "".join(axes),
            "axis_minimum": self.axes_min,
            "axis_maximum": self.axes_max,
            "wire_length": self.wire_length,
        }


def load_kinematics(toolhead, config):
    return FoamCutterKinematics(toolhead, config)
