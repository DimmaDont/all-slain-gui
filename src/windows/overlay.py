from __future__ import annotations

import logging
from collections import deque
from typing import TYPE_CHECKING

import win32con
import win32gui
from allslain.version import VersionCheckResult
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QLabel,
    QStyle,
    QVBoxLayout,
    QWidget,
)


if TYPE_CHECKING:
    from ..app import MainWindow


logger = logging.getLogger("all-slain-gui").getChild("overlay")


class Overlay(QWidget):
    def __init__(self, mw: MainWindow):
        super().__init__(mw)

        self.config_gui = mw.options.parent().app.config

        self.alignment = Qt.AlignmentFlag.AlignLeft
        if self.config_gui["main"]["overlay_position"] == "bottom":
            self.alignment |= Qt.AlignmentFlag.AlignBottom
        else:
            self.alignment |= Qt.AlignmentFlag.AlignTop
        self.set_screen()

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool  # Hide from taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.text = QLabel(self)
        if self.config_gui["main"]["overlay_position"] == "bottom":
            self.text.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
            )
        else:
            self.text.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
            )

        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(0)
        effect.setColor(QColor("#222222"))
        effect.setOffset(1, 1)
        self.text.setGraphicsEffect(effect)

        stylesheet = (
            "background-color: transparent;"
            "border: none;"
            "font-family: Cascadia Code;"
            "font-size: 12px;"
            "text-align: top;"
            # "padding-top: 0px;"
            "margin-left: 1px;"
        )
        # if __debug__:
        #     stylesheet += "background-color: blue;"
        self.text.setStyleSheet(stylesheet)
        self.lines = deque(
            [
                '<span style="color:white;">all-slain: Star Citizen Game Log Reader</span>',
                '<a style="color:#1050FF; text-decoration: none;" href="https://github.com/DimmaDont/all-slain-gui">https://github.com/DimmaDont/all-slain-gui</a>',
                "Waiting for Star Citizen to start...",
            ]
        )
        for _ in range(self.config_gui["main"]["line_count"] - len(self.lines)):
            self.lines.appendleft("")
        self.text.setText("<br>".join(self.lines))
        self.text.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )  # default
        self.text.setOpenExternalLinks(True)
        self.text.show()

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        win32gui.SetWindowLong(
            int(self.winId()),
            win32con.GWL_EXSTYLE,
            win32con.WS_EX_NOACTIVATE,
        )

    def update_text(self, text: str):
        self.lines.popleft()
        self.lines.append(text)
        self.text.setText("<br>".join(self.lines))

    def update_position(self, pos_name: str):
        logger.debug(f"overlay pos {pos_name}")
        self.alignment = Qt.AlignmentFlag.AlignLeft
        self.alignment |= (
            Qt.AlignmentFlag.AlignBottom
            if pos_name == "Bottom Left"
            else Qt.AlignmentFlag.AlignTop
        )
        self.text.setAlignment(self.alignment)
        self.set_screen()

    def set_screen(self, screen_name: str | None = None):
        screen_name = screen_name or self.config_gui["main"]["screen"]
        screen = next(
            (s for s in QApplication.screens() if s.name() == screen_name),
            QApplication.primaryScreen(),
        )
        if screen is None:
            raise RuntimeError()
        geometry = screen.geometry()
        qrect = QStyle.alignedRect(
            Qt.LayoutDirection.LeftToRight,
            self.alignment,
            QSize(int(geometry.width() * 0.66), 100),
            geometry,
        )
        self.setGeometry(qrect)
        if layout := self.layout():
            layout.setAlignment(self.alignment)

    def update_line_count(self, lines: int):
        while len(self.lines) > lines:
            self.lines.popleft()
        while len(self.lines) < lines:
            self.lines.appendleft("")
        self.text.setText("<br>".join(self.lines))

    def add_message_update_available(self, result: VersionCheckResult):
        if result.error is None:
            self.update_text(
                f'<span style="color: cyan">An update is available:</span> '
                f'<a style="color:#1050FF; text-decoration: none;" href="{result.url}">v{result.version}</a>'
            )
