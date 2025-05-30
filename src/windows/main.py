from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from allslain.version import VersionCheckResult
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtWidgets import QLabel, QMainWindow, QMenu, QSystemTrayIcon, QWidgetAction

from src.functions import get_icon
from src.update import UpdateCheck
from src.windows.about import About
from src.windows.options import Options
from src.windows.overlay import Overlay


if TYPE_CHECKING:
    from ..app import App

logger = logging.getLogger("all-slain-gui").getChild("main")


class MainWindow(QMainWindow):
    EXIT_CODE_REBOOT = 762308

    def __init__(self, app: App):
        super().__init__()
        self.app = app

        self.options = Options(self)

        self.overlay = Overlay(self)
        self.overlay.show()

        self.options.overlay_update_position.connect(self.overlay.update_position)
        self.options.overlay_update_line_count.connect(self.overlay.update_line_count)

        self.app.allslain.output.connect(self.overlay.update_text)

        self.about = About(self)

        self.create_tray()

        if __debug__:
            QTimer().singleShot(250, self.init_debug)

    def slot_reboot(self):
        logger.debug("Performing application reboot...")
        self.app.exit(MainWindow.EXIT_CODE_REBOOT)

    def create_tray(self) -> None:
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
        self.action_options.triggered.connect(self.options.show)
        self.menu.addAction(self.action_options)

        self.action_about = QAction("About")
        self.action_about.triggered.connect(self.about.show)
        self.menu.addAction(self.action_about)

        self.quit_sep = self.menu.addSeparator()

        self.action_quit = QAction("Exit")
        self.action_quit.triggered.connect(self.app.exit)
        self.menu.addAction(self.action_quit)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(get_icon())
        self.tray.setVisible(True)
        self.tray.setContextMenu(self.menu)

        self.uc = UpdateCheck()
        self.uc.result.connect(self.enable_update_button)
        self.uc.result.connect(self.overlay.add_message_update_available)
        self.uc.result.connect(self.about.show_update_check_result)
        QTimer().singleShot(250, self.uc.start)

    def init_debug(self) -> None:
        logger.debug("console KeyboardInterrupt enabled")

        self.ki_timer = QTimer()  # pylint: disable=attribute-defined-outside-init
        self.ki_timer.timeout.connect(lambda: None)
        self.ki_timer.start(1000)

        self.options.show()
        self.about.show()

    def enable_update_button(self, result: VersionCheckResult) -> None:
        if result.url:
            self.action_update.triggered.connect(
                lambda: QDesktopServices.openUrl(QUrl(result.url))
            )
            self.action_update.setVisible(True)
