# GIF Timer

Python + PySide6 实现的简洁 GIF 间隔提醒器。

## 功能

- 本地选择 GIF
- 小时 / 分钟 / 秒间隔
- 最短间隔 4 秒
- 自动消失 1～16 秒
- 点击 GIF 消失
- 屏幕中央显示
- 淡入淡出
- 系统托盘后台运行
- 运行时打开主窗口，按钮变成“停止”
- 运行时设置锁定

## 安装

```bash
pip install -r requirements.txt
python main.py
```

建议 Python 3.11+。

## Windows打包

```shell
pyinstaller --noconfirm --clean --windowed --onefile --name "GIF Timer" --icon "assets/icon.ico" main.py
```
