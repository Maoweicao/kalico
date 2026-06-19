# Kalico Printer Config Wizard

一个基于 Vue 3 + Vite + Element Plus 的交互式打印机配置向导工具。

## 功能特性

- 分步引导配置，适合新手使用
- 支持多种打印机类型（Cartesian、CoreXY、Delta等）
- 预置常见主板引脚配置（BTT SKR、Creality、MKS等）
- 实时预览生成的配置文件
- 支持导出 `.cfg` 和 `.json` 两种格式
- 每个配置项都有详细说明和帮助提示

## 配置阶段

### 基本配置
1. MCU连接方式（USB串口/CAN总线）
2. 打印机类型（运动学选择）
3. 运动参数（速度、加速度）
4. XYZ轴步进电机配置
5. 挤出机配置
6. 热床配置
7. 风扇配置

### 高级配置
8. TMC步进驱动配置
9. 探针配置（BLTouch等）
10. 热床网格调平
11. 输入整形（共振补偿）
12. 显示屏配置
13. 温度传感器

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 使用

1. 运行 `npm run dev` 启动开发服务器
2. 在浏览器中打开 http://localhost:5173
3. 按照向导一步步配置打印机参数
4. 完成后导出配置文件

## 技术栈

- Vue 3
- Vite
- Element Plus
- @element-plus/icons-vue
