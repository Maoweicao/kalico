# 打包Kalico

Kalico在python程序中有些异常，因为它不使用setuptools进行构建和安装。以下是关于如何最好地打包它的一些注意事项：

## C模块

Kalico使用C模块来更快地处理一些运动学计算。需要在打包时编译此模块，以避免在运行时引入编译器依赖项。要编译C模块，运行`python3 klippy/chelper/__init__.py`。

## 编译python代码

许多发行版都有一项政策，在打包前编译所有python代码以改进启动时间。您可以通过运行`python3 -m compileall klippy`来执行此操作。

## 版本控制

如果您从git构建Kalico包，通常不会提供.git目录，因此版本控制必须在没有git的情况下处理。要执行此操作，请使用`scripts/make_version.py`中提供的脚本，应按如下方式运行：`python3 scripts/make_version.py YOURDISTRONAME > klippy/.version`。

## 示例打包脚本

klipper-git是为Arch Linux打包的，在[Arch用户存储库](https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=klipper-git)中有一个PKGBUILD（包构建脚本）可用。