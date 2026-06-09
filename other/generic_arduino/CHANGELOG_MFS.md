# 2026-06-04 MFS 固件优化

## 问题
generic_arduino 固件刷入后蜂鸣器一直响。

## 原因
hw262 的蜂鸣器是低电平有效（active LOW），Arduino 启动时引脚默认是 INPUT 浮空状态，导致蜂鸣器误触发。

## 解决方案
1. 添加 `initial_pins.c`，在固件启动时初始化 hw262 的引脚：
   - 蜂鸣器 D3: OUTPUT HIGH（关闭）
   - LED D10-D13: OUTPUT HIGH（关闭）
   - 显示引脚 D4,D7,D8: OUTPUT LOW（安全状态）

2. 在 `main.cpp` 的 `setup()` 中调用 `initial_pins_setup()`

3. 更新 `printer.cfg` 中 LED 引脚为 hw262 标准配置：
   - led_d1: ar10 (D10)
   - led_d2: ar11 (D11)
   - led_d3: ar12 (D12)
   - led_d4: ar13 (D13)

## 编译结果
- RAM: 67.6% (1385/2048 bytes)
- Flash: 50.0% (16124/32256 bytes)

## 测试文件
- `/home/mellow/printer_data/gcodes/mfs_test.gcode`
- 测试命令: MFS_TEST, MFS_BUZZER_TEST, MFS_DISPLAY_TEST, MFS_LED_TEST
