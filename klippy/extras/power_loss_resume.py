# Power Loss Resume - Resume printing after a power outage
# 断电续打 - 断电后恢复打印
#
# Copyright (C) 2024  Xiaok <xiaok@zxkxz.cn>
# Enhanced for kalico with bilingual support and improved reliability
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import json
import os
import logging
import io

INFO_FILE = ".power_loss_recover.json"


class PowerLossResume:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.printer.register_event_handler(
            "klippy:analyze_shutdown", self._handle_analyze_shutdown
        )
        self.printer.register_event_handler("klippy:ready", self._handle_ready)

        self.buttons = self.printer.load_object(config, "buttons")
        power_pin = config.get("power_pin")
        self.buttons.register_buttons([power_pin], self._power_button_handler)

        self.is_shutdown = config.getboolean("is_shutdown", True)
        self.paused_recover_z = config.getfloat("paused_recover_z", 0.0)
        self.layer_count = config.getint("layer_count", 0)
        gcode_macro = self.printer.load_object(config, "gcode_macro")
        self.shutdown_gcode = gcode_macro.load_template(config, "shutdown_gcode", "")
        self.layer_change_gcode = gcode_macro.load_template(
            config, "layer_change_gcode", ""
        )
        self.start_gcode = gcode_macro.load_template(config, "start_gcode")

        self.gcode_move = self.printer.load_object(config, "gcode_move")
        self.gcode = self.printer.lookup_object("gcode")

        # Virtual SD card / pause_resume objects
        self.virtual_sdcard = self.printer.lookup_object("virtual_sdcard", None)
        self.exclude_objects = self.printer.lookup_object("exclude_object", None)
        self.webhooks = self.printer.lookup_object("webhooks")

        # Print Stat Tracking
        self.print_stats = self.printer.load_object(config, "print_stats")

        self.power_loss_info = None
        self.sdcard_dirname = f"/usr/share/{INFO_FILE}"

        self.pheaters = None

        self.gcode.register_command(
            "START_POWER_LOSS_RESUME",
            self.cmd_START_POWER_LOSS_RESUME,
            desc=self.cmd_START_POWER_LOSS_RESUME_help,
        )
        self.gcode.register_command(
            "CLEAR_POWER_LOSS_RESUME",
            self.cmd_CLEAR_POWER_LOSS_RESUME,
            desc=self.cmd_CLEAR_POWER_LOSS_RESUME_help,
        )
        self.webhooks.register_endpoint(
            "power_loss_resume/start_print",
            self._handle_start_power_loss_resume,
        )
        self.webhooks.register_endpoint(
            "power_loss_resume/clear_info",
            self._handle_clear_power_loss_resume_info,
        )
        self.webhooks.register_endpoint(
            "power_loss_resume/get_info",
            self._handle_get_power_loss_resume_info,
        )

    def _is_printing(self):
        # Check if currently printing (adapted for kalico)
        if self.virtual_sdcard is not None and self.virtual_sdcard.is_active():
            return True
        return False

    def _is_paused(self):
        # Check if currently paused (adapted for kalico)
        pause_resume = self.printer.lookup_object("pause_resume", None)
        if pause_resume is not None:
            return pause_resume.is_paused
        return False

    def _handle_analyze_shutdown(self, msg, details):
        logging.info("power_loss_resume: analyze_shutdown triggered")
        self._save_power_loss_info()

    def _handle_ready(self):
        logging.info("power_loss_resume: ready")
        self.virtual_sdcard = self.printer.lookup_object("virtual_sdcard", None)
        self.exclude_objects = self.printer.lookup_object("exclude_object", None)
        if self.virtual_sdcard is None:
            raise self.printer.config_error(
                "virtual_sdcard not found. Cannot start power loss resume."
            )
        if hasattr(self.virtual_sdcard, "sdcard_dirname"):
            try:
                self.sdcard_dirname = os.path.join(
                    os.path.dirname(self.virtual_sdcard.sdcard_dirname), INFO_FILE
                )
            except ValueError:
                raise self.printer.config_error(
                    "virtual_sdcard.sdcard_dirname not found. "
                    "Cannot start power loss resume."
                )
        if self.sdcard_dirname is None:
            raise self.printer.config_error(
                "sdcard_dirname not found. Cannot start power loss resume."
            )
        self.pheaters = self.printer.lookup_object("heaters", None)
        if self.pheaters is None:
            raise self.printer.config_error(
                "heaters not found. Cannot start power loss resume."
            )
        self._read_power_loss_info()

    def get_status(self, eventtime):
        if (
            self.power_loss_info is not None
            and "power_loss_resume" in self.power_loss_info
        ):
            if (
                "file_path" in self.power_loss_info
                and self.power_loss_info["file_path"] is not None
                and self.power_loss_info["file_path"] != ""
                and "print_stats" in self.power_loss_info
                and self.power_loss_info["print_stats"]["filename"] is not None
                and self.power_loss_info["print_stats"]["filename"] != ""
            ):
                power_loss_resume = self.power_loss_info["power_loss_resume"]
            else:
                power_loss_resume = False
        else:
            power_loss_resume = False
        return {"power_loss_resume": power_loss_resume}

    cmd_CLEAR_POWER_LOSS_RESUME_help = (
        "Clear power loss resume info / 清除断电续打信息"
    )

    def cmd_CLEAR_POWER_LOSS_RESUME(self, gcmd):
        self._save_power_loss_info(False)
        gcmd.respond_raw("Power loss resume info cleared / 断电续打信息已清除")

    cmd_START_POWER_LOSS_RESUME_help = (
        "Start power loss resume print / 开始断电续打"
    )

    def cmd_START_POWER_LOSS_RESUME(self, gcmd):
        if self.virtual_sdcard.work_timer is not None:
            gcmd.respond_raw(
                "Printing in progress. Unable to operate. / "
                "正在打印中，无法操作"
            )
            return
        if self.power_loss_info is None:
            gcmd.respond_raw("No power loss info found. / 未找到断电续打信息")
            return
        self.reactor.register_async_callback(
            (lambda e: self._handle_power_loss_resume())
        )
        gcmd.respond_raw("Start power loss resume / 开始断电续打")

    def _handle_start_power_loss_resume(self, web_request):
        if self.virtual_sdcard.work_timer is not None:
            web_request.send(
                {"msg": "Printing in progress. Unable to operate."}
            )
            return
        if self.power_loss_info is None:
            web_request.send({"msg": "No power loss info found."})
            return
        self.reactor.register_async_callback(
            (lambda e: self._handle_power_loss_resume())
        )
        web_request.send({"msg": "Start power loss resume"})

    def _handle_clear_power_loss_resume_info(self, web_request):
        self._save_power_loss_info(False)
        web_request.send({"msg": "Clear power loss resume info"})

    def _handle_get_power_loss_resume_info(self, web_request):
        if (
            self.power_loss_info is not None
            and "power_loss_resume" in self.power_loss_info
        ):
            if (
                "file_path" in self.power_loss_info
                and self.power_loss_info["file_path"] is not None
                and self.power_loss_info["file_path"] != ""
                and "print_stats" in self.power_loss_info
                and self.power_loss_info["print_stats"]["filename"] is not None
                and self.power_loss_info["print_stats"]["filename"] != ""
            ):
                power_loss_resume = self.power_loss_info["power_loss_resume"]
            else:
                power_loss_resume = False
        else:
            power_loss_resume = False
        ret = {
            "power_loss_resume": power_loss_resume,
            "file_path": (
                self.power_loss_info["file_path"] if power_loss_resume else None
            ),
            "progress": (
                self.power_loss_info["progress"] if power_loss_resume else 0
            ),
            "filename": (
                self.power_loss_info["print_stats"]["filename"]
                if power_loss_resume
                else None
            ),
        }
        web_request.send({"power_loss_info": ret})

    def _read_power_loss_info(self):
        if os.path.exists(self.sdcard_dirname):
            with open(self.sdcard_dirname, "r", encoding="utf-8") as file:
                try:
                    text = file.read()
                    text = text.encode("utf-8").decode("unicode_escape")
                    self.power_loss_info = json.loads(text)
                except Exception:
                    logging.exception("power_loss_resume: JSON load error")
                    self.power_loss_info = None
        else:
            self.power_loss_info = None

    def _save_power_loss_info(self, is_power_loss=True):
        if is_power_loss and self._is_printing():
            eventtime = self.reactor.monotonic()
            # Get all heater temperatures / 获取所有温度
            heaters = {}
            if self.pheaters is not None:
                for heater_name in self.pheaters.get_all_heaters():
                    heater = self.pheaters.lookup_heater(heater_name.split()[-1])
                    temperature, target = heater.get_temp(eventtime)
                    heaters[heater_name] = {
                        "name": heater_name.split()[-1],
                        "temperature": temperature,
                        "target": target,
                    }
            # Get gcode move status / 获取gcode移动状态
            gcodestatus = self.gcode_move.get_status()
            # Get print stats / 获取打印状态
            printstats = self.print_stats.get_status(eventtime)
            # Get fan speed / 获取风扇速度
            fan = self.printer.lookup_object("fan", None)
            # Get toolhead status / 获取toolhead
            toolhead = self.printer.lookup_object("toolhead", None)
            toolhead_status = None
            if toolhead is not None:
                toolhead_status = toolhead.get_status(eventtime)
            # Get dual carriage status / 获取dual_carriage
            dual_carriage = self.printer.lookup_object("dual_carriage", None)
            dual_carriage_status = None
            if dual_carriage is not None:
                dual_carriage_status = dual_carriage.get_status(eventtime)
            if (
                printstats["filename"] == ""
                and self.power_loss_info is not None
                and "print_stats" in self.power_loss_info
            ):
                printstats = self.power_loss_info["print_stats"]
            current_object = ""
            if self.exclude_objects is not None:
                current_object = self.exclude_objects.current_object
            fan_speed = 255
            if fan is not None:
                fan_speed = int(fan.get_status(eventtime)["speed"] * 255)
            # Build state snapshot / 生成数据
            self.power_loss_info = {
                "power_loss_resume": True,
                "is_paused": self._is_paused(),
                "file_path": self.virtual_sdcard.file_path(),
                "progress": self.virtual_sdcard.progress(),
                "is_active": self.virtual_sdcard.is_active(),
                "file_size": self.virtual_sdcard.file_size,
                "gcode_move": gcodestatus,
                "print_stats": printstats,
                "heaters": heaters,
                "toolhead": toolhead_status,
                "dual_carriage": dual_carriage_status,
                "file_position": self.virtual_sdcard.file_position,
                "next_file_position": self.virtual_sdcard.next_file_position,
                "current_object": current_object,
                "fan_speed": fan_speed,
                "move_speed_percent": gcodestatus["speed_factor"] * 100,
                "extrude_speed_percent": gcodestatus["extrude_factor"] * 100,
            }
        else:
            self.power_loss_info = {"power_loss_resume": False}
        logging.info(
            "power_loss_resume: saving info - %s",
            json.dumps(self.power_loss_info, indent=4),
        )
        with open(self.sdcard_dirname, "w") as file:
            json.dump(self.power_loss_info, file)
            os.fsync(file.fileno())

    def _shutdown(self):
        try:
            self.gcode.run_script(self.shutdown_gcode.render())
        except Exception:
            logging.exception("power_loss_resume: shutdown gcode error")
        try:
            if self.is_shutdown:
                self.webhooks.call_remote_method("shutdown_machine")
        except self.printer.command_error:
            logging.exception("power_loss_resume: remote call error")

    def _power_button_handler(self, eventtime, state):
        if state == 0:
            # Power loss detected / 检测到断电
            logging.info("power_loss_resume: power loss detected, shutting down")
            self._save_power_loss_info()
            self._shutdown()

    def run_layer_change_gcode(self):
        logging.info("power_loss_resume: layer change gcode")
        if self.layer_change_gcode is not None and self.layer_change_gcode != "":
            try:
                self.gcode.run_script(
                    self.layer_change_gcode.render(
                        context=self.layer_change_gcode_context
                    )
                )
            except Exception:
                logging.exception("power_loss_resume: layer change gcode error")

    def _handle_power_loss_resume(self):
        if self.power_loss_info is None:
            self.gcode._respond_error(
                "No power loss info found / 未找到断电续打信息"
            )
            return
        if (
            self.power_loss_info["power_loss_resume"] is False
            or self.power_loss_info["file_path"] is None
        ):
            self.gcode._respond_error(
                "No print to resume / 没有需要续打的打印任务"
            )
            return
        if (
            "file_path" in self.power_loss_info
            and self.power_loss_info["file_path"] is not None
            and self.power_loss_info["file_path"] != ""
            and "print_stats" in self.power_loss_info
            and self.power_loss_info["print_stats"]["filename"] is not None
            and self.power_loss_info["print_stats"]["filename"] != ""
            and "file_size" in self.power_loss_info
            and "gcode_move" in self.power_loss_info
        ):
            self.gcode.respond_raw("Resuming print / 正在恢复打印")
        else:
            self.gcode._respond_error(
                "Power loss info incomplete / 续打信息不完整"
            )
            return
        self.virtual_sdcard._reset_file()
        # Restore print stats / 恢复打印统计信息
        self.print_stats.filename = self.power_loss_info["print_stats"]["filename"]
        self.print_stats.total_duration = self.power_loss_info["print_stats"][
            "total_duration"
        ]
        self.print_stats.filament_used = self.power_loss_info["print_stats"][
            "filament_used"
        ]
        self.print_stats.state = self.power_loss_info["print_stats"]["state"]
        self.print_stats.error_message = self.power_loss_info["print_stats"][
            "message"
        ]
        self.print_stats.info_total_layer = self.power_loss_info["print_stats"][
            "info"
        ]["total_layer"]
        self.print_stats.info_current_layer = self.power_loss_info["print_stats"][
            "info"
        ]["current_layer"]
        filename = self.power_loss_info["print_stats"]["filename"]
        if filename is None or filename == "":
            filename = os.path.basename(self.power_loss_info["file_path"])
        if filename is None or filename == "":
            self.gcode._respond_error(
                "Resume file not found / 未找到续打文件"
            )
            return
        self.print_stats.set_current_file(filename)
        self.print_stats.note_start()

        x = self.power_loss_info["gcode_move"]["gcode_position"][0]
        y = self.power_loss_info["gcode_move"]["gcode_position"][1]
        z = self.power_loss_info["gcode_move"]["gcode_position"][2]
        e = self.power_loss_info["gcode_move"]["gcode_position"][3]

        # Force set toolhead position / 强制设置工具头位置
        toolhead = self.printer.lookup_object("toolhead")
        toolhead.get_last_move_time()
        curpos = toolhead.get_position()
        toolhead.set_position([x, y, z, curpos[3]], homing_axes="xyz")

        # Extract extruder and bed temperatures / 单独提取挤出与热床温度信息
        extruder = self.power_loss_info["heaters"].get(
            "extruder", {"temp": 0, "target": 0}
        )
        bed = self.power_loss_info["heaters"].get(
            "heater_bed", {"temp": 0, "target": 0}
        )
        # Build PLR context for Jinja2 template / 将断电数据写入jinja2模版参数
        plr = {
            "POS_X": x,
            "POS_Y": y,
            "POS_Z": z,
            "POS_E": e,
            "extruder": extruder,
            "bed": bed,
        }
        plr.update(self.power_loss_info)
        context = self.start_gcode.create_template_context()
        context.update({"PLR": plr})

        if self.layer_change_gcode is not None and self.layer_change_gcode != "":
            self.layer_change_gcode_context = (
                self.layer_change_gcode.create_template_context()
            )
            self.layer_change_gcode_context.update({"PLR": plr})

        # Set coordinate commands / 设置坐标信息
        lines = []
        lines.append("G1 F%s" % self.power_loss_info["gcode_move"]["speed"])
        lines.append("G90")
        lines.append("G1 X%.4f Y%.4f Z%.4f" % (x, y, z))
        if self.power_loss_info["is_paused"] and self.paused_recover_z > 0.0:
            lines.append("G91")
            lines.append("G1 Z%.4f" % self.paused_recover_z)
        if self.power_loss_info["gcode_move"]["absolute_coordinates"]:
            lines.append("G90")
        else:
            lines.append("G91")
        if self.power_loss_info["gcode_move"]["absolute_extrude"]:
            lines.append("M82")
        else:
            lines.append("M83")
        lines.append("G92 E%.4f" % e)

        # Execute start gcode macro / 执行gcode宏
        try:
            self.gcode.run_script(self.start_gcode.render(context=context))
            if len(lines) > 0:
                for line in lines:
                    self.gcode.run_script(line)
        except Exception:
            logging.exception("power_loss_resume: script running error")

        # Open file and seek to saved position / 调用virtual_sdcard从指定位置加载文件
        try:
            current_position = self.power_loss_info["file_position"]
            f = io.open(
                self.power_loss_info["file_path"],
                "r",
                newline="",
                errors="ignore",
            )
            self.virtual_sdcard._gcode_file_path = self.power_loss_info["file_path"]
            f.seek(0, os.SEEK_END)
            fsize = f.tell()
            f.seek(self.virtual_sdcard.file_position)
            # Backtrack to the previous newline boundary / 回退到前一行的换行符位置
            while current_position > 0:
                current_position -= 1
                f.seek(current_position)
                char = f.read(1)
                if char == "\n":
                    break
            self.virtual_sdcard.file_position = current_position
        except Exception:
            logging.exception("power_loss_resume: virtual_sdcard file open")
            self.gcode._respond_error("Unable to open file / 无法打开文件")
            return
        self.virtual_sdcard.current_file = f
        self.virtual_sdcard.file_size = fsize
        self.virtual_sdcard.current_file.seek(self.virtual_sdcard.file_position)
        self.virtual_sdcard.is_pwr_loss_resume = True
        self.virtual_sdcard.layer_change_count = 0
        self.virtual_sdcard.is_resume_speed = True
        # Start printing / 开始打印
        self.virtual_sdcard.do_resume()

        # Clear power loss data / 清除断电数据
        self._save_power_loss_info(False)
        logging.info("power_loss_resume: print resumed successfully")


def load_config(config):
    return PowerLossResume(config)
