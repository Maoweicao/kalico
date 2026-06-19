# 概述

欢迎阅读 Kalico 文档。如果你是 Kalico 新手，请从[功能](Features.md)和[安装](Installation.md)文档开始。

## 概述信息

- [功能](Features.md)：Kalico 功能的高级列表。
- [常见问题](FAQ.md)：常见问题解答。
- [配置更改](Config_Changes.md)：可能需要用户更新打印机配置文件的近期软件更改。
- [联系方式](Contact.md)：错误报告和与 Kalico 开发者一般通信的信息。

## 安装和配置

- [安装](Installation.md)：Kalico 安装指南。
  - [OctoPrint](OctoPrint.md)：使用 Kalico 安装 OctoPrint 的指南。
- [配置参考](Config_Reference.md)：配置参数说明。
  - [旋转距离](Rotation_Distance.md)：计算步进器 rotation_distance 参数。
- [配置检查](Config_checks.md)：验证配置文件中的基本引脚设置。
- [床面调平](Bed_Level.md)：Kalico 中"床面调平"的信息。
  - [Delta 校准](Delta_Calibrate.md)：Delta 运动学的校准。
  - [探针校准](Probe_Calibrate.md)：自动 Z 探针的校准。
  - [BL-Touch](BLTouch.md)：配置"BL-Touch"Z 探针。
  - [手动调平](Manual_Level.md)：Z 限位开关（及类似设备）的校准。
  - [床面网格](Bed_Mesh.md)：基于 XY 位置的床面高度校正。
  - [限位相位](Endstop_Phase.md)：步进器辅助的 Z 限位定位。
  - [轴扭曲补偿](Axis_Twist_Compensation.md)：补偿由于 X 架扭曲导致的不准确探针读数的工具。
- [共振补偿](Resonance_Compensation.md)：减少打印中振铃的工具。
  - [测量共振](Measuring_Resonances.md)：使用 adxl345 加速度计硬件测量共振的信息。
- [压力提前](Pressure_Advance.md)：校准挤出机压力。
- [G-Codes](G-Codes.md)：Kalico 支持的命令信息。
- [命令模板](Command_Templates.md)：G-Code 宏和条件评估。
  - [状态参考](Status_Reference.md)：宏可用的信息（及类似内容）。
- [TMC 驱动](TMC_Drivers.md)：在 Kalico 中使用 Trinamic 步进电机驱动。
- [多 MCU 归零](Multi_MCU_Homing.md)：使用多个微控制器进行归零和探测。
- [切片软件](Slicers.md)：为 Kalico 配置"切片软件"。
- [偏斜校正](Skew_Correction.md)：调整不完全方正的轴。
- [PWM 工具](Using_PWM_Tools.md)：如何使用 PWM 控制工具（如激光器或主轴）的指南。
- [排除对象](Exclude_Object.md)：排除对象实现指南。

## 开发者文档

- [代码概述](Code_Overview.md)：开发者应首先阅读此文档。
- [运动学](Kinematics.md)：Kalico 如何实现运动的技术细节。
- [协议](Protocol.md)：主机和微控制器之间低级消息传递协议的信息。
- [API 服务器](API_Server.md)：Kalico 命令和控制 API 的信息。
- [MCU 命令](MCU_Commands.md)：微控制器软件中实现的低级命令描述。
- [CAN 总线协议](CANBUS_protocol.md)：Kalico CAN 总线消息格式。
- [调试](Debugging.md)：如何测试和调试 Kalico 的信息。
- [基准测试](Benchmarks.md)：Kalico 基准测试方法的信息。
- [贡献](CONTRIBUTING.md)：如何提交对 Kalico 改进的信息。
- [打包](Packaging.md)：构建操作系统软件包的信息。

## 设备特定文档

- [示例配置](Example_Configs.md)：向 Kalico 添加示例配置文件的信息。
- [SD 卡更新](SDCard_Updates.md)：通过将二进制文件复制到微控制器的 SD 卡来刷写微控制器。
- [Raspberry Pi 作为微控制器](RPi_microcontroller.md)：控制连接到 Raspberry Pi GPIO 引脚的设备的详细信息。
- [Beaglebone](Beaglebone.md)：在 Beaglebone PRU 上运行 Kalico 的详细信息。
- [引导加载程序](Bootloaders.md)：微控制器刷写的开发者信息。
- [引导加载程序入口](Bootloader_Entry.md)：请求引导加载程序。
- [CAN 总线](CANBUS.md)：在 Kalico 中使用 CAN 总线的信息。
  - [CAN 总线故障排除](CANBUS_Troubleshooting.md)：CAN 总线故障排除提示。
- [TSL1401CL 耗材宽度传感器](TSL1401CL_Filament_Width_Sensor.md)
- [霍尔耗材宽度传感器](Hall_Filament_Width_Sensor.md)
- [称重传感器](Load_Cell.md)
