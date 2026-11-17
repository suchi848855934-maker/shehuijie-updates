# 社会姐桌面宠物更新仓库

仅用于社会姐程序发行和更新，不包含猫咪照片、个人资料或运行日志。独立于原私有仓库。

## 安装

在 [Releases](https://github.com/suchi848855934-maker/shehuijie-updates/releases) 下载 `shehuijie.zip`，解压到有写入权限的文件夹，双击 `启动社会姐.bat`。需要安装包含 Tkinter 和 Python Launcher 的 Python 3.13。本包不包含 Python。

V1.0.4 没有自动更新能力，首次需要使用本发行包启动。后续启动会后台检查并下载新版，展示说明，由用户确认安装。

## 更新安全和恢复

下载及安装前校验 SHA-256，只允许发行文件清单中的文件。独立进程等待宠物退出后备份和安装；新版窗口发出健康信号后完成安装，启动失败恢复旧文件。SHA-256 保证完整性，不代替更新账户的安全保护。

日志和备份仅保存在本机 `%LOCALAPPDATA%\SheHuiJie`。断电或强制结束安装器不保证自动恢复，可以从该目录的最新 `backup-*` 文件夹复制文件回安装目录。

## 发行流程

Windows/Python 3.13 检查通过后，自动生成白名单 ZIP 和校验值，先发布 Release，再更新 `latest.json`。后续版本须修改 `release/version.json`；同一版本不会覆盖已发布附件。

本地已完成更新模块的模拟故障测试。GitHub Windows 验证不等于 Windows 10 实机完整更新测试。
