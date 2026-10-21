# Support for position encoders (SPI absolute + quadrature incremental)
#
# Copyright (C) 2024-2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

from . import bulk_sensor, bus

MIN_MSG_TIME = 0.100
TCODE_ERROR = 0xFF

# SPI absolute angle sensors supported by src/sensor_angle.c
SPI_SENSOR_TYPES = ["a1333", "as5047d", "tle5012b", "mt6816", "mt6826s"]
# Quadrature incremental sensors - these require src/encoder_quadrature.c
# which is not part of the firmware build at present.  The code path is kept
# so that it is ready once the firmware support lands.
QUADRATURE_SENSOR_TYPES = ["quadrature", "heds9740"]
UNSUPPORTED_SENSOR_TYPES = QUADRATURE_SENSOR_TYPES

BYTES_PER_SAMPLE_SPI = 3
BYTES_PER_SAMPLE_QUAD = 4
SAMPLES_PER_BLOCK = bulk_sensor.MAX_BULK_MSG_SIZE // BYTES_PER_SAMPLE_SPI

SAMPLE_PERIOD = 0.000400
BATCH_UPDATES = 0.100

# SPI angle sensors report a normalized 16bit angle
ANGLE_FULL_SCALE = 65536.0

AXIS_LIST = ["x", "y", "z"]


class Encoder:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[1]
        self.encoder_type = config.getchoice(
            "encoder_type",
            {t: t for t in SPI_SENSOR_TYPES + QUADRATURE_SENSOR_TYPES})
        if self.encoder_type in UNSUPPORTED_SENSOR_TYPES:
            raise config.error(
                "Encoder type '%s' is not yet supported by the firmware"
                " (src/encoder_quadrature.c is not built).  Use an SPI"
                " absolute sensor (eg 'as5047d') instead."
                % (self.encoder_type,))
        self.is_quadrature = self.encoder_type in QUADRATURE_SENSOR_TYPES
        self.stepper_name = config.get("stepper", None)
        self.last_position = 0
        self.last_sample = None
        self.error_count = 0
        self.mcu_stepper = None
        self.cpr = None
        self.rotation_distance = 1.0
        self._sampling_active = False
        # Encoder scaling - "scale" is the number of millimeters of axis
        # travel per encoder revolution.  It defaults to the paired
        # stepper's rotation_distance which is correct when the encoder is
        # coupled 1:1 to the axis.
        self.scale = config.getfloat("scale", None, above=0.0)
        self.invert = config.getboolean("invert", False)
        # Axis of the cartesian machine measured by this encoder
        self.axis = config.get("axis", None)
        if self.axis is not None and self.axis not in AXIS_LIST:
            raise config.error(
                "Invalid axis '%s' in section '%s'"
                % (self.axis, config.get_name()))
        self._resolve_stepper_config(config)

        if self.is_quadrature:
            self._init_quadrature(config)
        else:
            self._init_spi(config)

        self.printer.register_event_handler("klippy:ready",
                                            self._handle_ready)
        cname = self.name.split()[-1]
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command(
            "ENCODER_POSITION",
            "ENCODER",
            cname,
            self.cmd_ENCODER_POSITION,
            desc=self.cmd_ENCODER_POSITION_help,
        )
        gcode.register_mux_command(
            "ENCODER_RAW_DATA",
            "ENCODER",
            cname,
            self.cmd_ENCODER_RAW_DATA,
            desc=self.cmd_ENCODER_RAW_DATA_help,
        )

    cmd_ENCODER_POSITION_help = "Query current encoder position"
    cmd_ENCODER_RAW_DATA_help = "Query raw encoder sensor data"

    def _init_spi(self, config):
        from .angle import (
            HelperA1333,
            HelperAS5047D,
            HelperMT6816,
            HelperMT6826S,
            HelperTLE5012B,
        )

        sensors = {
            "a1333": HelperA1333, "as5047d": HelperAS5047D,
            "tle5012b": HelperTLE5012B, "mt6816": HelperMT6816,
            "mt6826s": HelperMT6826S,
        }
        self.sample_period = config.getfloat(
            "sample_period", SAMPLE_PERIOD, above=0.0)
        sensor_class = sensors[self.encoder_type]
        self.spi = bus.MCU_SPI_from_config(
            config, sensor_class.SPI_MODE,
            default_speed=sensor_class.SPI_SPEED)
        self.mcu = self.spi.get_mcu()
        self.oid = self.mcu.create_oid()
        self.sensor_helper = sensor_class(config, self.spi, self.oid)
        self.mcu.add_config_cmd(
            "config_spi_angle oid=%d spi_oid=%d spi_angle_type=%s"
            % (self.oid, self.spi.get_oid(), self.encoder_type))
        self.mcu.add_config_cmd(
            "query_spi_angle oid=%d clock=0 rest_ticks=0 time_shift=0"
            % (self.oid,), on_restart=True)
        self.mcu.register_config_callback(self._build_spi_config)
        self.bulk_queue = bulk_sensor.BulkDataQueue(self.mcu, oid=self.oid)
        self.batch_bulk = bulk_sensor.BatchBulkHelper(
            self.printer, self._process_batch_spi,
            self._start_spi_measurements, self._finish_spi_measurements,
            BATCH_UPDATES)
        api_resp = {"header": ("time", "position")}
        self.batch_bulk.add_mux_endpoint(
            "encoder/dump_encoder", "sensor", self.name, api_resp)

    def _init_quadrature(self, config):
        ppins = self.printer.lookup_object("pins")
        pin_a = ppins.lookup_pin(config.get("channel_a_pin"))
        pin_b = ppins.lookup_pin(config.get("channel_b_pin"))
        self.cpr = config.getint("cpr", above=0)
        self.sample_period = config.getfloat(
            "sample_period", SAMPLE_PERIOD, above=0.0)
        self.mcu = pin_a["chip"]
        self.oid = self.mcu.create_oid()
        self.mcu.add_config_cmd(
            "config_quadrature_encoder oid=%d pin_a=%s pin_b=%s"
            % (self.oid, pin_a["pin"], pin_b["pin"]))
        self.mcu.add_config_cmd(
            "query_quadrature_encoder oid=%d clock=0 rest_ticks=0"
            % (self.oid,), on_restart=True)
        self.mcu.register_config_callback(self._build_quad_config)
        self.bulk_queue = bulk_sensor.BulkDataQueue(self.mcu, oid=self.oid)
        self.batch_bulk = bulk_sensor.BatchBulkHelper(
            self.printer, self._process_batch_quad,
            self._start_quad_measurements, self._finish_quad_measurements,
            BATCH_UPDATES)
        api_resp = {"header": ("time", "position")}
        self.batch_bulk.add_mux_endpoint(
            "encoder/dump_encoder", "sensor", self.name, api_resp)

    def _build_spi_config(self):
        self.query_cmd = self.mcu.lookup_command(
            "query_spi_angle oid=%c clock=%u rest_ticks=%u time_shift=%c",
            cq=self.spi.get_command_queue())
        freq = self.mcu.seconds_to_clock(1.0)
        self.time_shift = 0
        while float(TCODE_ERROR << self.time_shift) / freq < 0.002:
            self.time_shift += 1

    def _build_quad_config(self):
        self.query_cmd = self.mcu.lookup_command(
            "query_quadrature_encoder oid=%c clock=%u rest_ticks=%u")

    def _start_spi_measurements(self):
        self.sensor_helper.start()
        self.bulk_queue.clear_queue()
        self.last_sequence = self.last_angle = 0
        systime = self.printer.get_reactor().monotonic()
        print_time = self.mcu.estimated_print_time(systime) + MIN_MSG_TIME
        self.start_clock = reqclock = self.mcu.print_time_to_clock(print_time)
        rest_ticks = self.mcu.seconds_to_clock(self.sample_period)
        self.sample_ticks = rest_ticks
        self.query_cmd.send(
            [self.oid, reqclock, rest_ticks, self.time_shift],
            reqclock=reqclock)
        logging.info("Started encoder '%s' SPI measurements", self.name)

    def _finish_spi_measurements(self):
        self.query_cmd.send_wait_ack([self.oid, 0, 0, 0])
        self.bulk_queue.clear_queue()
        logging.info("Stopped encoder '%s' SPI measurements", self.name)

    def _start_quad_measurements(self):
        self.bulk_queue.clear_queue()
        self.last_sequence = self.last_quad_position = 0
        systime = self.printer.get_reactor().monotonic()
        print_time = self.mcu.estimated_print_time(systime) + MIN_MSG_TIME
        self.start_clock = reqclock = self.mcu.print_time_to_clock(print_time)
        rest_ticks = self.mcu.seconds_to_clock(self.sample_period)
        self.sample_ticks = rest_ticks
        self.query_cmd.send([self.oid, reqclock, rest_ticks])
        logging.info("Started encoder '%s' quadrature measurements",
                     self.name)

    def _finish_quad_measurements(self):
        self.query_cmd.send([self.oid, 0, 0])
        self.bulk_queue.clear_queue()
        logging.info("Stopped encoder '%s' quadrature measurements",
                     self.name)

    def _process_batch_spi(self, eventtime):
        raw_samples = self.bulk_queue.pull_queue()
        if not raw_samples:
            return {}
        samples, error_count = self._extract_spi_samples(raw_samples)
        if not samples:
            return {}
        self._note_sample(samples[-1])
        return {"data": samples, "errors": error_count,
                "position": self.last_position}

    def _process_batch_quad(self, eventtime):
        raw_samples = self.bulk_queue.pull_queue()
        if not raw_samples:
            return {}
        samples, error_count = self._extract_quad_samples(raw_samples)
        if not samples:
            return {}
        self._note_sample(samples[-1])
        return {"data": samples, "errors": error_count,
                "position": self.last_position}

    def _note_sample(self, sample):
        # Keep the raw position along with the print time it was taken at.
        # The closed loop controller needs the timestamp to align the
        # measurement with the commanded position of the same instant.
        ptime, raw_pos = sample
        self.last_position = raw_pos
        self.last_sample = (ptime, raw_pos)

    def _extract_spi_samples(self, raw_samples):
        sample_ticks = self.sample_ticks
        start_clock = self.start_clock
        clock_to_print_time = self.mcu.clock_to_print_time
        last_sequence = self.last_sequence
        last_angle = self.last_angle
        time_shift = self.time_shift
        static_delay = self.sensor_helper.get_static_delay()
        count = error_count = 0
        samples = [None] * (len(raw_samples) * SAMPLES_PER_BLOCK)
        for params in raw_samples:
            seq_diff = (params["sequence"] - last_sequence) & 0xFFFF
            last_sequence += seq_diff
            samp_count = last_sequence * SAMPLES_PER_BLOCK
            msg_mclock = start_clock + samp_count * sample_ticks
            d = bytearray(params["data"])
            for i in range(len(d) // BYTES_PER_SAMPLE_SPI):
                idx = i * BYTES_PER_SAMPLE_SPI
                tcode = d[idx]
                if tcode == TCODE_ERROR:
                    error_count += 1
                    continue
                raw_angle = d[idx + 1] | (d[idx + 2] << 8)
                angle_diff = (raw_angle - last_angle) & 0xFFFF
                angle_diff -= (angle_diff & 0x8000) << 1
                last_angle += angle_diff
                mclock = msg_mclock + i * sample_ticks
                sclock = mclock + (tcode << time_shift)
                ptime = round(
                    clock_to_print_time(sclock) - static_delay, 6)
                samples[count] = (ptime, last_angle)
                count += 1
        self.last_sequence = last_sequence
        self.last_angle = last_angle
        del samples[count:]
        return samples, error_count

    def _extract_quad_samples(self, raw_samples):
        sample_ticks = self.sample_ticks
        start_clock = self.start_clock
        clock_to_print_time = self.mcu.clock_to_print_time
        last_sequence = self.last_sequence
        QUAD_PER_BLOCK = bulk_sensor.MAX_BULK_MSG_SIZE // BYTES_PER_SAMPLE_QUAD
        count = error_count = 0
        samples = [None] * (len(raw_samples) * QUAD_PER_BLOCK)
        for params in raw_samples:
            seq_diff = (params["sequence"] - last_sequence) & 0xFFFF
            last_sequence += seq_diff
            samp_count = last_sequence * QUAD_PER_BLOCK
            msg_mclock = start_clock + samp_count * sample_ticks
            d = bytearray(params["data"])
            for i in range(len(d) // BYTES_PER_SAMPLE_QUAD):
                idx = i * BYTES_PER_SAMPLE_QUAD
                raw_pos = (d[idx] | (d[idx + 1] << 8) |
                           (d[idx + 2] << 16) | (d[idx + 3] << 24))
                if raw_pos >= 0x80000000:
                    raw_pos -= 0x100000000
                diff = raw_pos - self.last_quad_position
                if diff > 0x3FFFFFFF:
                    diff -= 0x100000000
                elif diff < -0x40000000:
                    diff += 0x100000000
                self.last_quad_position += diff
                mclock = msg_mclock + i * sample_ticks
                ptime = round(clock_to_print_time(mclock), 6)
                samples[count] = (ptime, self.last_quad_position)
                count += 1
        self.last_sequence = last_sequence
        del samples[count:]
        return samples, error_count

    def cmd_ENCODER_POSITION(self, gcmd):
        pos = self.get_position()
        pos_mm = self.get_position_mm()
        gcmd.respond_info(
            "Encoder '%s': type=%s raw=%d position=%.4fmm"
            % (self.name, self.encoder_type, pos, pos_mm))
        if self.is_quadrature:
            gcmd.respond_info("  CPR=%d" % (self.cpr,))
        gcmd.respond_info("  scale=%.6f mm/rev invert=%s axis=%s"
                          % (self.scale or 0.0, self.invert,
                             self.axis or "n/a"))
        if self.stepper_name:
            gcmd.respond_info("  paired_stepper=%s" % (self.stepper_name,))
        sample = self.last_sample
        if sample is not None:
            gcmd.respond_info("  last sample print_time=%.6f" % (sample[0],))

    def cmd_ENCODER_RAW_DATA(self, gcmd):
        pos = self.get_position()
        gcmd.respond_info(
            "Encoder '%s' raw position: %d (0x%08x)"
            % (self.name, pos, pos & 0xFFFFFFFF))
        gcmd.respond_info(
            "  type=%s errors=%d"
            % (self.encoder_type, self.error_count))

    def get_status(self, eventtime=None):
        st = {"position": self.last_position,
              "position_mm": self.get_position_mm(),
              "encoder_type": self.encoder_type,
              "scale": self.scale,
              "invert": self.invert,
              "axis": self.axis}
        if self.is_quadrature:
            st["cpr"] = self.cpr
        else:
            st["temperature"] = self.sensor_helper.last_temperature
        return st

    def get_position(self):
        return self.last_position

    def get_position_mm(self):
        # Convert the raw sensor position into millimeters of axis travel
        return self._raw_to_mm(self.last_position)

    def _raw_to_mm(self, raw):
        scale = self.scale
        if scale is None:
            return 0.0
        if self.is_quadrature and self.cpr:
            val = raw * scale / self.cpr
        else:
            val = raw * scale / ANGLE_FULL_SCALE
        if self.invert:
            val = -val
        return val

    def get_latest_sample(self):
        # Return the (print_time, raw_position) of the most recent sample
        return self.last_sample

    def get_sample_mm(self, sample):
        # Convert a (print_time, raw_position) sample into axis travel (mm)
        return self._raw_to_mm(sample[1])

    def get_axis_index(self):
        # Index of the cartesian axis measured by this encoder
        if self.axis is None:
            return None
        return AXIS_LIST.index(self.axis)

    def add_client(self, client_cb):
        self.batch_bulk.add_client(client_cb)

    def _ensure_sampling(self):
        # The bulk sensor batch is only started when a client is attached.
        # Register an internal client so that measurements are always
        # running - otherwise the encoder would only report data while a
        # web client is connected to the "encoder/dump_encoder" endpoint.
        if self._sampling_active:
            return
        self._sampling_active = True

        def _internal_client(msg):
            return True

        self.batch_bulk.add_client(_internal_client)

    def _resolve_stepper_config(self, config):
        # Resolve the scale and the measured axis from the paired stepper.
        # This is done at config time so that a misconfiguration is
        # reported when the config is parsed.
        if self.stepper_name is None:
            return
        scfg = self.printer.lookup_object("configfile")
        try:
            ssection = scfg.getsection(self.stepper_name)
            self.rotation_distance = ssection.getfloat("rotation_distance")
        except Exception:
            # The stepper section is validated when the printer is ready
            pass
        if self.scale is None:
            self.scale = self.rotation_distance
        if self.axis is None:
            # Infer the measured axis from the stepper name
            for axis_name in AXIS_LIST:
                if self.stepper_name.endswith("_" + axis_name):
                    self.axis = axis_name
                    break
        if self.axis is None:
            raise config.error(
                "Encoder '%s': unable to determine the measured axis of"
                " stepper '%s' - set the 'axis' option explicitly"
                % (self.name, self.stepper_name))

    def _handle_ready(self):
        self._sampling_active = False
        if self.stepper_name is None:
            # Standalone encoder - still sample so the position is reported
            self._ensure_sampling()
            return
        try:
            fmove = self.printer.lookup_object("force_move")
            self.mcu_stepper = fmove.lookup_stepper(self.stepper_name)
        except self.printer.command_error:
            logging.warning(
                "Encoder '%s': referenced stepper '%s' not found",
                self.name, self.stepper_name)
            self._ensure_sampling()
            return
        closed_loop = self.printer.lookup_object("closed_loop", None)
        if closed_loop is not None:
            closed_loop.register_encoder(self)
        self._ensure_sampling()

    def get_stepper(self):
        return self.mcu_stepper


def load_config_prefix(config):
    return Encoder(config)
