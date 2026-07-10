# Code for handling the kinematics of TPARA robots
#
# TPARA (Three Parallel Axis Rotary Arm) is a 3-axis robotic arm
# with three parallel rotation axes.
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math

from klippy import stepper


class TPARAKinematics:
    """TPARA (Three Parallel Axis Rotary Arm) kinematics.
    
    Configuration example:
    [printer]
    kinematics: tpara
    
    [tpara]
    linkage_1: 120    # Length of inner arm (mm)
    linkage_2: 120    # Length of outer arm (mm)
    offset_x: 0       # X offset (mm)
    offset_y: 0       # Y offset (mm)
    offset_z: 0       # Z offset (mm)
    segments_per_second: 200
    
    [stepper_a]   # Base rotation
    ...
    
    [stepper_b]   # Shoulder rotation
    ...
    
    [stepper_c]   # Elbow rotation
    ...
    """

    def __init__(self, toolhead, config):
        self.printer = config.get_printer()
        
        # Read TPARA configuration
        tpara_config = config.getsection("tpara")
        self.linkage_1 = tpara_config.getfloat("linkage_1", above=0.0)
        self.linkage_2 = tpara_config.getfloat("linkage_2", above=0.0)
        self.offset_x = tpara_config.getfloat("offset_x", 0.0)
        self.offset_y = tpara_config.getfloat("offset_y", 0.0)
        self.offset_z = tpara_config.getfloat("offset_z", 0.0)
        self.segments_per_second = tpara_config.getfloat(
            "segments_per_second", 200.0, above=0.0
        )
        
        # Calculate derived constants
        self.l1_sq = self.linkage_1 ** 2
        self.l2_sq = self.linkage_2 ** 2
        
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
        
        # Calculate printable radius
        self.print_radius = tpara_config.getfloat(
            "print_radius",
            self.linkage_1 + self.linkage_2,
            above=0.0
        )
        
        # Axis limits
        self.axes_min = toolhead.Coord(
            -self.print_radius, -self.print_radius,
            tpara_config.getfloat("min_z", 0.0), 0.0
        )
        self.axes_max = toolhead.Coord(
            self.print_radius, self.print_radius,
            tpara_config.getfloat("max_z", 300.0, above=0.0), 0.0
        )
        
        self.need_home = True
        self.supports_dual_carriage = False
        
        logging.info(
            "TPARA: L1=%.1f L2=%.1f offset=(%.1f,%.1f,%.1f) radius=%.1f",
            self.linkage_1, self.linkage_2, 
            self.offset_x, self.offset_y, self.offset_z,
            self.print_radius
        )

    def get_steppers(self):
        return [s for rail in self.steppers for s in rail.get_steppers()]

    def _forward_kinematics(self, a_angle, b_angle, c_angle):
        """Convert joint angles (degrees) to Cartesian position (mm)."""
        a_rad = math.radians(a_angle)
        b_rad = math.radians(b_angle)
        c_rad = math.radians(c_angle)
        
        # Calculate end effector position
        # This is a simplified model - actual TPARA kinematics are more complex
        r = self.linkage_1 * math.cos(b_rad) + self.linkage_2 * math.sin(c_rad - (math.pi/2 - b_rad))
        x = r * math.cos(a_rad) + self.offset_x
        y = r * math.sin(a_rad) + self.offset_y
        z = self.linkage_1 * math.sin(b_rad) - self.linkage_2 * math.cos(c_rad - (math.pi/2 - b_rad)) + self.offset_z
        
        return x, y, z

    def _inverse_kinematics(self, x, y, z):
        """Convert Cartesian position (mm) to joint angles (degrees)."""
        # Adjust for offset
        sx = x - self.offset_x
        sy = y - self.offset_y
        sz = z - self.offset_z
        
        # Calculate distance in XY plane
        r_xy = math.sqrt(sx * sx + sy * sy)
        
        # Calculate base angle
        theta = math.atan2(sy, sx)
        
        # Calculate distance from shoulder to end effector
        rho_sq = r_xy * r_xy + sz * sz
        rho = math.sqrt(rho_sq)
        
        # Calculate shoulder and elbow angles using law of cosines
        cos_beta = (self.l1_sq + self.l2_sq - rho_sq) / (2 * self.linkage_1 * self.linkage_2)
        cos_beta = max(-1.0, min(1.0, cos_beta))
        beta = math.acos(cos_beta)
        
        # Calculate shoulder angle
        cos_alpha = (self.l1_sq + rho_sq - self.l2_sq) / (2 * self.linkage_1 * rho)
        cos_alpha = max(-1.0, min(1.0, cos_alpha))
        alpha = math.acos(cos_alpha)
        
        # Calculate elevation angle
        gamma = math.atan2(sz, r_xy)
        
        # Combine angles
        phi = gamma + alpha
        psi = phi + beta
        
        return math.degrees(theta), math.degrees(phi), math.degrees(psi)

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
        """Home TPARA axes."""
        # Move to home position (origin)
        home_a, home_b, home_c = self._inverse_kinematics(0, 0, 0)
        
        # Set home position
        self.steppers[0].set_position([home_a, 0, 0])
        self.steppers[1].set_position([home_b, 0, 0])
        self.steppers[2].set_position([home_c, 0, 0])
        
        self.need_home = False
        self.printer.lookup_object("toolhead").set_position([0, 0, 0, 0])

    def _motor_off(self, print_time):
        self.clear_homing_state((0, 1, 2))

    def check_move(self, move):
        """Validate move and apply constraints."""
        end_pos = move.end_pos
        
        # Check if homed
        if self.need_home:
            raise move.move_error("Must home TPARA first")
        
        # Calculate end effector position
        x, y, z = end_pos[0], end_pos[1], end_pos[2]
        
        # Check print radius
        r_sq = x * x + y * y
        if r_sq > self.print_radius ** 2:
            raise move.move_error()
        
        # Check Z limits
        if z < self.axes_min[2] or z > self.axes_max[2]:
            raise move.move_error()
        
        # Limit Z speed
        if move.axes_d[2]:
            z_ratio = move.move_d / abs(move.axes_d[2])
            move.limit_speed(
                self.max_z_velocity * z_ratio, self.max_z_accel * z_ratio
            )
        
        # Calculate required joint angles for speed limiting
        a_start, b_start, c_start = self._inverse_kinematics(
            move.start_pos[0], move.start_pos[1], move.start_pos[2]
        )
        a_end, b_end, c_end = self._inverse_kinematics(x, y, z)
        
        # Limit angular velocity
        da = abs(a_end - a_start)
        db = abs(b_end - b_start)
        dc = abs(c_end - c_start)
        if da > 180:
            da = 360 - da
        if db > 180:
            db = 360 - db
        if dc > 180:
            dc = 360 - dc
        
        # Convert angular distance to linear distance for speed limiting
        angular_dist = math.sqrt(da * da + db * db + dc * dc)
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
            "print_radius": self.print_radius,
            "linkage_1": self.linkage_1,
            "linkage_2": self.linkage_2,
        }


def load_kinematics(toolhead, config):
    return TPARAKinematics(toolhead, config)
