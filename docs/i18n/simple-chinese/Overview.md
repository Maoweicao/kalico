# 概述

欢迎来到 Kalico 文档。如果初次使用 Kalico，请从[功能](Features.md)和[安装](Installation.md)文档开始。

## 概述信息

- [功能](Features.md)：Kalico 中功能的高级列表。
- [常见问题](FAQ.md)：常见问题。
- [配置更改](Config_Changes.md)：可能需要用户更新打印机配置文件的最近软件更改。
- [联系](Contact.md)：有关 bug 报告和与 Kalico 开发者一般通信的信息。

## 安装和配置

- [安装](Installation.md)：Kalico 安装指南。
  - [Octoprint](OctoPrint.md)：使用 Kalico 安装 Octoprint 的指南。
- [配置参考](Config_Reference.md)：配置参数说明。
  - [旋转距离](Rotation_Distance.md)：计算rotation_distance 步进电机参数。
- [配置检查](Config_checks.md)：验证配置文件中的基本针脚设置。
- [床面平整化](Bed_Level.md)：关于 Kalico 中"床面平整化"的信息。
  - [Delta 校准](Delta_Calibrate.md)：Delta 运动学校准。
  - [探针校准](Probe_Calibrate.md)：自动 Z 探针校准。
  - [BL-Touch](BLTouch.md)：配置"BL-Touch"Z 探针。
  - [手动调平](Manual_Level.md)：Z 限位开关（及类似）的校准。
  - [床面网格](Bed_Mesh.md)：基于 XY 位置的床面高度校正。
  - [限位阶段](Endstop_Phase.md)：步进电机辅助 Z 限位开关定位。
  - [轴扭转补偿](Axis_Twist_Compensation.md)：补偿由于 X 龙门架扭转导致的不准确探针读数的工具。
- [共振补偿](Resonance_Compensation.md)：减少打印中震铃的工具。
  - [测量共振](Measuring_Resonances.md)：关于使用 adxl345 加速度计硬件测量共振的信息。
- [压力提前](Pressure_Advance.md)：校准挤出机压力。
- [G 代码](G-Codes.md)：关于 Kalico 支持的命令的信息。
- [命令模板](Command_Templates.md)：G 代码宏和条件评估。
  - [状态参考](Status_Reference.md)：可用于宏的信息（及类似）。
- [TMC 驱动程序](TMC_Drivers.md)：使用 Trinamic 步进电机驱动程序与 Kalico。
- [多 MCU 归位](Multi_MCU_Homing.md)：使用多微控制器的归位和探针。
- [切片器](Slicers.md)：为 Kalico 配置"切片器"软件。
- [歪斜校正](Skew_Correction.md)：对轴不完全正方形的调整。
- [PWM 工具](Using_PWM_Tools.md)：如何使用 PWM 控制工具（如激光或主轴）的指南。
- [排除对象](Exclude_Object.md)：排除对象实现指南。

## 开发者文档

- [代码概述](Code_Overview.md)：开发者应首先阅读此内容。
- [运动学](Kinematics.md)：关于 Kalico 如何实现运动的技术详情。
- [协议](Protocol.md)：关于主机和微控制器之间的低级消息传递协议的信息。
- [API 服务器](API_Server.md)：关于 Kalico 的命令和控制 API 的信息。
- [MCU 命令](MCU_Commands.md)：微控制器软件中实现的低级命令说明。
- [CAN 总线协议](CANBUS_protocol.md)：Kalico CAN 总线消息格式。
- [调试](Debugging.md)：关于如何测试和调试 Kalico 的信息。
- [基准](Benchmarks.md)：关于 Kalico 基准方法的信息。
- [贡献](CONTRIBUTING.md)：关于如何向 Kalico 提交改进的信息。
- [打包](Packaging.md)：关于构建 OS 包的信息。

## 设备特定文档

- [示例配置](Example_Configs.md)：关于向 Kalico 添加示例配置文件的信息。
- [SDCard 更新](SDCard_Updates.md)：通过将二进制文件复制到微控制器中的 sdcard 来闪烁微控制器。
- [树莓派作为微控制器](RPi_microcontroller.md)：控制连接到树莓派 GPIO 针脚的设备的详情。
- [Beaglebone](Beaglebone.md)：在 Beaglebone PRU 上运行 Kalico 的详情。
- [引导加载程序](Bootloaders.md)：关于微控制器闪烁的开发者信息。
- [引导加载程序入口](Bootloader_Entry.md)：请求引导加载程序。
- [CAN 总线](CANBUS.md)：关于使用 CAN 总线与 Kalico 的信息。
  - [CAN 总线故障排除](CANBUS_Troubleshooting.md)：CAN 总线故障排除提示。
- [TSL1401CL 丝材宽度传感器](TSL1401CL_Filament_Width_Sensor.md)
- [Hall 丝材宽度传感器](Hall_Filament_Width_Sensor.md)
- [称重传感器](Load_Cell.md)