# 从 Klipper 迁移

> [!NOTE]
> 切换到 Kalico 后，你需要重新安装所有正在使用的附加模块。这包括 Beacon 支持、led-effect 等。
>
> ~/printer_data 中的所有数据（如打印机配置和宏）将不受影响，但仍建议进行备份。

### 选项 1. 手动克隆仓库

如果需要，可以通过运行以下命令备份现有的 Klipper 安装：

```bash
mv ~/klipper ~/klipper_old
```

然后克隆 Kalico 仓库并重启 klipper 服务：

```bash
git clone https://github.com/KalicoCrew/kalico.git ~/klipper
sudo systemctl restart klipper
```

### 选项 2. 使用 KIAUH

对于不习惯直接使用 Git 的用户，[KIAUH v6](https://github.com/dw-0/kiauh) 支持使用自定义仓库。

为此，请按以下步骤将 Kalico 仓库添加到 KIAUH 的自定义仓库配置中：

1. 在 KIAUH 中设置 kalico 作为仓库
- `cd ~/kiauh`
- `cp default.kiauh.cfg kiauh.cfg`
- `nano kiauh.cfg`
- 添加 `https://github.com/KalicoCrew/kalico, main` 用于主分支

    或 `https://github.com/KalicoCrew/kalico, bleeding-edge-v2` 用于前沿分支
- CTRL-X 保存并退出

2. 在 KIAUH 中选择 Kalico

从 KIAUH 菜单中选择：

-   [S] 设置
-   1\) 切换 Klipper 源代码仓库

-   从列表中选择 Kalico

### 选项 3. 向现有安装添加 git-remote
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

Kalico 以 `vYYYY.MM.NN` 格式（例如 `v2026.01.00`）创建每月发布标签。你可以选择跟踪最新的提交或稳定的每月发布。

在你的 `moonraker.conf` 中，设置 `[update_manager klipper]` 部分的 channel：

```ini
[update_manager klipper]
channel: dev
```

- **dev** - 跟踪主分支上的最新提交
- **stable** - 仅跟踪每月发布标签

同一个月内的热修复发布使用递增的后缀（例如 `v2026.01.01`、`v2026.01.02`）。
