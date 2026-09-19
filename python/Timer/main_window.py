from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QSpinBox,
    QRadioButton,
    QButtonGroup,
    QFrame,
    QApplication,
)
from gif_window import GifWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gif_path = ""
        self.running = False
        self.interval_timer = QTimer(self)
        self.interval_timer.setSingleShot(True)
        self.interval_timer.timeout.connect(self.show_gif)
        self.gif_window = GifWindow()
        self._build_ui()
        self._apply_style()
        self._update_state()

    def _build_ui(self):
        self.setWindowTitle("GIF Timer")
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.WindowType.Window)
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(36, 30, 36, 32)
        layout.setSpacing(16)

        title = QLabel("GIF Timer")
        title.setObjectName("title")
        subtitle = QLabel("让 GIF 在你需要的时候出现")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("gifCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(8)

        self.file_button = QPushButton("＋  选择 GIF")
        self.file_button.setObjectName("fileButton")
        self.file_button.setMinimumHeight(48)
        self.file_button.clicked.connect(self.select_gif)
        card_layout.addWidget(self.file_button)

        self.file_name = QLabel("尚未选择文件")
        self.file_name.setObjectName("fileName")
        self.file_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.file_name)
        layout.addWidget(card)

        layout.addWidget(self._section_label("间隔时间"))
        hint = QLabel("总间隔不能少于 4 秒")
        hint.setObjectName("hint")
        layout.addWidget(hint)
        interval_row = QHBoxLayout()
        interval_row.setSpacing(10)
        self.hour_spin = self._spin(0, 99, 0, " 小时")
        self.minute_spin = self._spin(0, 59, 0, " 分钟")
        self.second_spin = self._spin(0, 59, 0, " 秒")
        interval_row.addWidget(self.hour_spin)
        interval_row.addWidget(self.minute_spin)
        interval_row.addWidget(self.second_spin)
        layout.addLayout(interval_row)

        layout.addWidget(self._section_label("消失方式"))
        disappear_row = QHBoxLayout()
        disappear_row.setSpacing(12)
        self.auto_radio = QRadioButton("自动消失")
        self.click_radio = QRadioButton("点击消失")
        self.auto_radio.setChecked(True)
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.auto_radio)
        self.radio_group.addButton(self.click_radio)
        self.auto_radio.toggled.connect(self._update_state)
        disappear_row.addWidget(self.auto_radio)
        self.disappear_spin = self._spin(1, 16, 4, " 秒")
        self.disappear_spin.setFixedWidth(128)
        disappear_row.addWidget(self.disappear_spin)
        disappear_row.addStretch()
        disappear_row.addWidget(self.click_radio)
        layout.addLayout(disappear_row)

        layout.addStretch()

        self.status_label = QLabel("")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.start_button = QPushButton("开始")
        self.start_button.setObjectName("startButton")
        self.start_button.setMinimumHeight(48)
        self.start_button.clicked.connect(self.toggle_running)
        layout.addWidget(self.start_button)

    def _section_label(self, text):
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def _spin(self, minimum, maximum, value, suffix):
        box = QSpinBox()
        box.setRange(minimum, maximum)
        box.setValue(value)
        box.setSuffix(suffix)
        box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.setMinimumHeight(46)
        box.setKeyboardTracking(False)
        return box

    def select_gif(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 GIF", str(Path.home()), "GIF 图片 (*.gif)"
        )
        if not path:
            return
        self.gif_path = path
        self.file_name.setText(Path(path).name)
        self.file_button.setText("更换 GIF")
        self.gif_window.set_gif(path)

    def _interval_ms(self):
        total = (
            self.hour_spin.value() * 3600
            + self.minute_spin.value() * 60
            + self.second_spin.value()
        )
        return total * 1000

    def toggle_running(self):
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if not self.gif_path:
            self.status_label.setText("请先选择一个 GIF")
            return
        if self._interval_ms() < 4000:
            self.status_label.setText("间隔时间不能少于 4 秒")
            return
        self.running = True
        self.status_label.setText("正在运行")
        self.interval_timer.start(self._interval_ms())
        self._update_state()
        self.showMinimized()

    def stop_timer(self):
        self.running = False
        self.interval_timer.stop()
        self.gif_window.hide()
        self.status_label.setText("")
        self._update_state()

    def show_gif(self):
        if not self.running:
            return
        self.gif_window.show_centered(
            auto_hide=self.auto_radio.isChecked(),
            duration_seconds=self.disappear_spin.value(),
        )
        self.interval_timer.start(self._interval_ms())

    def show_main_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        if self.running:
            self.showMinimized()
            event.ignore()
        else:
            self.quit_app()
            event.accept()

    def quit_app(self):
        self.interval_timer.stop()
        self.gif_window.close()
        QApplication.quit()

    def _update_state(self):
        running = self.running
        for widget in [
            self.file_button,
            self.hour_spin,
            self.minute_spin,
            self.second_spin,
            self.auto_radio,
            self.click_radio,
        ]:
            widget.setEnabled(not running)
        self.disappear_spin.setEnabled(not running and self.auto_radio.isChecked())
        self.start_button.setText("停止" if running else "开始")
        self.start_button.setProperty("running", running)
        self.start_button.style().unpolish(self.start_button)
        self.start_button.style().polish(self.start_button)

    def _apply_style(self):
        self.setStyleSheet("""
        QWidget#root {
            background: #f5f5f7;
            color: #1d1d1f;
            font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
            font-size: 14px;
        }
        QLabel#title {
            color: #1d1d1f;
            font-size: 30px;
            font-weight: 700;
        }
        QLabel#subtitle, QLabel#hint, QLabel#fileName {
            color: #86868b;
            font-size: 13px;
        }
        QLabel#sectionTitle {
            color: #1d1d1f;
            font-size: 15px;
            font-weight: 600;
        }
        QFrame#gifCard {
            background: #ffffff;
            border: 1px solid #e5e5ea;
            border-radius: 18px;
        }
        QPushButton#fileButton {
            background: #f5f5f7;
            border: 1px solid #e5e5ea;
            border-radius: 14px;
            color: #007aff;
            font-size: 15px;
            font-weight: 600;
        }
        QPushButton#fileButton:hover { background: #eeeeF0; }
        QSpinBox {
            color: #1d1d1f;
            background: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 12px;
            padding: 0 12px;
            font-size: 16px;
        }
        QSpinBox:focus {
            border: 2px solid #007aff;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            width: 0px;
            border: none;
        }
        QRadioButton {
            color: #1d1d1f;
            spacing: 7px;
        }
        QLabel#status {
            color: #86868b;
            min-height: 20px;
        }
        QPushButton#startButton {
            background: #007aff;
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 16px;
            font-weight: 600;
        }
        QPushButton#startButton:hover { background: #0a84ff; }
        QPushButton#startButton[running="true"] { background: #ff3b30; }
        """)
