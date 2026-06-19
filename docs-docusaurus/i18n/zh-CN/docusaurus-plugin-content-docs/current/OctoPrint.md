# 使用 OctoPrint

Kalico 有几个前端选项，OctoPrint 是 Kalico 最初的和原始的前端。本文档将简要概述使用此选项进行安装的过程。

## 使用 OctoPi 安装

首先在 Raspberry Pi 计算机上安装 [OctoPi](https://github.com/guysoft/OctoPi)。使用 OctoPi v0.17.0 或更高版本 - 有关发布信息，请参阅 [OctoPi 发布版本](https://github.com/guysoft/OctoPi/releases)。

应验证 OctoPi 能正常启动且 OctoPrint Web 服务器能正常工作。连接到 OctoPrint 网页后，按照提示升级 OctoPrint（如果需要）。

安装 OctoPi 并升级 OctoPrint 后，需要通过 ssh 登录目标机器来运行一些系统命令。

首先在主机设备上运行这些命令：

__如果你没有安装 git，请使用以下命令安装：__
```
sudo apt install git
```
然后继续：
```
cd ~
git clone https://github.com/KalicoCrew/kalico klipper
./klipper/scripts/install-octopi.sh
```

上述操作将下载 Kalico，安装所需的系统依赖项，设置 Kalico 在系统启动时运行，并启动 Kalico 主机软件。它需要互联网连接，可能需要几分钟才能完成。

## 使用 KIAUH 安装

KIAUH 可用于在各种运行 Debian 系列的 Linux 系统上安装 OctoPrint。更多信息可以在 https://github.com/dw-0/kiauh 找到。

## 配置 OctoPrint 以使用 Kalico

OctoPrint Web 服务器需要配置为与 Kalico 主机软件通信。使用 Web 浏览器登录 OctoPrint 网页，然后配置以下项目：

导航到设置选项卡（页面顶部的扳手图标）。在"串口连接"下的"附加串口"中添加：

```
~/printer_data/comms/klippy.serial
```

然后点击"保存"。

_在一些较旧的设置中，此地址可能是 `/tmp/printer`，根据你的设置，你可能也需要保留此行_

再次进入设置选项卡，在"串口连接"下将"串口"设置更改为上面添加的串口。

在设置选项卡中，导航到"行为"子选项卡，选择"取消任何正在进行的打印但保持与打印机的连接"选项。点击"保存"。

从主页面，在"连接"部分（页面左上方），确保"串口"设置为新添加的附加串口，然后点击"连接"。（如果它不在可用选项中，请尝试重新加载页面。）

连接后，导航到"终端"选项卡，在命令输入框中输入 "status"（不带引号），然后点击"发送"。终端窗口可能会报告打开配置文件时出错 - 这意味着 OctoPrint 已成功与 Kalico 通信。

请继续阅读 [Installation.md](Installation.md) 中的_构建和刷写微控制器_部分。
