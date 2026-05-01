# 从 Klipper 迁移

> [!NOTE]
> 使用的任何附加组件模块都需要在切换到 Kalico 后重新安装。这包括诸如 Beacon 支持、led-effect 等内容。
>
> ~/printer_data 中的任何数据（如打印机配置和宏）都将不受影响，尽管最好进行备份。

### 选项 1. 手动克隆存储库

如果需要，通过运行以下命令进行现有 Klipper 安装的备份副本：

```bash
mv ~/klipper ~/klipper_old
```

然后克隆 Kalico 存储库并重新启动 klipper 服务：

```bash
git clone https://github.com/KalicoCrew/kalico.git ~/klipper
sudo systemctl restart klipper
```

### 选项 2. 使用 KIAUH

对于不熟悉直接使用 Git 的用户，[KIAUH v6](https://github.com/dw-0/kiauh) 能够使用自定义存储库。

为此，通过以下步骤将 Kalico 存储库添加到 KIAUH 的自定义存储库配置中：

1. 在 KIAUH 中设置 kalico 作为存储库
- `cd ~/kiauh`
- `cp default.kiauh.cfg kiauh.cfg`
- `nano kiauh.cfg`
- 为主分支添加 `https://github.com/KalicoCrew/kalico.git, main`

    或为 bleeding edge 分支添加 `https://github.com/KalicoCrew/kalico, bleeding-edge-v2`
- CTRL-X 保存并退出

2. 在 KIAUH 中选择 Kalico

从 KIAUH 菜单中选择：

-   [S] Settings
-   1\) Switch Klipper source repository

-   从列表中选择 Kalico

### 选项 3. 向现有安装添加 git 远程
可以随时通过 `git checkout upstream_main` 切换回主线 klipper

```bash
cd ~/klipper
git remote add kalico https://github.com/KalicoCrew/kalico.git
git checkout -b upstream-main origin/master
git branch -D master
git fetch kalico main
git checkout -b main kalico/main
sudo systemctl restart klipper
sudo systemctl restart moonraker
```

## Moonraker 更新配置

Kalico 以 `vYYYY.MM.NN` 格式创建月度发布标签（例如 `v2026.01.00`）。可以在跟踪最新提交或稳定月度发布之间选择。

在 `moonraker.conf` 中，在 `[update_manager klipper]` 部分中设置通道：

```ini
[update_manager klipper]
channel: dev
```

- **dev** - 跟踪主分支上的最新提交
- **stable** - 仅跟踪月度发布标签

同一个月内的热修复版本使用递增后缀（例如 `v2026.01.01`、`v2026.01.02`）。