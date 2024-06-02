---
title: 命令行手册
---
本页介绍工具支持的所有命令及选项。

TataruBook命令行有[两种用法]({{ site.baseurl }}/index.html#如何下载和安装tatarubook)，为了简便起见，本页都以可执行文件用法为示例。如果采用的是Python脚本用法，则需要将所有命令开头从`tatarubook`换成`python tatarubook.py`。比如，创建一个名为`example.db`的数据库文件，需要将`tatarubook init example.db`命令改为`python tatarubook.py init example.db`。

# 通用注意事项

下面介绍一些和多个命令都有关的事项：

## 字符编码格式

默认设置下，TataruBook使用操作系统默认字符编码格式读写文件。但是注意非英文Windows操作系统的默认字符编码格式不是UTF-8，因此在Windows下读取UTF-8格式的csv文件时，TataruBook可能会遇到解码错误。为了解决这个问题，TataruBook在用其他格式解码失败时，会再尝试使用UTF-8解码一次。

如果想要TataruBook使用其他的字符编码格式读写文件，可以在相关命令中使用`--encoding`选项指定字符编码格式。

## 根据名字查找索引

