from PySide6.QtWidgets import (
    QPushButton, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QWidget, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QPixmap, QFont, QPainter, QPen, QColor
import os, base64

from .theme import Colors


class SidebarButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setObjectName("sidebarButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(34)
        if icon_path:
            if icon_path.startswith("data:image"):
                b64 = icon_path.split(",", 1)[1]
                pix = QPixmap()
                pix.loadFromData(base64.b64decode(b64))
                self.setIcon(QIcon(pix))
            elif os.path.exists(icon_path):
                self.setIcon(QIcon(icon_path))
            self.setIconSize(self.iconSize())


class Card(QFrame):
    def __init__(self, parent=None, no_padding=False):
        super().__init__(parent)
        self.setObjectName("cardNoPadding" if no_padding else "card")
        self._layout = QVBoxLayout(self)
        if no_padding:
            self._layout.setContentsMargins(0, 0, 0, 0)
            self._layout.setSpacing(0)
        else:
            self._layout.setContentsMargins(12, 10, 12, 10)
            self._layout.setSpacing(6)

    def layout(self):
        return self._layout

    def add_widget(self, widget):
        self._layout.addWidget(widget)

    def add_layout(self, layout):
        self._layout.addLayout(layout)


class StatCard(QFrame):
    def __init__(self, title, value="0", color="#569cd6", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        self.value_label.setStyleSheet(f"color: {color}; background: transparent;")
        f = self.value_label.font()
        f.setPointSize(20)
        f.setBold(True)
        self.value_label.setFont(f)
        title_label = QLabel(title)
        title_label.setObjectName("statLabel")
        title_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self.setMinimumSize(140, 70)

    def set_value(self, value):
        self.value_label.setText(str(value))


class Toast(QFrame):
    def __init__(self, parent, message, type_="info", duration=4000):
        super().__init__(parent)
        self.duration = duration
        colors = {"success": "#6a9955", "error": "#f44747", "warning": "#dcdcaa", "info": "#569cd6"}
        c = colors.get(type_, "#569cd6")
        self.setStyleSheet(f"""
            background-color: #2d2d2d;
            border: 1px solid {c};
            border-left: 3px solid {c};
            padding: 8px 12px;
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        indicator = QFrame()
        indicator.setFixedSize(6, 6)
        indicator.setStyleSheet(f"background-color: {c};")
        layout.addWidget(indicator)
        msg = QLabel(message)
        msg.setStyleSheet("color: #d4d4d4; font-size: 12px; background: transparent;")
        msg.setWordWrap(True)
        layout.addWidget(msg, 1)
        self.adjustSize()
        QTimer.singleShot(self.duration, self._fade_out)

    def _fade_out(self):
        a = QPropertyAnimation(self, b"windowOpacity")
        a.setDuration(200)
        a.setStartValue(1.0)
        a.setEndValue(0.0)
        a.finished.connect(self.deleteLater)
        a.start()


class ScanOutputWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardNoPadding")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet("background-color: #252526; border-bottom: 1px solid #333;")
        header.setFixedHeight(30)
        h = QHBoxLayout(header)
        h.setContentsMargins(10, 0, 8, 0)

        indent = QFrame()
        indent.setFixedSize(3, 12)
        indent.setStyleSheet("background-color: #569cd6;")
        h.addWidget(indent)
        h.addSpacing(6)

        t = QLabel("# output")
        t.setStyleSheet("color: #858585; font-size: 11px; background: transparent; font-family: 'Cascadia Code', 'Consolas', monospace;")
        h.addWidget(t)
        h.addStretch()

        cls = QPushButton("x")
        cls.setFixedSize(18, 18)
        cls.setStyleSheet("""
            QPushButton { background: transparent; color: #555; border: none; font-size: 11px; }
            QPushButton:hover { color: #d4d4d4; background: #333; }
        """)
        cls.setCursor(Qt.CursorShape.PointingHandCursor)
        cls.clicked.connect(self.clear_output)
        h.addWidget(cls)

        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")

        self.output = QLabel()
        self.output.setWordWrap(True)
        self.output.setTextFormat(Qt.TextFormat.RichText)
        self.output.setStyleSheet("""
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 8px 12px;
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 12px;
            border: none;
        """)
        self.output.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.output.setMinimumHeight(150)

        scroll.setWidget(self.output)
        scroll.setMinimumHeight(150)
        layout.addWidget(scroll, 1)

    def append(self, text, style=""):
        c = self.output.text()
        n = f'<span style="{style}">{text}</span>' if style else text
        self.output.setText((c + "<br>" + n) if c else n)

    def append_found(self, text):
        self.append(text, "color: #f44747;")

    def append_warning(self, text):
        self.append(text, "color: #dcdcaa;")

    def append_info(self, text):
        self.append(text, "color: #858585;")

    def append_success(self, text):
        self.append(text, "color: #6a9955;")

    def append_divider(self):
        self.append("\u2500" * 50, "color: #333;")

    def clear_output(self):
        self.output.clear()
