# 联系方式

本文档提供 Kalico 的联系信息。
Kalico 是一个由社区维护的 Kalico 固件分支。

## Discord

Kalico 有一个专门的 Discord 服务器，你可以在那里与 Kalico 的开发者和用户实时聊天。

你可以在这里加入服务器：
[kalico.gg/discord](https://kalico.gg/discord)

## 我有关于 Kalico 的问题

我们收到的许多问题已经在[概述](Overview.md)中得到了解答。请务必阅读文档并按照其中提供的说明操作。

如果你有兴趣与其他 Kalico 用户分享你的知识和经验，你可以加入 Kalico [Discord 服务器](#discord)

如果你有一般性问题或遇到一般的打印问题，也可以考虑一般的 3d 打印论坛或专门讨论打印机硬件的论坛。

## 我有功能请求

所有新功能都需要有人感兴趣并能够实现该功能。如果你有兴趣帮助实现或测试新功能，你可以在 [GitHub issues](https://github.com/KalicoCrew/kalico/issues) 页面和 [pull requests](https://github.com/KalicoCrew/kalico/pulls) 页面上搜索正在进行的开发

协作者之间也在 Kalico [Discord 服务器](#discord)上进行讨论。

## 帮助！它不工作！

如果你遇到问题，我们建议你仔细阅读[概述](Overview.md)并仔细检查是否遵循了所有步骤。

如果你遇到打印问题，我们建议仔细检查打印机硬件（所有连接点、电线、螺丝等），并验证一切是否正常。我们发现大多数打印问题与 Kalico 软件无关。如果你确实发现了打印机硬件问题，可以考虑搜索一般的 3d 打印论坛或专门讨论打印机硬件的论坛。

## 我在 Kalico 软件中发现了错误

Kalico 是一个开源项目，我们感谢协作者诊断软件中的错误。

问题应在 [Discord 服务器](#discord)上报告

修复错误需要一些重要信息。请按照以下步骤操作：
1. 确保你运行的是来自 [https://github.com/KalicoCrew/kalico](https://github.com/KalicoCrew/kalico) 的未修改代码。如果代码已被修改或来自其他来源，你应在报告之前使用来自 [https://github.com/KalicoCrew/kalico](https://github.com/KalicoCrew/kalico) 的未修改代码重现问题。
2. 如果可能，在不良事件发生后立即运行 `M112` 命令。这将使 Kalico 进入"关闭状态"，并将导致额外的调试信息写入日志文件。
3. 从事件中获取 Kalico 日志文件。日志文件旨在回答 Kalico 开发者关于软件及其环境的常见问题（软件版本、硬件类型、配置、事件时间以及数百个其他问题）。
   1. 专用的 Kalico Web 界面能够直接获取 Kalico 日志文件。使用这些界面时，这是获取日志最简单的方式。否则，需要"scp"或"sftp"实用程序将日志文件复制到你的桌面计算机。"scp"实用程序在 Linux 和 MacOS 桌面中是标准的。其他桌面也有免费可用的 scp 实用程序（例如 WinSCP）。日志文件可能位于 `~/printer_data/logs/klippy.log` 文件中（如果使用图形化 scp 实用程序，请查找"printer_data"文件夹，然后查找其下的"logs"文件夹，然后是 `klippy.log` 文件）。日志文件也可能位于 `/tmp/klippy.log` 文件中（如果使用无法直接复制 `/tmp/klippy.log` 的图形化 scp 实用程序，请反复点击 `..` 或"父文件夹"直到到达根目录，点击 `tmp` 文件夹，然后选择 `klippy.log` 文件）。
   2. 将日志文件复制到桌面，以便可以将其附加到问题报告中。
   3. 不要以任何方式修改日志文件；不要提供日志片段。只有完整的未修改日志文件才能提供必要的信息。
   4. 建议使用 zip 或 gzip 压缩日志文件。
5. 在 [Discord 服务器](#discord)上开设新主题，并提供问题的清晰描述。其他 Kalico 贡献者需要了解采取了哪些步骤、预期的结果是什么以及实际发生了什么。压缩的 Kalico 日志文件应附加到该主题中。

## 我正在进行我想包含在 Kalico 中的更改

Kalico 是开源软件，我们感谢新的贡献。

有关信息，请参阅[贡献文档](CONTRIBUTING.md)。

有几份[开发者文档](Overview.md#developer-documentation)。如果你对代码有疑问，也可以在 [Discord 服务器](#discord)上提问。
