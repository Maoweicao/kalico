# Filament blockage detection sensor
# 耗材堵塞检测传感器
#
# Copyright (C) 2026  Mellow <service@3dmellow.com>
# Enhanced for kalico
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math

from . import filament_switch_sensor


class MCUFilamentBlockageDetector:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.config_name = config.get_name()
        self.name = config.get_name().split()[-1]
        self.switch_pin = config.get('switch_pin')
        self.extruder_name = config.get('extruder', 'extruder')
        self.detection_length = config.getfloat(
            'detection_length', 7., above=0.)
        self.recovery_length = config.getfloat(
            'recovery_length', self.detection_length * 0.5,
            minval=0., maxval=self.detection_length)
        self.window_length = config.getfloat(
            'window_length', self.detection_length * 3., above=0.)
        self.retraction_min_delta = config.getfloat(
            'retraction_min_delta', 0.050, minval=0.)
        self.blockage_sample_count = config.getint(
            'blockage_sample_count', 2, minval=1, maxval=5)
        self.poll_time = config.getfloat(
            'poll_time', .000050, minval=.000010)
        self.report_time = config.getfloat(
            'report_time', .250, minval=.050)
        self.distance_per_edge = config.getfloat(
            'distance_per_edge', above=0.)
        self.distance_per_edge_um = max(
            1, int(math.ceil(self.distance_per_edge * 1000.)))

        ppins = self.printer.lookup_object('pins')
        pin_params = ppins.lookup_pin(self.switch_pin, can_pullup=True)
        self.mcu = pin_params['chip']
        if hasattr(self.mcu, 'get_mcu'):
            self.mcu = self.mcu.get_mcu()
        self.oid = self.mcu.create_oid()
        self.pin = pin_params['pin']
        self.pullup = pin_params['pullup']

        self.runout_helper = filament_switch_sensor.RunoutHelper(config)
        self.get_status = self._get_status
        self.extruder = None
        self.estimated_print_time = None
        self.gcode = self.printer.lookup_object('gcode')
        self.is_printing = False
        self.blockage_detected = False
        self.last_measured_um = 0
        self.last_edge_count = 0
        self.last_pin_state = 0
        self.total_measured_distance = 0.
        self.raw_measured_distance = 0.
        self.last_measured_delta = 0.
        self.measured_speed = 0.
        self.expected_distance = 0.
        self.measured_distance = 0.
        self.slip_distance = 0.
        self.total_extruded_distance = 0.
        self.last_extruder_pos = 0.
        self.last_eventtime = 0.
        self.in_retraction = False
        self.pending_blockage_count = 0
        self.last_motion_dir = 0
        self.last_motion_extruder_pos = 0.

        self.mcu.register_config_callback(self._build_config)
        self.printer.register_event_handler('klippy:ready', self._handle_ready)
        self.printer.register_event_handler('idle_timeout:printing',
                                            self._handle_printing)
        self.printer.register_event_handler('idle_timeout:ready',
                                            self._handle_not_printing)
        self.printer.register_event_handler('idle_timeout:idle',
                                            self._handle_not_printing)
        self.gcode.register_mux_command(
            "QUERY_FILAMENT_BLOCKAGE", "SENSOR", self.name,
            self.cmd_QUERY_FILAMENT_BLOCKAGE,
            desc=self.cmd_QUERY_FILAMENT_BLOCKAGE_help)
        self.gcode.register_mux_command(
            "CALIBRATE_FILAMENT_BLOCKAGE", "SENSOR", self.name,
            self.cmd_CALIBRATE_FILAMENT_BLOCKAGE,
            desc=self.cmd_CALIBRATE_FILAMENT_BLOCKAGE_help)
        logging.info(
            "Filament blockage sensor %s: init extruder=%s switch_pin=%s "
            "detection_length=%.6f recovery_length=%.6f "
            "window_length=%.6f "
            "retraction_min_delta=%.6f blockage_sample_count=%d "
            "distance_per_edge=%.6f poll_time=%.6f report_time=%.6f",
            self.name, self.extruder_name, self.switch_pin,
            self.detection_length, self.recovery_length, self.window_length,
            self.retraction_min_delta, self.blockage_sample_count,
            self.distance_per_edge, self.poll_time, self.report_time)

    def _build_config(self):
        self.mcu.add_config_cmd(
            "config_filament_blockage oid=%d pin=%s pull_up=%d"
            % (self.oid, self.pin, self.pullup))
        clock = self.mcu.get_query_slot(self.oid)
        poll_ticks = self.mcu.seconds_to_clock(self.poll_time)
        report_ticks = self.mcu.seconds_to_clock(self.report_time)
        self.mcu.add_config_cmd(
            "filament_blockage_start oid=%d clock=%d poll_ticks=%d"
            " report_ticks=%d distance_per_edge_um=%d"
            % (self.oid, clock, poll_ticks, report_ticks,
               self.distance_per_edge_um), is_init=True)
        self.mcu.register_serial_response(
            self._handle_sensor_state,
            "filament_blockage_state oid=%c clock=%u measured_um=%u"
            " edge_count=%u pin_state=%c", self.oid)
        logging.info(
            "Filament blockage sensor %s: build_config mcu=%s pin=%s "
            "pullup=%d distance_per_edge_um=%d",
            self.name, self.mcu.get_name(), self.pin, self.pullup,
            self.distance_per_edge_um)

    def _handle_ready(self):
        self.extruder = self.printer.lookup_object(self.extruder_name)
        self.estimated_print_time = (
            self.printer.lookup_object('mcu').estimated_print_time)
        self._reset_tracking(self.reactor.monotonic())
        logging.info(
            "Filament blockage sensor %s: ready oid=%d",
            self.name, self.oid)

    def _handle_printing(self, _print_time):
        self.is_printing = True
        self._reset_tracking(self.reactor.monotonic())
        logging.info("Filament blockage sensor %s: printing start", self.name)

    def _handle_not_printing(self, _print_time):
        self.is_printing = False
        self._reset_tracking(self.reactor.monotonic())
        logging.info("Filament blockage sensor %s: printing stop", self.name)

    def _get_extruder_pos(self, eventtime):
        print_time = self.estimated_print_time(eventtime)
        return self.extruder.find_past_position(print_time)

    def _reset_tracking(self, eventtime):
        if self.extruder is not None and self.estimated_print_time is not None:
            self.last_extruder_pos = self._get_extruder_pos(eventtime)
        else:
            self.last_extruder_pos = 0.
        self.expected_distance = 0.
        self.measured_distance = 0.
        self.slip_distance = 0.
        self.total_extruded_distance = 0.
        self.blockage_detected = False
        self.total_measured_distance = 0.
        self.last_measured_delta = 0.
        self.measured_speed = 0.
        self.last_eventtime = eventtime
        self.in_retraction = False
        self.pending_blockage_count = 0
        self.last_motion_dir = 0
        self.last_motion_extruder_pos = self.last_extruder_pos
        self.runout_helper.filament_present = True
        logging.info(
            "Filament blockage sensor %s: tracking reset eventtime=%.6f "
            "extruder_pos=%.6f measured_um=%d edge_count=%d pin_state=%d",
            self.name, eventtime, self.last_extruder_pos,
            self.last_measured_um, self.last_edge_count, self.last_pin_state)

    def _handle_sensor_state(self, params):
        if self.estimated_print_time is None or self.extruder is None:
            logging.debug(
                "Filament blockage sensor %s: ignoring early sensor state",
                self.name)
            return
        eventtime = params['#receive_time']
        measured_um = params['measured_um']
        edge_count = params['edge_count']
        pin_state = params['pin_state']
        clock = params['clock']

        delta_um = (measured_um - self.last_measured_um) & 0xffffffff
        delta_edges = (edge_count - self.last_edge_count) & 0xffffffff
        measured_delta = delta_um / 1000.
        extruder_pos = self._get_extruder_pos(eventtime)
        extruder_delta = extruder_pos - self.last_extruder_pos
        delta_time = eventtime - self.last_eventtime

        self.last_measured_um = measured_um
        self.last_edge_count = edge_count
        self.last_pin_state = pin_state
        self.raw_measured_distance = measured_um / 1000.
        if extruder_delta >= 0.:
            self.last_measured_delta = measured_delta
        else:
            self.last_measured_delta = -measured_delta
        self.measured_speed = (
            0. if delta_time <= 0. else self.last_measured_delta / delta_time)
        self.last_eventtime = eventtime
        self.last_extruder_pos = extruder_pos

        if not self.is_printing:
            logging.debug(
                "Filament blockage sensor %s: idle sync clock=%u "
                "pin_state=%d edge_count=%d measured_um=%d "
                "extruder_pos=%.6f",
                self.name, clock, pin_state, edge_count, measured_um,
                extruder_pos)
            return

        motion_dir = 0
        if extruder_delta > self.retraction_min_delta:
            motion_dir = 1
        elif extruder_delta < -self.retraction_min_delta:
            motion_dir = -1
        if motion_dir == 0 and extruder_delta < 0.:
            extruder_delta = 0.

        if (motion_dir and self.last_motion_dir
                and motion_dir != self.last_motion_dir):
            logging.info(
                "Filament blockage sensor %s: direction change rebaseline "
                "clock=%u old_dir=%d new_dir=%d extruder_delta=%.6f "
                "measured_delta=%.6f",
                self.name, clock, self.last_motion_dir, motion_dir,
                extruder_delta, measured_delta)
            self.expected_distance = 0.
            self.measured_distance = 0.
            self.slip_distance = 0.
            self.pending_blockage_count = 0
            self.blockage_detected = False
            self.last_motion_extruder_pos = extruder_pos

        if motion_dir:
            self.last_motion_dir = motion_dir
        self.in_retraction = motion_dir < 0

        if motion_dir < 0:
            return

        if extruder_delta >= 0.:
            self.total_extruded_distance += extruder_delta
            self.total_measured_distance += measured_delta
        if delta_edges > 0:
            self.last_motion_extruder_pos = extruder_pos
        self.expected_distance = max(
            0., extruder_pos - self.last_motion_extruder_pos)
        self.measured_distance = 0.
        self.slip_distance = self.expected_distance

        logging.debug(
            "Filament blockage sensor %s: report clock=%u pin_state=%d "
            "edge_count=%d delta_edges=%d measured_um=%d delta_um=%d "
            "extruder_pos=%.6f extruder_delta=%.6f "
            "last_motion_extruder_pos=%.6f expected=%.6f "
            "measured=%.6f slip=%.6f printing=%s",
            self.name, clock, pin_state, edge_count, delta_edges,
            measured_um, delta_um, extruder_pos, extruder_delta,
            self.last_motion_extruder_pos,
            self.expected_distance, self.measured_distance,
            self.slip_distance, self.is_printing)

        was_blocked = self.blockage_detected
        if self.is_printing and self.slip_distance >= self.detection_length:
            self.pending_blockage_count += 1
            if self.pending_blockage_count >= self.blockage_sample_count:
                self.blockage_detected = True
        elif self.slip_distance <= self.recovery_length:
            self.pending_blockage_count = 0
            self.blockage_detected = False
        else:
            self.pending_blockage_count = 0

        if self.blockage_detected != was_blocked:
            logging.info(
                "Filament blockage sensor %s: state change blocked=%s "
                "prev_blocked=%s expected=%.6f measured=%.6f slip=%.6f",
                self.name, self.blockage_detected, was_blocked,
                self.expected_distance, self.measured_distance,
                self.slip_distance)
            self.reactor.register_async_callback(
                lambda et, bt=eventtime, present=(not self.blockage_detected):
                self.runout_helper.note_filament_present(bt, present))

    cmd_QUERY_FILAMENT_BLOCKAGE_help = (
        "Query the measured filament total distance and speed"
        " / 查询耗材测量距离和速度"
    )
    def cmd_QUERY_FILAMENT_BLOCKAGE(self, gcmd):
        gcmd.respond_info(
            "Filament blockage sensor %s:\n"
            "  total_measured_distance: %.3f mm\n"
            "  raw_measured_distance: %.3f mm\n"
            "  measured_speed: %.3f mm/s\n"
            "  edge_count: %d\n"
            "  total_extruded_distance: %.3f mm\n"
            "  expected_distance: %.3f mm\n"
            "  measured_distance: %.3f mm\n"
            "  slip_distance: %.3f mm\n"
            "  pending_blockage_count: %d\n"
            "  in_retraction: %s\n"
            "  blocked: %s\n"
            "  printing: %s"
            % (self.name, self.total_measured_distance,
               self.raw_measured_distance, self.measured_speed,
               self.last_edge_count, self.total_extruded_distance,
               self.expected_distance,
               self.measured_distance, self.slip_distance,
               self.pending_blockage_count,
               self.in_retraction,
               self.blockage_detected, self.is_printing))

    def _wait_for_sensor_report(self, min_eventtime, timeout):
        eventtime = self.reactor.monotonic()
        deadline = eventtime + timeout
        while self.last_eventtime <= min_eventtime:
            if eventtime >= deadline:
                raise self.printer.command_error(
                    "Timed out waiting for filament blockage sensor update")
            eventtime = self.reactor.pause(eventtime + 0.050)

    cmd_CALIBRATE_FILAMENT_BLOCKAGE_help = (
        "Heat extruder, perform repeated extrusion tests, and save "
        "distance_per_edge / 加热挤出机，执行重复挤出测试并保存distance_per_edge"
    )
    def cmd_CALIBRATE_FILAMENT_BLOCKAGE(self, gcmd):
        temperature = gcmd.get_float('TEMPERATURE', above=0.)
        distance = gcmd.get_float('DISTANCE', 30., above=0.)
        count = gcmd.get_int('COUNT', 5, minval=1, maxval=20)
        speed = gcmd.get_float('SPEED', 2., above=0.)
        settle_time = gcmd.get_float(
            'SETTLE_TIME', max(0.200, self.report_time * 1.5), minval=0.050)
        min_edges = gcmd.get_int('MIN_EDGES', 1, minval=1)

        if self.extruder is None:
            self.extruder = self.printer.lookup_object(self.extruder_name)
        toolhead = self.printer.lookup_object('toolhead')
        pheaters = self.printer.lookup_object('heaters')
        configfile = self.printer.lookup_object('configfile')
        state_name = "FILAMENT_BLOCKAGE_CAL_%s" % (self.name,)
        feedrate = speed * 60.
        samples = []

        gcmd.respond_info(
            "Filament blockage sensor %s calibration start:\n"
            "  temperature: %.1f C\n"
            "  rounds: %d\n"
            "  distance_per_round: %.3f mm\n"
            "  speed: %.3f mm/s"
            % (self.name, temperature, count, distance, speed))

        self.gcode.run_script_from_command(
            "ACTIVATE_EXTRUDER EXTRUDER=%s" % (self.extruder_name,))
        pheaters.set_temperature(self.extruder.get_heater(), temperature, True)
        self.gcode.run_script_from_command(
            "SAVE_GCODE_STATE NAME=%s" % (state_name,))
        self.gcode.run_script_from_command("M83")

        try:
            for i in range(count):
                start_edges = self.last_edge_count
                start_eventtime = self.last_eventtime
                self.gcode.run_script_from_command(
                    "G1 E%.5f F%.5f" % (distance, feedrate))
                toolhead.wait_moves()
                wait_start = self.reactor.monotonic()
                self.reactor.pause(wait_start + settle_time)
                self._wait_for_sensor_report(
                    start_eventtime,
                    settle_time + self.report_time + 1.)
                end_edges = self.last_edge_count
                delta_edges = (end_edges - start_edges) & 0xffffffff
                if delta_edges < min_edges:
                    raise gcmd.error(
                        "Calibration round %d captured too few edges (%d)"
                        % (i + 1, delta_edges))
                samples.append(delta_edges)
                gcmd.respond_info(
                    "Filament blockage sensor %s calibration round %d/%d:\n"
                    "  edge_count_delta: %d\n"
                    "  implied_distance_per_edge: %.6f mm"
                    % (self.name, i + 1, count, delta_edges,
                       distance / float(delta_edges)))
        finally:
            self.gcode.run_script_from_command(
                "RESTORE_GCODE_STATE NAME=%s" % (state_name,))

        avg_edges = sum(samples) / float(len(samples))
        new_distance_per_edge = distance / avg_edges
        self.distance_per_edge = new_distance_per_edge
        self.distance_per_edge_um = max(
            1, int(math.ceil(new_distance_per_edge * 1000.)))

        configfile.set(self.config_name, 'distance_per_edge',
                       "%.6f" % (new_distance_per_edge,))
        gcmd.respond_info(
            "Filament blockage sensor %s calibration result:\n"
            "  samples: %s\n"
            "  average_edge_count: %.3f\n"
            "  calibrated_distance_per_edge: %.6f mm\n"
            "The SAVE_CONFIG command will update the printer config file\n"
            "with this parameter and restart the printer."
            % (self.name, ", ".join(str(v) for v in samples),
               avg_edges, new_distance_per_edge))

    def _get_status(self, eventtime):
        base_status = self.runout_helper.get_status(eventtime)
        return dict(base_status, **{
            'blockage_detected': self.blockage_detected,
            'printing': self.is_printing,
            'edge_count': self.last_edge_count,
            'total_extruded_distance': self.total_extruded_distance,
            'total_measured_distance': self.total_measured_distance,
            'raw_measured_distance': self.raw_measured_distance,
            'last_measured_delta': self.last_measured_delta,
            'measured_speed': self.measured_speed,
            'measured_distance': self.measured_distance,
            'expected_distance': self.expected_distance,
            'slip_distance': self.slip_distance,
            'pending_blockage_count': self.pending_blockage_count,
            'in_retraction': self.in_retraction,
            'distance_per_edge': self.distance_per_edge,
            'window_length': self.window_length,
            'retraction_min_delta': self.retraction_min_delta,
            'blockage_sample_count': self.blockage_sample_count,
            'report_time': self.report_time,
            'poll_time': self.poll_time,
        })


def load_config_prefix(config):
    return MCUFilamentBlockageDetector(config)
