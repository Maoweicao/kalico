# 联系方式

本文档提供了 Kalico 的联系信息。
Kalico 是 Kalico 固件社区维护的分支。

## Discord

Kalico 有一个专用 Discord 服务器，您可以在其中与 Kalico 的开发者和用户实时聊天。

您可以在此处加入服务器：
[kalico.gg/discord](https://kalico.gg/discord)

## 我对 Kalico 有疑问

我们收到的许多问题已在 [概述](Overview.md) 中得到解答。
请务必阅读文档并按照那里提供的指示进行操作。

如果您有兴趣与其他 Kalico 用户分享您的知识和经验，
可以加入 Kalico [Discord 服务器](#discord)

如果您有一般问题或遇到一般打印问题，
也可以考虑使用一般 3D 打印论坛或专门针对打印机硬件的论坛。

## 我有功能请求

所有新功能都需要有人有兴趣和能力实现该功能。
如果您有兴趣帮助实现或测试新功能，可以在
[GitHub issues](https://github.com/KalicoCrew/kalico/issues) 页面和
[pull requests](https://github.com/KalicoCrew/kalico/pulls) 页面上搜索正在进行的开发

协作者之间也在 Kalico [Discord 服务器](#discord) 上进行讨论。

## 帮助！不起作用！

如果遇到问题，建议您仔细阅读 [概述](Overview.md)
并双重检查所有步骤是否已按照进行。

如果您遇到打印问题，建议您仔细检查打印机硬件
（所有连接、电线、螺钉等）并验证没有异常。
我们发现大多数打印问题与 Kalico 软件无关。
如果发现打印机硬件问题，请考虑搜索一般 3D 打印论坛
或针对打印机硬件的论坛。

## 我在 Kalico 软件中发现了错误

Kalico 是一个开源项目，我们感谢协作者诊断软件中的错误。

问题应在 [Discord 服务器](#discord) 上报告

为了修复错误，需要重要信息。请按照以下步骤操作：
1. 确保您运行的是来自
   [https://github.com/KalicoCrew/kalico](https://github.com/KalicoCrew/kalico)
   的未修改代码。如果代码已修改或从其他来源获得，
   则应在来自 [https://github.com/KalicoCrew/kalico](https://github.com/KalicoCrew/kalico)
   的未修改代码上重现问题后再进行报告。
2. 如果可能，在发生不良事件后立即运行 `M112` 命令。
   这会导致 Kalico 进入"关闭状态"，它会导致额外的调试信息
   被写入日志文件。
3. 从事件中获取 Kalico 日志文件。日志文件已设计为回答
   Kalico 开发人员有关软件及其环境的常见问题
   （软件版本、硬件类型、配置、事件时序和数百个其他问题）。
   1. 专用 Kalico Web 接口可以直接获取 Kalico 日志文件。
      这是使用这些接口之一时获取日志的最简单方法。
      否则，需要"scp"或"sftp"实用程序将日志文件复制到桌面计算机。
      "scp"实用程序随 Linux 和 MacOS 桌面一起提供。
      还有其他桌面免费提供的 scp 实用程序（例如 WinSCP）。
      日志文件可能位于 `~/printer_data/logs/klippy.log` 文件中
      （如果使用图形 scp 实用程序，请查找"printer_data"文件夹，
      然后查找其下的"logs"文件夹，然后查找 `klippy.log` 文件）。
      日志文件也可能位于 `/tmp/klippy.log` 文件中
      （如果使用无法直接复制 `/tmp/klippy.log` 的图形 scp 实用程序，
      则重复单击 `..` 或"parent folder"直到到达根目录，
      单击 `tmp` 文件夹，然后选择 `klippy.log` 文件）。
   2. 将日志文件复制到桌面以便可以将其附加到问题报告。
   3. 不要以任何方式修改日志文件；不要提供日志的片段。
      只有完整的未修改日志文件提供必要的信息。
   4. 最好用 zip 或 gzip 压缩日志文件。
5. 在 [Discord 服务器](#discord) 上打开新线程并清楚地描述问题。
   其他 Kalico 贡献者需要了解采取了哪些步骤、期望的结果是什么以及
   实际发生的结果是什么。压缩的 Kalico 日志文件应附加到该主题。

## 我正在进行我想包含在 Kalico 中的更改

Kalico 是开源软件，我们感谢新贡献。

有关信息，请参阅 [CONTRIBUTING 文档](CONTRIBUTING.md)。

有多个 [开发人员文档](Overview.md#developer-documentation)。
如果您对代码有疑问，也可以在 [Discord 服务器](#discord) 上提问