# 使用 OctoPrint

Kalico 有几个前端选项，OctoPrint 是 Kalico 的第一个和原始前端。本文档将简要介绍使用此选项进行安装。

## 使用 OctoPi 安装

首先在树莓派计算机上安装 [OctoPi](https://github.com/guysoft/OctoPi)。使用 OctoPi v0.17.0 或更高版本——查看 [OctoPi 发布](https://github.com/guysoft/OctoPi/releases) 了解发布信息。

应验证 OctoPi 启动并且 OctoPrint 网络服务器正常工作。连接到 OctoPrint 网页后，按照提示升级 OctoPrint（如需要）。

安装 OctoPi 并升级 OctoPrint 后，需要 SSH 连接到目标机器运行一些系统命令。

首先在主机设备上运行这些命令：

__如果未安装 git，请使用以下方式安装：__
```
sudo apt install git
```
然后继续：
```
cd ~
git clone https://github.com/KalicoCrew/kalico klipper
./klipper/scripts/install-octopi.sh
```

上述命令将下载 Kalico、安装所需的系统依赖项、设置 Kalico 以在系统启动时运行，并启动 Kalico 主机软件。它将需要互联网连接，可能需要几分钟才能完成。

## 使用 KIAUH 安装

KIAUH 可用于在运行 Debian 形式的各种基于 Linux 的系统上安装 OctoPrint。更多信息可以在 https://github.com/dw-0/kiauh 找到

## 配置 OctoPrint 使用 Kalico

OctoPrint 网络服务器需要配置为与 Kalico 主机软件通信。使用网络浏览器登录 OctoPrint 网页，然后配置以下项：

导航到设置选项卡（页面顶部的扳手图标）。在"串行连接"中的"其他串行端口"下添加：

```
~/printer_data/comms/klippy.serial
```

然后点击"保存"。

_在某些较旧的设置中，此地址可能是 `/tmp/printer`，取决于设置，可能需要保留此行_

再次进入设置选项卡，在"串行连接"下更改"串行端口"设置为上面添加的端口。

在设置选项卡中，导航到"行为"子选项卡并选择"取消任何正在进行的打印但保持连接到打印机"选项。点击"保存"。

从主页，在页面左上角的"连接"部分下，确保"串行端口"设置为添加的新端口并点击"连接"。（如果未在可用选择中，请尝试重新加载页面。）

连接后，导航到"终端"选项卡并在命令输入框中输入"status"（不含引号）并点击"发送"。终端窗口可能会报告打开配置文件时出现错误——这意味着 OctoPrint 正在成功与 Kalico 通信。

请继续进行 [Installation.md](Installation.md) 并查看_构建和闪烁微控制器_部分