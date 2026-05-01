# Support for 74HC595 shift register output expansion
#
# Copyright (C) 2025  KalicoCrew <https://github.com/KalicoCrew/kalico>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

from . import bus

BACKGROUND_PRIORITY_CLOCK = 0x7FFFFFFF00000000

# Maximum number of daisy-chained 74HC595 chips supported
MAX_CHAIN_COUNT = 4  # Up to 4 chained = 32 outputs


class HC595:
    def __init__(self, config):
        self.printer = config.get_printer()
        ppins = self.printer.lookup_object("pins")
        # Read configuration
        self.chain_count = config.getint(
            "chain_count", 1, minval=1, maxval=MAX_CHAIN_COUNT
        )
        self.total_outputs = self.chain_count * 8
        # The 74HC595 uses a 3-wire SPI-like protocol:
        #   DATA (SER, pin 14), CLOCK (SRCLK, pin 11), LATCH (RCLK, pin 12)
        # We use software SPI where MOSI=DATA, SCLK=CLOCK, and the SPI
        # CS pin acts as LATCH.  SPI mode 0 with CS active-low gives:
        #   CS low  -> shift data -> CS high (rising edge = latch)
        # This matches the 74HC595 timing perfectly.
        data_pin = config.get("data_pin")
        clock_pin = config.get("clock_pin")
        latch_pin = config.get("latch_pin")
        data_params = ppins.lookup_pin(data_pin)
        clock_params = ppins.lookup_pin(clock_pin)
        latch_params = ppins.lookup_pin(latch_pin)
        mcu = data_params["chip"]
        if (mcu is not clock_params["chip"]
                or mcu is not latch_params["chip"]):
            raise config.error(
                "HC595 pins must be on the same MCU"
            )
        self.mcu = mcu
        # Setup software SPI with latch pin as CS
        sw_spi_pins = (
            data_params["pin"],   # MISO (unused, set same as MOSI)
            data_params["pin"],   # MOSI (DATA/SER)
            clock_params["pin"],  # SCLK (CLOCK/SRCLK)
        )
        self.spi = bus.MCU_SPI(
            mcu, None, latch_params["pin"], 0, 1000000, sw_spi_pins
        )
        # Setup OE pin if configured (active low, enable outputs)
        self.oe_pin = config.get("oe_pin", None)
        self.mcu_oe = None
        if self.oe_pin is not None:
            self.mcu_oe = ppins.setup_pin("digital_out", self.oe_pin)
            self.mcu_oe.setup_max_duration(0.0)
            self.mcu_oe.setup_start_value(0, 0)
        # Register chip with pin system
        chip_name = config.get_name().split()[1] if len(
            config.get_name().split()
        ) > 1 else "hc595"
        try:
            ppins.register_chip(chip_name, self)
        except ppins.error as e:
            raise config.error(
                "Unable to register HC595 chip '%s': %s"
                % (chip_name, str(e))
            )
        # State tracking
        self.pin_states = bytearray(self.total_outputs)
        self.pin_objects = {}
        self.dirty = False
        self.initialized = False
        # Register event handlers
        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )
        self.name = chip_name
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command(
            "SET_HC595",
            "CHIP",
            self.name,
            self.cmd_SET_HC595,
            desc=self.cmd_SET_HC595_help,
        )

    def _handle_connect(self):
        # SPI is now configured, perform initial shift-out with
        # accumulated pin states
        self.initialized = True
        self._shift_out()

    def setup_pin(self, pin_type, pin_params):
        if pin_type != "digital_out":
            raise self.printer.lookup_object("pins").error(
                "HC595 only supports digital_out pins"
            )
        pin_name = pin_params["pin"]
        try:
            pin_num = int(pin_name)
        except ValueError:
            raise self.printer.lookup_object("pins").error(
                "HC595 pin must be an integer (0-%d), got '%s'"
                % (self.total_outputs - 1, pin_name)
            )
        if pin_num < 0 or pin_num >= self.total_outputs:
            raise self.printer.lookup_object("pins").error(
                "HC595 pin %d out of range (0-%d)"
                % (pin_num, self.total_outputs - 1)
            )
        if pin_num in self.pin_objects:
            return self.pin_objects[pin_num]
        pin_obj = HC595Pin(self, pin_num, pin_params["invert"])
        self.pin_objects[pin_num] = pin_obj
        return pin_obj

    def _shift_out(self, print_time=None):
        """Send current pin states to the shift register(s) via SPI.
        The SPI CS pin acts as the 74HC595 latch: CS goes low during
        data transfer, then high after - the rising edge latches
        the shifted data to the output pins."""
        if print_time is None:
            print_time = self.mcu.estimated_print_time(
                self.printer.get_reactor().monotonic()
            )
        clock = self.mcu.print_time_to_clock(print_time)
        # Build data bytes (first byte sent ends up in the last
        # chip of the daisy chain)
        data = bytearray(self.chain_count)
        for chip in range(self.chain_count):
            byte_val = 0
            base = chip * 8
            for bit in range(8):
                if self.pin_states[base + bit]:
                    byte_val |= 1 << bit
            data[self.chain_count - 1 - chip] = byte_val
        # SPI handles CS (latch) automatically
        self.spi.spi_send(data, minclock=clock, reqclock=clock)
        self.dirty = False

    def _schedule_update(self):
        if self.dirty:
            self._shift_out()

    def set_output(self, pin_num, value):
        if self.pin_states[pin_num] == value:
            return
        self.pin_states[pin_num] = value
        self.dirty = True
        if self.initialized:
            self._schedule_update()

    def get_status(self, eventtime):
        return {
            "pin_states": self.pin_states[:],
            "chain_count": self.chain_count,
        }

    cmd_SET_HC595_help = (
        "Set all HC595 output pins at once (for debugging/testing)"
    )

    def cmd_SET_HC595(self, gcmd):
        bits = gcmd.get_int("BITS", None)
        if bits is not None:
            for i in range(self.total_outputs):
                self.pin_states[i] = (bits >> i) & 1
            self.dirty = True
            self._schedule_update()
            gcmd.respond_info(
                "HC595 '%s' outputs set to 0x%x" % (self.name, bits)
            )
        else:
            state = 0
            for i in range(self.total_outputs):
                state |= self.pin_states[i] << i
            gcmd.respond_info(
                "HC595 '%s' current outputs: 0x%x" % (self.name, state)
            )


class HC595Pin:
    def __init__(self, hc595, pin_num, invert):
        self._hc595 = hc595
        self._pin_num = pin_num
        self._invert = invert
        self._start_value = 0
        self._shutdown_value = 0

    def get_mcu(self):
        return self._hc595.mcu

    def setup_max_duration(self, max_duration):
        pass  # No max duration enforcement needed

    def setup_start_value(self, start_value, shutdown_value):
        self._start_value = start_value ^ self._invert
        self._shutdown_value = shutdown_value ^ self._invert
        # Apply start value
        self._hc595.set_output(self._pin_num, self._start_value)

    def setup_cycle_time(self, cycle_time, hardware_pwm=False):
        raise self._hc595.printer.lookup_object("pins").error(
            "HC595 does not support PWM"
        )

    def set_digital(self, print_time, value):
        self._hc595.set_output(self._pin_num, (not not value) ^ self._invert)

    def set_pwm(self, print_time, value):
        raise self._hc595.printer.lookup_object("pins").error(
            "HC595 does not support PWM"
        )


def load_config_prefix(config):
    return HC595(config)
