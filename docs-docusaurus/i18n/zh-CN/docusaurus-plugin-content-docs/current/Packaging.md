# 打包 Kalico

Kalico 在 Python 程序中算是一个打包方面的特例，因为它不使用 setuptools 来构建和安装。以下是一些关于如何最好地打包它的说明：

## C 模块

Kalico 使用 C 模块来更快速地处理一些运动学计算。此模块需要在打包时编译，以避免引入对编译器的运行时依赖。要编译 C 模块，请运行 `python3 klippy/chelper/__init__.py`。

## 编译 Python 代码

许多发行版有一项策略，即在打包前编译所有 Python 代码以提高启动时间。你可以通过运行 `python3 -m compileall klippy` 来完成此操作。

## 版本管理

如果你正在从 git 构建 Kalico 的软件包，通常的做法是不包含 .git 目录，因此必须在不使用 git 的情况下处理版本号。为此，请使用 `scripts/make_version.py` 中附带的脚本，运行方式如下：`python3 scripts/make_version.py YOURDISTRONAME > klippy/.version`。

## 打包脚本示例

klipper-git 是为 Arch Linux 打包的，其 PKGBUILD（软件包构建脚本）可在 [Arch 用户仓库](https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=klipper-git)中找到。
