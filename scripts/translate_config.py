#!/usr/bin/env python3
"""
Translate Config_Reference.md from English to Chinese.
Reads docs/Config_Reference.md and writes to docs/i18n/simple-chinese/Config_Reference.md
"""

import os
import re

INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "Config_Reference.md")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "i18n", "simple-chinese", "Config_Reference.md")

HEADER_TRANSLATIONS = {
    "# Configuration reference": "# 配置参考",
    "## Micro-controller configuration": "## 微控制器配置",
    "## ⚠️ Danger Options": "## ⚠️ 危险选项",
    "## ⚠️ Configuration references": "## ⚠️ 配置引用",
    "## Common kinematic settings": "## 通用运动学设置",
    "## Common extruder and heated bed support": "## 通用挤出机和热床支持",
    "## Custom heaters and sensors": "## 自定义加热器和传感器",
    "## Bed level support": "## 调平支持",
    "## Bed probing hardware": "## 床探测硬件",
    "## Additional stepper motors and extruders": "## 额外步进电机和挤出机",
    "## Additional servos, buttons, and other pins": "## 额外伺服、按钮和其他引脚",
    "## Display support": "## 显示屏支持",
    "## LEDs": "## LED灯",
    "## Fans": "## 风扇",
    "## Filament sensors": "## 耗材传感器",
    "## G-Code macros and events": "## G-Code宏和事件",
    "## Other Custom Modules": "## 其他自定义模块",
    "## Load Cells": "## 称重传感器",
    "## Resonance compensation": "## 共振补偿",
    "## Config file helpers": "## 配置文件辅助工具",
    "## Customized homing": "## 自定义归位",
    "## TMC stepper driver configuration": "## TMC步进驱动配置",
    "## Temperature sensors": "## 温度传感器",
    "## Run-time stepper motor current configuration": "## 运行时步进电机电流配置",
    "## Board specific hardware support": "## 特定硬件支持",
    "## Optional G-Code features": "## 可选G-Code功能",
    "## CANopen servo stepper support": "## CANopen伺服步进支持",
    "## Common bus parameters": "## 总线通用参数",
    "## EtherCAT servo stepper support": "## EtherCAT伺服步进支持",
    "## RS485 servo stepper support": "## RS485伺服步进支持",
    "## External pulse generator stepper support": "## 外部脉冲发生器步进支持",
    "## Servo safety monitoring": "## 伺服安全监控",
    "### Format of micro-controller pin names": "### 微控制器引脚名称格式",
    "### Common SPI settings": "### SPI通用设置",
    "### Common I2C settings": "### I2C通用设置",
    "### Common temperature amplifiers": "### 温度放大器通用设置",
    "### Common thermistors": "### 热敏电阻通用设置",
    "### Dummy thermistor": "### 假热敏传感器",
    "### Directly connected PT1000 sensor": "### 直连PT1000传感器",
    "### MAXxxxxx temperature sensors": "### MAXxxxxx温度传感器",
    "### BMP180/BMP280/BME280/BMP388/BME680 temperature sensor": "### BMP180/BMP280/BME280/BMP388/BME680温度传感器",
    "### AHT10/AHT20/AHT21/AHT30 temperature sensor": "### AHT10/AHT20/AHT21/AHT30温度传感器",
    "### HTU21D sensor": "### HTU21D传感器",
    "### SHT3X sensor": "### SHT3X传感器",
    "### Builtin micro-controller temperature sensor": "### 内置微控制器温度传感器",
    "### Host temperature sensor": "### 主机温度传感器",
    "### DS18B20 temperature sensor": "### DS18B20温度传感器",
    "### Combined temperature sensor": "### 组合温度传感器",
    "### LM75 temperature sensor": "### LM75温度传感器",
    "### INDX temperature sensor": "### INDX温度传感器",
    "### MPC Ambient Sensor": "### MPC环境传感器",
    "### MPC Block Sensor": "### MPC块传感器",
    "### Cartesian Kinematics": "### 直角坐标运动学",
    "### CoreXY Kinematics": "### CoreXY运动学",
    "### CoreXZ Kinematics": "### CoreXZ运动学",
    "### Linear Delta Kinematics": "### 线性Delta运动学",
    "### Rotary delta Kinematics": "### 旋转Delta运动学",
    "### Deltesian Kinematics": "### Deltesian运动学",
    "### Polar Kinematics": "### 极坐标运动学",
    "### Hybrid-CoreXY Kinematics": "### 混合CoreXY运动学",
    "### Hybrid-CoreXZ Kinematics": "### 混合CoreXZ运动学",
    "### Cable winch Kinematics": "### 缆绳绞车运动学",
    "### None Kinematics": "### 无运动学",
    "### ⚠️ Cartesian Kinematics with limits for X and Y axes": "### ⚠️ 带X和Y轴限制的直角坐标运动学",
    "### ⚠️ CoreXY Kinematics with limits for X and Y axes": "### ⚠️ 带X和Y轴限制的CoreXY运动学",
    "### ⚠️ CoreXZ Kinematics with limits for X and Y axes": "### ⚠️ 带X和Y轴限制的CoreXZ运动学",
    "### ⚠️ [dockable_probe]": "### ⚠️ [dockable_probe]",
    "### ⚠️ [force_move]": "### ⚠️ [force_move]",
    "### ⚠️ [menu]": "### ⚠️ [menu]",
    "### ⚠️ [tools_calibrate]": "### ⚠️ [tools_calibrate]",
    "### ⚠️ [z_calibration]": "### ⚠️ [z_calibration]",
    "#### HC595 Wiring": "#### HC595接线",
    "#### HC595 Usage Example": "#### HC595使用示例",
    "#### hd44780 display": "#### hd44780显示屏",
    "#### hd44780_spi display": "#### hd44780_spi显示屏",
    "#### aip31068_spi display": "#### aip31068_spi显示屏",
    "#### st7920 display": "#### st7920显示屏",
    "#### emulated_st7920 display": "#### emulated_st7920显示屏",
    "#### uc1701 display": "#### uc1701显示屏",
    "#### ssd1306 and sh1106 displays": "#### ssd1306和sh1106显示屏",
    "#### HX711": "#### HX711",
    "#### HX717": "#### HX717",
    "#### ADS1220": "#### ADS1220",
    "#### ADS131M02": "#### ADS131M02",
    "#### ADS131M04": "#### ADS131M04",
    "#### [z_tilt_ng]": "#### [z_tilt_ng]",
}

def normalize_ws(text):
    return re.sub(r"\s+", " ", text.strip())

PARA_CACHE = {}
COMMENT_CACHE = {}

def load_dictionaries():
    return HEADER_TRANSLATIONS

def translate_header(line):
    stripped = line.rstrip()
    return HEADER_TRANSLATIONS.get(stripped, line)

def translate_paragraph(text):
    key = normalize_ws(text)
    if key in PARA_CACHE:
        return PARA_CACHE[key]
    return None

def translate_comment_block(text):
    key = normalize_ws(text)
    if key in COMMENT_CACHE:
        return COMMENT_CACHE[key]
    return None

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    output_lines = []
    in_code_block = False
    para_buffer = []
    comment_buffer = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip("\n")

        # Track code blocks
        if stripped.startswith("```"):
            # Flush paragraph buffer before code block
            if para_buffer:
                joined = "\n".join(para_buffer)
                translated = translate_paragraph(joined)
                if translated:
                    output_lines.append(translated + "\n")
                else:
                    output_lines.extend([l + "\n" for l in para_buffer])
                para_buffer = []
            # Flush comment buffer at end of code block
            if in_code_block and comment_buffer:
                joined = "\n".join(comment_buffer)
                translated = translate_comment_block(joined)
                if translated:
                    output_lines.append(translated + "\n")
                    comment_buffer = []
                else:
                    # Try to translate each line individually
                    for cb in comment_buffer:
                        output_lines.append(cb + "\n")
                    comment_buffer = []
            in_code_block = not in_code_block
            output_lines.append(line)
            i += 1
            continue

        if in_code_block:
            # Inside code block: collect comment lines
            is_comment = re.match(r"^#\s{3,}", stripped) or re.match(r"^#$", stripped)
            if is_comment or (stripped.startswith("#") and not re.match(r"^#\w", stripped)):
                # Check if it's a config line (#key: value)
                if re.match(r"^#\w+:", stripped) or re.match(r"^#\s+\w+:", stripped):
                    # This is a config line, not a descriptive comment
                    if comment_buffer:
                        joined = "\n".join(comment_buffer)
                        translated = translate_comment_block(joined)
                        if translated:
                            output_lines.append(translated + "\n")
                        else:
                            for cb in comment_buffer:
                                output_lines.append(cb + "\n")
                        comment_buffer = []
                    output_lines.append(line)
                else:
                    comment_buffer.append(stripped)
            else:
                # Non-comment line in code block
                if comment_buffer:
                    joined = "\n".join(comment_buffer)
                    translated = translate_comment_block(joined)
                    if translated:
                        output_lines.append(translated + "\n")
                    else:
                        for cb in comment_buffer:
                            output_lines.append(cb + "\n")
                    comment_buffer = []
                output_lines.append(line)
        else:
            # Outside code block
            # Check for headers
            if stripped.startswith("#"):
                # Flush paragraph buffer
                if para_buffer:
                    joined = "\n".join(para_buffer)
                    translated = translate_paragraph(joined)
                    if translated:
                        output_lines.append(translated + "\n")
                    else:
                        output_lines.extend([l + "\n" for l in para_buffer])
                    para_buffer = []
                # Translate header
                translated = translate_header(stripped)
                output_lines.append(translated + "\n")
            elif stripped == "":
                # Empty line - flush paragraph buffer
                if para_buffer:
                    joined = "\n".join(para_buffer)
                    translated = translate_paragraph(joined)
                    if translated:
                        output_lines.append(translated + "\n")
                    else:
                        output_lines.extend([l + "\n" for l in para_buffer])
                    para_buffer = []
                output_lines.append(line)
            else:
                # Text line - add to paragraph buffer
                para_buffer.append(stripped)

        i += 1

    # Flush remaining buffers
    if comment_buffer:
        joined = "\n".join(comment_buffer)
        translated = translate_comment_block(joined)
        if translated:
            output_lines.append(translated + "\n")
        else:
            for cb in comment_buffer:
                output_lines.append(cb + "\n")
    if para_buffer:
        joined = "\n".join(para_buffer)
        translated = translate_paragraph(joined)
        if translated:
            output_lines.append(translated + "\n")
        else:
            output_lines.extend([l + "\n" for l in para_buffer])

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(output_lines)
    print(f"Translation complete. Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
