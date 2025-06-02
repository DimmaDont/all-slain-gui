from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow

from ..update import UpdateCheck
from .about import About
from .options import Options
from .overlay import Overlay
from .tray_icon import TrayIcon


if TYPE_CHECKING:
    from ..app import App


logger = logging.getLogger("all-slain-gui").getChild("main")


class MainWindow(QMainWindow):
    EXIT_CODE_REBOOT = 762308

    def __init__(self, app: App):
        super().__init__()
        self.app = app

        self.about = About(self)
        self.options = Options(self)

        self.overlay = Overlay(self)
        self.overlay.show()

        self.options.overlay_update_screen.connect(self.overlay.set_screen)
        self.options.overlay_update_position.connect(self.overlay.update_position)
        self.options.overlay_update_line_count.connect(self.overlay.update_line_count)

        self.app.allslain.output.connect(self.overlay.update_text)

        self.tray_icon = TrayIcon(self)

        if __debug__:
            QTimer().singleShot(250, self.init_debug)

        if self.app.config["main"]["check_updates"]:
            self.uc = UpdateCheck()
            self.uc.result.connect(self.tray_icon.enable_update_button)
            self.uc.result.connect(self.overlay.add_message_update_available)
            self.uc.result.connect(self.about.show_update_check_result)
            QTimer().singleShot(250, self.uc.start)

    def slot_reboot(self):
        logger.debug("Performing application reboot...")
        self.app.exit(MainWindow.EXIT_CODE_REBOOT)

    def init_debug(self) -> None:
        logger.debug("console KeyboardInterrupt enabled")

        self.ki_timer = QTimer()  # pylint: disable=attribute-defined-outside-init
        self.ki_timer.timeout.connect(lambda: None)
        self.ki_timer.start(1000)

        self.options.show()
        self.about.show()
