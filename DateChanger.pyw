import datetime
import os
import sys
from pathlib import Path

import ctypes
from ctypes import wintypes

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDateTimeEdit,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
)
from win32_setctime import setctime

VERSION = "1.0"

BUTTON_CSS = """
QPushButton {
    border: 2px solid #555;
    border-radius: 8px;
    background: none;
    padding: 2px 10px;
}
QPushButton:hover {
    border-color: #0078d7;
}
"""

WM_SYSCOMMAND      = 0x0112
MF_STRING          = 0x0000
MF_BYCOMMAND       = 0x0000
MF_CHECKED         = 0x0008
MF_UNCHECKED       = 0x0000
SYSMENU_ID_TOPMOST = 0x8000


class FileLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            filepath = event.mimeData().urls()[0].toLocalFile()
            self.setText(filepath)
            self.editingFinished.emit()


class TimeCopyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.msg_timeout = 2000
        self._menu_added = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"DateChanger v{VERSION}")
        self.setFixedSize(535, 140)

        self.in_line = FileLineEdit()
        self.in_line.setPlaceholderText(" Drag and Drop file to copy date and time")
        self.in_line.setMinimumWidth(250)
        self.in_line.editingFinished.connect(self.update_times)

        self.out_line = FileLineEdit()
        self.out_line.setPlaceholderText(" Drag and Drop file to apply date and time")
        self.out_line.setMinimumWidth(250)

        self.create_label = QLabel("    Date Create File:")
        self.create_edit = QDateTimeEdit()
        self.create_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.create_edit.setCalendarPopup(True)

        self.modify_label = QLabel("    Date Modify File:")
        self.modify_edit = QDateTimeEdit()
        self.modify_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.modify_edit.setCalendarPopup(True)

        now = QDateTime.currentDateTime()
        self.create_edit.setDateTime(now)
        self.modify_edit.setDateTime(now)

        self.reset_create_btn = QPushButton("⭯")
        self.reset_create_btn.setFixedWidth(30)
        self.reset_create_btn.setToolTip("Reset creation date to current time")
        self.reset_create_btn.clicked.connect(
            lambda: self.create_edit.setDateTime(QDateTime.currentDateTime())
        )

        self.reset_modify_btn = QPushButton("⭯")
        self.reset_modify_btn.setFixedWidth(30)
        self.reset_modify_btn.setToolTip("Reset modification date to current time")
        self.reset_modify_btn.clicked.connect(
            lambda: self.modify_edit.setDateTime(QDateTime.currentDateTime())
        )

        self.load_out_btn = QPushButton("   Get Date →")
        self.load_out_btn.clicked.connect(self.load_out_time)
        self.load_out_btn.setStyleSheet(BUTTON_CSS)

        self.set_btn = QPushButton("Set Time ⏰")
        self.set_btn.clicked.connect(self.copy_time)
        self.set_btn.setStyleSheet(BUTTON_CSS)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_fields)
        self.clear_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #871719;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #c53227;
            }
            """
        )

        layout = QGridLayout()
        layout.addWidget(self.clear_btn, 0, 0)
        layout.addWidget(self.in_line, 0, 1, 1, 5)
        layout.addWidget(self.load_out_btn, 1, 0)
        layout.addWidget(self.out_line, 1, 1, 1, 5)

        layout.addWidget(self.create_label, 2, 0)
        layout.addWidget(self.reset_create_btn, 2, 1)
        layout.addWidget(self.create_edit, 2, 2, 1, 3)
        self.create_edit.setMaximumWidth(273)

        layout.addWidget(self.set_btn, 2, 5, 2, 1)

        layout.addWidget(self.modify_label, 3, 0)
        layout.addWidget(self.reset_modify_btn, 3, 1)
        layout.addWidget(self.modify_edit, 3, 2, 1, 3)
        self.modify_edit.setMaximumWidth(273)

        self.setLayout(layout)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._menu_added:
            self._add_always_on_top_menu()
            self._menu_added = True

    def _add_always_on_top_menu(self):
        hwnd = int(self.winId())
        hMenu = ctypes.windll.user32.GetSystemMenu(hwnd, False)
        ctypes.windll.user32.AppendMenuW(hMenu, MF_STRING, SYSMENU_ID_TOPMOST, "Always on top")

    def nativeEvent(self, eventType, message):
        msg = wintypes.MSG.from_address(message.__int__())
        if msg.message == WM_SYSCOMMAND and msg.wParam == SYSMENU_ID_TOPMOST:
            self._toggle_always_on_top()
            return True, 0
        return super().nativeEvent(eventType, message)

    def _toggle_always_on_top(self):
        is_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, not is_top)
        self.show()

        hwnd = int(self.winId())
        hMenu = ctypes.windll.user32.GetSystemMenu(hwnd, False)
        if not is_top:
            ctypes.windll.user32.CheckMenuItem(hMenu, SYSMENU_ID_TOPMOST, MF_BYCOMMAND | MF_CHECKED)
        else:
            ctypes.windll.user32.CheckMenuItem(hMenu, SYSMENU_ID_TOPMOST, MF_BYCOMMAND | MF_UNCHECKED)

    def show_message(self, icon, title, text):
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.show()
        QTimer.singleShot(self.msg_timeout, msg.close)

    def update_times(self):
        path = Path(self.in_line.text().strip())
        if path.exists():
            stat = path.stat()
            self.create_edit.setDateTime(
                QDateTime.fromSecsSinceEpoch(int(stat.st_ctime))
            )
            self.modify_edit.setDateTime(
                QDateTime.fromSecsSinceEpoch(int(stat.st_mtime))
            )

    def load_out_time(self):
        path = Path(self.out_line.text().strip())
        if not path.exists():
            self.show_message(QMessageBox.Warning, "Error", "File not specified or does not exist.")
            return

        stat = path.stat()
        self.create_edit.setDateTime(
            QDateTime.fromSecsSinceEpoch(int(stat.st_ctime))
        )
        self.modify_edit.setDateTime(
            QDateTime.fromSecsSinceEpoch(int(stat.st_mtime))
        )

    def copy_time(self):
        target = Path(self.out_line.text().strip())
        if not target.exists():
            self.show_message(QMessageBox.Warning, "Error", "File not specified or does not exist.")
            return

        new_ct = int(self.create_edit.dateTime().toSecsSinceEpoch())
        new_mt = int(self.modify_edit.dateTime().toSecsSinceEpoch())

        try:
            setctime(str(target), new_ct)
            os.utime(str(target), (new_mt, new_mt))
            self.show_message(QMessageBox.Information, "Success", "Timestamps changed successfully.")
        except Exception as e:
            self.show_message(QMessageBox.Critical, "Error", f"Could not change timestamps:\n{e}")

    def clear_fields(self):
        self.in_line.clear()
        self.out_line.clear()
        now = QDateTime.currentDateTime()
        self.create_edit.setDateTime(now)
        self.modify_edit.setDateTime(now)


if __name__ == "__main__":
    try:
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0
        )
    except Exception:
        pass

    app = QApplication(sys.argv)
    window = TimeCopyApp()
    window.show()
    sys.exit(app.exec_())
