# Code for handling the kinematics of SCARA robots
#
# Based on Marlin's SCARA implementation by QHARLEY and Joachim Cerny
# Adapted for Kalico by [Your Name]
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math

from klippy import chelper, stepper


class SCARAKinematics:
    """SCARA (Selective Compliance Assembly Robot Arm) kinematics.
    
    Supports two SCARA variants:
    - Morgan SCARA: Uses Cartesian XY home position
    - MP SCARA: Uses arm angles for AB home position
    
    Configuration example:
    [printer]
    kinematics: scara
    
    [scara]
    linkage_1: 150    # Length of inner arm (mm)
    linkage_2: 150    # Length of outer arm (mm)
    offset_x: 100     # X offset of tower from bed center (mm)
    offset_y: -56     # Y offset of tower from bed center (mm)
    segments_per_second: 200
    #variant: morgan  # or "mp" for MP SCARA
    
    [stepper_a]      # Shoulder motor
    ...
    
    [stepper_b]      # Elbow motor
    ...
    
    [stepper_z]      # Z axis (standard cartesian)
    ...
    """

    def __init__(self, toolhead, config):
        self.printer = config.get_printer()
        
        # Read SCARA-specific configuration
        scara_config = config.getsection("scara")
        self.linkage_1 = scara_config.getfloat("linkage_1", above=0.0)
        self.linkage_2 = scara_config.getfloat("linkage_2", above=0.0)
        self.offset_x = scara_config.getfloat("offset_x", 0.0)
        self.offset_y = scara_config.getfloat("offset_y", 0.0)
        self.segments_per_second = scara_config.getfloat(
            "segments_per_second", 200.0, above=0.0
        )
        self.variant = scara_config.getchoice(
            "variant", {"morgan": "morgan", "mp": "mp"}, default="morgan"
        )
        
        # Calculate derived constants
        self.l1_sq = self.linkage_1 ** 2
        self.l2_sq = self.linkage_2 ** 2
        self.l1_sq_x2 = 2.0 * self.l1_sq
        
        # Setup steppers (A=shoulder, B=elbow, Z=vertical)
        self.steppers = [
            stepper.LookupMultiRail(config.getsection("stepper_" + n))
            for n in "abz"
        ]
        
        # Configure stepper kinematics
        # A and B steppers are rotational (in degrees)
        # Z stepper is linear (in mm)
        ffi_main, ffi_lib = chelper.get_ffi()
        self.sk_steppers = []
        for i, s in enumerate(self.steppers):
            if i < 2:  # A and B (rotational)
                sk = ffi_main.gc(
                    ffi_lib.cartesian_stepper_alloc(b"z"), ffi_lib.free
                )
            else:  # Z (linear)
                sk = ffi_main.gc(
                    ffi_lib.cartesian_stepper_alloc(b"z"), ffi_lib.free
                )
            s.set_stepper_kinematics(sk)
            self.sk_steppers.append(sk)
        
        # Setup trapq
        for s in self.get_steppers():
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
        
        # Calculate printable radius
        self.print_radius = scara_config.getfloat(
            "print_radius",
            self.linkage_1 + self.linkage_2,
            above=0.0
        )
        
        # Home position
        self.home_position = [
            scara_config.getfloat("home_x", 0.0),
            scara_config.getfloat("home_y", 0.0),
            scara_config.getfloat("home_z", 0.0)
        ]
        
        # Axis limits
        self.axes_min = toolhead.Coord(
            -self.print_radius, -self.print_radius, 0.0, 0.0
        )
        self.axes_max = toolhead.Coord(
            self.print_radius, self.print_radius, 
            config.getfloat("max_z", 300.0, above=0.0), 0.0
        )
        
        self.need_home = True
        self.supports_dual_carriage = False
        
        logging.info(
            "SCARA: L1=%.1f L2=%.1f offset=(%.1f,%.1f) radius=%.1f variant=%s",
            self.linkage_1, self.linkage_2, self.offset_x, self.offset_y,
            self.print_radius, self.variant
        )

    def get_steppers(self):
        return [s for rail in self.steppers for s in rail.get_steppers()]

    def _forward_kinematics(self, a_angle, b_angle):
        """Convert joint angles (degrees) to Cartesian position (mm)."""
        a_rad = math.radians(a_angle)
        b_rad = math.radians(b_angle)
        
        if self.variant == "morgan":
            # Morgan SCARA: angles are absolute
            x = (math.cos(a_rad) * self.linkage_1 + 
                 math.cos(a_rad + b_rad) * self.linkage_2 + 
                 self.offset_x)
            y = (math.sin(a_rad) * self.linkage_1 + 
                 math.sin(a_rad + b_rad) * self.linkage_2 + 
                 self.offset_y)
        else:
            # MP SCARA: angles are relative
            x = (math.cos(a_rad) * self.linkage_1 + 
                 math.cos(b_rad) * self.linkage_2 + 
                 self.offset_x)
            y = (math.sin(a_rad) * self.linkage_1 + 
                 math.sin(b_rad) * self.linkage_2 + 
                 self.offset_y)
        
        return x, y

    def _inverse_kinematics(self, x, y):
        """Convert Cartesian position (mm) to joint angles (degrees)."""
        # Adjust for offset
        sx = x - self.offset_x
        sy = y - self.offset_y
        
        # Calculate distance squared
        h_sq = sx * sx + sy * sy
        
        # Calculate cosine of elbow angle using law of cosines
        if self.linkage_1 == self.linkage_2:
            cos_beta = h_sq / self.l1_sq_x2 - 1.0
        else:
            cos_beta = (h_sq - (self.l1_sq + self.l2_sq)) / (2.0 * self.linkage_1 * self.linkage_2)
        
        # Clamp to valid range
        cos_beta = max(-1.0, min(1.0, cos_beta))
        sin_beta = math.sqrt(1.0 - cos_beta * cos_beta)
        
        # Calculate arm projections
        sk1 = self.linkage_1 + self.linkage_2 * cos_beta
        sk2 = self.linkage_2 * sin_beta
        
        # Calculate shoulder angle
        theta = math.atan2(sk1, sk2) - math.atan2(sx, sy)
        
        # Calculate elbow angle
        beta = math.atan2(sin_beta, cos_beta)
        
        if self.variant == "morgan":
            # Morgan: return theta and beta (relative)
            a = math.degrees(theta)
            b = math.degrees(beta)
        else:
            # MP: return theta and theta+beta (absolute)
            a = math.degrees(theta)
            b = math.degrees(theta + beta)
        
        return a, b

    def calc_position(self, stepper_positions):
        """Calculate Cartesian position from stepper positions."""
        a_pos = stepper_positions[self.steppers[0].get_name()]
        b_pos = stepper_positions[self.steppers[1].get_name()]
        z_pos = stepper_positions[self.steppers[2].get_name()]
        
        x, y = self._forward_kinematics(a_pos, b_pos)
        return [x, y, z_pos]

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
        """Home SCARA axes."""
        # Home Z first (standard cartesian)
        if 2 in homing_state.get_axes():
            z_rail = self.steppers[2]
            z_hi = z_rail.get_homing_info()
            homepos = [None, None, z_hi.position_endstop, None]
            forcepos = list(homepos)
            if z_hi.positive_dir:
                forcepos[2] -= 1.5 * (z_hi.position_endstop - z_rail.get_range()[0])
            else:
                forcepos[2] += 1.5 * (z_rail.get_range()[1] - z_hi.position_endstop)
            homing_state.home_rails([z_rail], forcepos, homepos)
        
        # Home A and B (rotational axes)
        if 0 in homing_state.get_axes() or 1 in homing_state.get_axes():
            # Move to home position
            home_a, home_b = self._inverse_kinematics(
                self.home_position[0], self.home_position[1]
            )
            
            # Set home position
            self.steppers[0].set_position([home_a, 0, 0])
            self.steppers[1].set_position([home_b, 0, 0])
            
            # Mark as homed
            self.need_home = False
            self.printer.lookup_object("toolhead").set_position(
                [self.home_position[0], self.home_position[1], 
                 self.home_position[2], 0]
            )

    def _motor_off(self, print_time):
        self.clear_homing_state((0, 1, 2))

    def check_move(self, move):
        """Validate move and apply constraints."""
        end_pos = move.end_pos
        
        # Check if homed
        if self.need_home:
            raise move.move_error("Must home SCARA first")
        
        # Calculate end effector position
        x, y = end_pos[0], end_pos[1]
        
        # Check print radius
        r_sq = x * x + y * y
        if r_sq > self.print_radius ** 2:
            raise move.move_error()
        
        # Check Z limits
        if end_pos[2] < self.axes_min[2] or end_pos[2] > self.axes_max[2]:
            raise move.move_error()
        
        # Limit Z speed
        if move.axes_d[2]:
            z_ratio = move.move_d / abs(move.axes_d[2])
            move.limit_speed(
                self.max_z_velocity * z_ratio, self.max_z_accel * z_ratio
            )
        
        # Calculate required joint angles for speed limiting
        a_start, b_start = self._inverse_kinematics(
            move.start_pos[0], move.start_pos[1]
        )
        a_end, b_end = self._inverse_kinematics(x, y)
        
        # Limit angular velocity
        da = abs(a_end - a_start)
        db = abs(b_end - b_start)
        if da > 180:
            da = 360 - da
        if db > 180:
            db = 360 - db
        
        # Convert angular distance to linear distance for speed limiting
        angular_dist = math.sqrt(da * da + db * db)
        if angular_dist > 0:
            # Limit speed based on angular movement
            max_angular_velocity = 360.0  # degrees per second
            ratio = angular_dist / move.move_d
            move.limit_speed(
                max_angular_velocity / ratio,
                max_angular_velocity / ratio * 2
            )

    def get_status(self, eventtime):
        axes = "xyz" if not self.need_home else "z" if not self.need_home else ""
        return {
            "homed_axes": axes,
            "axis_minimum": self.axes_min,
            "axis_maximum": self.axes_max,
            "print_radius": self.print_radius,
            "linkage_1": self.linkage_1,
            "linkage_2": self.linkage_2,
        }


def load_kinematics(toolhead, config):
    return SCARAKinematics(toolhead, config)
