from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt


class Colors:
    BG_DARK        = "#1e1e1e"
    BG_MEDIUM      = "#252526"
    BG_CARD        = "#2d2d2d"
    BG_INPUT       = "#1e1e1e"
    BG_HOVER       = "#333333"
    SIDEBAR        = "#1e1e1e"
    SIDEBAR_HOVER  = "#2d2d2d"
    SIDEBAR_ACTIVE = "#37373d"

    ACCENT_PRIMARY   = "#569cd6"
    ACCENT_SECONDARY = "#c586c0"
    ACCENT_SUCCESS   = "#6a9955"
    ACCENT_WARNING   = "#dcdcaa"
    ACCENT_DANGER    = "#f44747"
    ACCENT_INFO      = "#4fc1ff"

    TEXT_PRIMARY   = "#d4d4d4"
    TEXT_SECONDARY = "#858585"
    TEXT_MUTED     = "#555555"

    BORDER       = "#333333"
    BORDER_LIGHT = "#2a2a2a"


def load_style():
    return f"""
    QWidget {{
        background-color: {Colors.BG_DARK};
        color: {Colors.TEXT_PRIMARY};
        font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
        font-size: 12px;
    }}

    QMainWindow {{ background-color: {Colors.BG_DARK}; }}

    QScrollBar:vertical {{
        background: {Colors.BG_MEDIUM}; width: 10px; margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {Colors.BORDER}; min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: #555; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

    QScrollBar:horizontal {{
        background: {Colors.BG_MEDIUM}; height: 10px; margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: {Colors.BORDER}; min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{ background: #555; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

    QPushButton {{
        background-color: {Colors.BG_CARD};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 6px 14px;
        font-family: 'Cascadia Code', 'Consolas', monospace;
        font-size: 12px;
    }}
    QPushButton:hover {{
        background-color: {Colors.BG_HOVER};
        border-color: #555;
    }}
    QPushButton:pressed {{
        background-color: #444;
    }}
    QPushButton:disabled {{
        color: {Colors.TEXT_MUTED};
    }}

    QPushButton#primaryButton {{
        background-color: #094771;
        color: #fff;
        border: 1px solid #094771;
        font-weight: bold;
    }}
    QPushButton#primaryButton:hover {{
        background-color: #0b5b8f;
    }}

    QPushButton#successButton {{
        background-color: {Colors.ACCENT_SUCCESS};
        color: #fff;
        border: 1px solid {Colors.ACCENT_SUCCESS};
    }}
    QPushButton#successButton:hover {{
        background-color: #5a8548;
    }}

    QPushButton#dangerButton {{
        background-color: #5a1d1d;
        color: #f48771;
        border: 1px solid #5a1d1d;
    }}
    QPushButton#dangerButton:hover {{
        background-color: #6d2424;
    }}

    QPushButton#sidebarButton {{
        background-color: transparent;
        color: {Colors.TEXT_SECONDARY};
        border: none;
        padding: 7px 12px;
        text-align: left;
        font-size: 12px;
    }}
    QPushButton#sidebarButton:hover {{
        background-color: {Colors.SIDEBAR_HOVER};
        color: {Colors.TEXT_PRIMARY};
    }}
    QPushButton#sidebarButton:checked {{
        background-color: {Colors.SIDEBAR_ACTIVE};
        color: #fff;
        border-left: 3px solid {Colors.ACCENT_PRIMARY};
    }}

    QPushButton#forensicButton {{
        background-color: {Colors.BG_CARD};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 6px 12px;
        font-size: 12px;
    }}
    QPushButton#forensicButton:hover {{
        background-color: {Colors.BG_HOVER};
        border-color: {Colors.ACCENT_PRIMARY};
    }}

    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 7px 10px;
        font-family: 'Cascadia Code', 'Consolas', monospace;
        font-size: 12px;
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {Colors.ACCENT_PRIMARY};
    }}

    QComboBox {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 7px 10px;
        font-size: 12px;
    }}
    QComboBox:hover {{ border-color: #555; }}
    QComboBox::drop-down {{ border: none; padding-right: 6px; }}
    QComboBox QAbstractItemView {{
        background-color: {Colors.BG_CARD};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        selection-background-color: {Colors.SIDEBAR_ACTIVE};
    }}

    QLabel {{ color: {Colors.TEXT_PRIMARY}; background: transparent; }}

    QLabel#sectionTitle {{
        font-size: 13px;
        font-weight: bold;
        color: {Colors.TEXT_PRIMARY};
        padding-bottom: 2px;
    }}

    QLabel#cardTitle {{
        font-size: 12px;
        font-weight: bold;
        color: {Colors.ACCENT_PRIMARY};
    }}

    QLabel#statValue {{
        font-size: 22px;
        font-weight: bold;
        color: {Colors.TEXT_PRIMARY};
    }}

    QLabel#statLabel {{
        font-size: 11px;
        color: {Colors.TEXT_SECONDARY};
    }}

    QFrame#card {{
        background-color: {Colors.BG_CARD};
        border: 1px solid {Colors.BORDER};
        padding: 12px;
    }}

    QFrame#cardNoPadding {{
        background-color: {Colors.BG_CARD};
        border: 1px solid {Colors.BORDER};
    }}

    QFrame#sidebar {{
        background-color: {Colors.SIDEBAR};
        border-right: 1px solid {Colors.BORDER};
    }}

    QFrame#contentArea {{
        background-color: {Colors.BG_DARK};
    }}

    QTreeWidget, QTableWidget {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        alternate-background-color: {Colors.BG_MEDIUM};
        selection-background-color: {Colors.SIDEBAR_ACTIVE};
        font-size: 12px;
    }}
    QTreeWidget::item, QTableWidget::item {{
        padding: 4px 6px;
        border-bottom: 1px solid {Colors.BORDER_LIGHT};
    }}
    QTreeWidget::item:hover, QTableWidget::item:hover {{
        background-color: {Colors.BG_HOVER};
    }}

    QHeaderView::section {{
        background-color: {Colors.BG_MEDIUM};
        color: {Colors.TEXT_SECONDARY};
        border: none;
        border-bottom: 1px solid {Colors.BORDER};
        padding: 5px 8px;
        font-weight: bold;
        font-size: 11px;
    }}

    QProgressBar {{
        background-color: {Colors.BG_MEDIUM};
        border: 1px solid {Colors.BORDER};
        height: 14px;
        text-align: center;
        font-size: 10px;
    }}
    QProgressBar::chunk {{
        background-color: #094771;
    }}

    QTabWidget::pane {{
        background-color: {Colors.BG_DARK};
        border: 1px solid {Colors.BORDER};
        border-top: none;
    }}
    QTabBar::tab {{
        background-color: {Colors.BG_MEDIUM};
        color: {Colors.TEXT_SECONDARY};
        border: 1px solid {Colors.BORDER};
        border-bottom: none;
        padding: 7px 16px;
        margin-right: 2px;
        font-size: 12px;
    }}
    QTabBar::tab:selected {{
        background-color: {Colors.BG_DARK};
        color: #fff;
    }}
    QTabBar::tab:hover {{
        color: {Colors.TEXT_PRIMARY};
    }}

    QSplitter::handle {{
        background-color: {Colors.BORDER};
    }}

    QToolTip {{
        background-color: {Colors.BG_CARD};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 4px 8px;
        font-size: 11px;
    }}

    QListView {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
    }}
    QListView::item {{ padding: 4px 8px; }}
    QListView::item:hover {{ background-color: {Colors.BG_HOVER}; }}
    QListView::item:selected {{ background-color: {Colors.SIDEBAR_ACTIVE}; }}
    """


def setup_fonts(app):
    font = QFont("Consolas", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
