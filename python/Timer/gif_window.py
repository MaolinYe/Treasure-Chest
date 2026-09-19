from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QGraphicsOpacityEffect

class GifWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.movie = None
        self.gif_path = ""
        self.auto_hide = True
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        self.fade_timer = QTimer(self)
        self.fade_timer.setInterval(30)
        self.fade_timer.timeout.connect(self._fade_step)
        self.fade_out = False
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide_with_fade)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.hide()

    def set_gif(self, path):
        self.gif_path = path
        if self.movie:
            self.movie.stop()
            self.movie.deleteLater()
        self.movie = QMovie(path)
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.movie.frameChanged.connect(self._frame_changed)
        self.label.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()
        self._frame_changed()

    def _frame_changed(self):
        if not self.movie:
            return
        pixmap = self.movie.currentPixmap()
        if pixmap.isNull():
            return
        max_w, max_h = self._max_size()
        scaled = pixmap.scaled(
            max_w, max_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label.setFixedSize(scaled.size())
        self.resize(scaled.size())

    def _max_size(self):
        screen = QApplication.primaryScreen()
        area = screen.availableGeometry()
        return int(area.width() * 0.5), int(area.height() * 0.5)

    def show_centered(self, auto_hide=True, duration_seconds=5):
        if not self.movie and self.gif_path:
            self.set_gif(self.gif_path)
        if not self.movie:
            return

        self.auto_hide = auto_hide
        self.auto_hide_timer.stop()
        self._frame_changed()
        area = QApplication.primaryScreen().availableGeometry()
        self.move(
            area.x() + (area.width() - self.width()) // 2,
            area.y() + (area.height() - self.height()) // 2
        )
        self.fade_timer.stop()
        self.fade_out = False
        self.opacity_effect.setOpacity(0.0)
        self.show()
        self.raise_()
        self.movie.start()
        self.fade_timer.start()
        if auto_hide:
            self.auto_hide_timer.start(max(1, duration_seconds) * 1000)

    def _fade_step(self):
        value = self.opacity_effect.opacity()
        if self.fade_out:
            value -= 0.12
            if value <= 0:
                self.opacity_effect.setOpacity(0.0)
                self.fade_timer.stop()
                self.hide()
                if self.movie:
                    self.movie.stop()
                return
        else:
            value += 0.16
            if value >= 1:
                value = 1.0
                self.fade_timer.stop()
        self.opacity_effect.setOpacity(value)

    def hide_with_fade(self):
        if self.isVisible():
            self.auto_hide_timer.stop()
            self.fade_out = True
            self.fade_timer.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide_with_fade()
        else:
            super().mousePressEvent(event)
