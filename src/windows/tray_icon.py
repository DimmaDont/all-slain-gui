from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

from allslain.version import VersionCheckResult
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtWidgets import QLabel, QMenu, QSystemTrayIcon, QWidgetAction

from ..functions import get_icon


if TYPE_CHECKING:
    from .main import MainWindow


logger = logging.getLogger("all-slain-gui").getChild("main")


class TrayIcon(QSystemTrayIcon):
    parent: Callable[[], MainWindow]

    def __init__(self, parent: MainWindow):
        super().__init__(parent)

        self.menu = QMenu()
        self.menu.setStyleSheet("border-radius: 5px")

        self.action_update = QWidgetAction(self.menu)
        label = QLabel("Update!")  # Emojis in labels are sloooow
        label.setStyleSheet(
            "QLabel {background-color: #00A030; padding: 3px; padding-left: 32px; border-radius: 4px; margin: 2px;}"
            "QLabel:hover { background-color: #008030;} "
        )
        self.action_update.setDefaultWidget(label)
        self.action_update.setVisible(False)
        self.menu.addAction(self.action_update)

        self.action_options = QAction("Options")
        self.action_options.triggered.connect(self.parent().options.show)
        self.menu.addAction(self.action_options)

        self.action_about = QAction("About")
        self.action_about.triggered.connect(self.parent().about.show)
        self.menu.addAction(self.action_about)

        self.quit_sep = self.menu.addSeparator()

        self.action_quit = QAction("Exit")
        self.action_quit.triggered.connect(self.parent().app.exit)
        self.menu.addAction(self.action_quit)

        self.setIcon(get_icon())
        self.setVisible(True)
        self.setContextMenu(self.menu)
        self.activated.connect(self.activate)

    def activate(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            cm = self.contextMenu()
            if cm:
                cm.popup(cm.cursor().pos())

    def enable_update_button(self, result: VersionCheckResult) -> None:
        if result.error is None:
            self.action_update.triggered.disconnect()
            self.action_update.triggered.connect(
                lambda: QDesktopServices.openUrl(QUrl(result.url))
            )
        # Breaks when setting invisible
        self.action_update.setVisible(result.error is None)
