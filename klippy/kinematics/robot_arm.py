# Code for handling the kinematics of articulated robot arms
#
# Articulated robot arms have multiple rotational joints
# (typically 6 axes for full freedom of movement).
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math

from klippy import stepper


class RobotArmKinematics:
    """Articulated robot arm kinematics.
    
    This implements a simplified 3-axis articulated robot arm.
    For full 6-axis arms, additional configuration would be needed.
    
    Configuration example:
    [printer]
    kinematics: robot_arm
    
    [robot_arm]
    # DH parameters (Denavit-Hartenberg)
    d1: 100       # Base height (mm)
    a1: 50        # Link 1 length (mm)
    a2: 200       # Link 2 length (mm)
    a3: 150       # Link 3 length (mm)
    segments_per_second: 100
    
    [stepper_a]   # Base rotation
    ...
    
    [stepper_b]   # Shoulder rotation
    ...
    
    [stepper_c]   # Elbow rotation
    ...
    """

    def __init__(self, toolhead, config):
        self.printer = config.get_printer()
        
        # Read robot arm configuration
        arm_config = config.getsection("robot_arm")
        self.d1 = arm_config.getfloat("d1", 100.0)
        self.a1 = arm_config.getfloat("a1", 50.0)
        self.a2 = arm_config.getfloat("a2", 200.0)
        self.a3 = arm_config.getfloat("a3", 150.0)
        self.segments_per_second = arm_config.getfloat(
            "segments_per_second", 100.0, above=0.0
        )
        
        # Setup steppers (A=base, B=shoulder, C=elbow)
        self.steppers = [
            stepper.LookupMultiRail(config.getsection("stepper_" + n))
            for n in "abc"
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
        
        # Calculate reach
        self.max_reach = self.a1 + self.a2 + self.a3
        
        # Axis limits
        self.axes_min = toolhead.Coord(
            -self.max_reach, -self.max_reach, 0.0, 0.0
        )
        self.axes_max = toolhead.Coord(
            self.max_reach, self.max_reach, self.d1 + self.max_reach, 0.0
        )
        
        self.need_home = True
        self.supports_dual_carriage = False
        
        logging.info(
            "Robot arm: d1=%.1f a1=%.1f a2=%.1f a3=%.1f max_reach=%.1f",
            self.d1, self.a1, self.a2, self.a3, self.max_reach
        )

    def get_steppers(self):
        return [s for rail in self.steppers for s in rail.get_steppers()]

    def _forward_kinematics(self, theta1, theta2, theta3):
        """Convert joint angles (degrees) to Cartesian position (mm)."""
        t1 = math.radians(theta1)
        t2 = math.radians(theta2)
        t3 = math.radians(theta3)
        
        # Calculate end effector position using DH parameters
        # This is a simplified model for a 3-axis arm
        r = self.a1 * math.cos(t2) + self.a2 * math.cos(t2 + t3)
        x = r * math.cos(t1)
        y = r * math.sin(t1)
        z = self.d1 + self.a1 * math.sin(t2) + self.a2 * math.sin(t2 + t3)
        
        return x, y, z

    def _inverse_kinematics(self, x, y, z):
        """Convert Cartesian position (mm) to joint angles (degrees)."""
        # Calculate base angle
        theta1 = math.atan2(y, x)
        
        # Calculate distance from base to end effector in XY plane
        r = math.sqrt(x * x + y * y)
        
        # Calculate distance from shoulder to end effector
        dz = z - self.d1
        d = math.sqrt(r * r + dz * dz)
        
        # Calculate elbow angle using law of cosines
        cos_theta3 = (self.a1 * self.a1 + self.a2 * self.a2 - d * d) / (2 * self.a1 * self.a2)
        cos_theta3 = max(-1.0, min(1.0, cos_theta3))
        theta3 = math.acos(cos_theta3)
        
        # Calculate shoulder angle
        alpha = math.atan2(dz, r)
        cos_beta = (self.a1 * self.a1 + d * d - self.a2 * self.a2) / (2 * self.a1 * d)
        cos_beta = max(-1.0, min(1.0, cos_beta))
        beta = math.acos(cos_beta)
        theta2 = alpha + beta
        
        return math.degrees(theta1), math.degrees(theta2), math.degrees(theta3)

    def calc_position(self, stepper_positions):
        """Calculate Cartesian position from stepper positions."""
        a_pos = stepper_positions[self.steppers[0].get_name()]
        b_pos = stepper_positions[self.steppers[1].get_name()]
        c_pos = stepper_positions[self.steppers[2].get_name()]
        
        x, y, z = self._forward_kinematics(a_pos, b_pos, c_pos)
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
        """Home robot arm axes."""
        # Move to home position (origin)
        home_t1, home_t2, home_t3 = self._inverse_kinematics(0, 0, self.d1)
        
        # Set home position
        self.steppers[0].set_position([home_t1, 0, 0])
        self.steppers[1].set_position([home_t2, 0, 0])
        self.steppers[2].set_position([home_t3, 0, 0])
        
        self.need_home = False
        self.printer.lookup_object("toolhead").set_position([0, 0, self.d1, 0])

    def _motor_off(self, print_time):
        self.clear_homing_state((0, 1, 2))

    def check_move(self, move):
        """Validate move and apply constraints."""
        end_pos = move.end_pos
        
        # Check if homed
        if self.need_home:
            raise move.move_error("Must home robot arm first")
        
        # Calculate end effector position
        x, y, z = end_pos[0], end_pos[1], end_pos[2]
        
        # Check reach
        r = math.sqrt(x * x + y * y)
        d = math.sqrt(r * r + (z - self.d1) ** 2)
        if d > self.max_reach:
            raise move.move_error()
        
        # Check Z limits
        if z < self.axes_min[2] or z > self.axes_max[2]:
            raise move.move_error()
        
        # Calculate required joint angles for speed limiting
        t1_start, t2_start, t3_start = self._inverse_kinematics(
            move.start_pos[0], move.start_pos[1], move.start_pos[2]
        )
        t1_end, t2_end, t3_end = self._inverse_kinematics(x, y, z)
        
        # Limit angular velocity
        dt1 = abs(t1_end - t1_start)
        dt2 = abs(t2_end - t2_start)
        dt3 = abs(t3_end - t3_start)
        if dt1 > 180:
            dt1 = 360 - dt1
        if dt2 > 180:
            dt2 = 360 - dt2
        if dt3 > 180:
            dt3 = 360 - dt3
        
        # Convert angular distance to linear distance for speed limiting
        angular_dist = math.sqrt(dt1 * dt1 + dt2 * dt2 + dt3 * dt3)
        if angular_dist > 0:
            # Limit speed based on angular movement
            max_angular_velocity = 360.0  # degrees per second
            ratio = angular_dist / move.move_d
            move.limit_speed(
                max_angular_velocity / ratio,
                max_angular_velocity / ratio * 2
            )

    def get_status(self, eventtime):
        axes = "xyz" if not self.need_home else ""
        return {
            "homed_axes": axes,
            "axis_minimum": self.axes_min,
            "axis_maximum": self.axes_max,
            "max_reach": self.max_reach,
        }


def load_kinematics(toolhead, config):
    return RobotArmKinematics(toolhead, config)
