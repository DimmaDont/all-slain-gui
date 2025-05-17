from __future__ import annotations

import logging
from importlib.metadata import version

from allslain.version import GAME_VERSION, VersionCheckResult
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from ..functions import application_path, get_icon
from ..update import UpdateCheck


logger = logging.getLogger("all-slain-gui").getChild("about")


class About(QWidget):
    def show(self) -> None:
        super().show()
        self.raise_()

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
        self.setWindowTitle("About")
        self.setWindowIcon(get_icon())

        screen = QApplication.primaryScreen()
        if not screen:
            raise RuntimeError()
        qrect = QStyle.alignedRect(
            Qt.LayoutDirection.LayoutDirectionAuto,
            Qt.AlignmentFlag.AlignCenter,
            QSize(300, 500),
            screen.availableGeometry(),
        )
        self.setGeometry(qrect)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        logo_widget = QLabel()
        logo = QPixmap()
        logo.load(f"{application_path()}/icon/ded.png")
        logo_widget.setPixmap(logo)
        logo_widget.setStyleSheet("min-height: 220px")
        layout.addWidget(logo_widget, stretch=0, alignment=Qt.AlignmentFlag.AlignCenter)

        about = QLabel(
            '<b style="font-size: 36px">all-slain-gui</b>'
            f'<br><code style="color: cyan">{version("allslain_gui")}</code>'
            "<br><br>"
            f'running <b>all-slain</b> <code style="color: cyan">{version("allslain")}</code>'
            "<br>"
            f'updated for <b>Star Citizen</b> {GAME_VERSION.phase} <code style="color: cyan">{GAME_VERSION.version}</code>'
        )
        about.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(about)

        links = QLabel(
            "<br>"
            '<a href="https://github.com/DimmaDont/all-slain-gui">https://github.com/DimmaDont/all-slain-gui</a>'
            "<br>"
            '<a href="https://github.com/DimmaDont/all-slain">https://github.com/DimmaDont/all-slain</a>'
        )
        links.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        links.setOpenExternalLinks(True)
        layout.addWidget(links)

        self.button_check_updates = QPushButton("Check for Updates", self)
        self.button_check_updates.clicked.connect(self.click_check_update)
        self.button_check_updates.setStyleSheet("margin-top: 24px; padding: 4px;")
        layout.addWidget(self.button_check_updates)

        self.update_check_result = QLabel()
        self.update_check_result.setStyleSheet("min-height: 40px; max-width: 260px;")
        self.update_check_result.setWordWrap(True)
        self.update_check_result.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        self.update_check_result.setOpenExternalLinks(True)
        layout.addWidget(self.update_check_result)

        self.setLayout(layout)

        self.uc = UpdateCheck()
        self.uc.result.connect(self.update_check_complete)

    def click_check_update(self) -> None:
        self.button_check_updates.setDisabled(True)
        self.update_check_result.setText("...")

        QTimer().singleShot(0, self.uc.start)

    def clear_check_result(self) -> None:
        self.button_check_updates.setDisabled(False)
        self.update_check_result.clear()

    def update_check_complete(self, result: VersionCheckResult) -> None:
        logger.debug("update check complete")
        if result.error:
            if result.version:
                self.update_check_result.setText(
                    '<span style="color: green">all-slain-gui is up to date</span>'
                )
                QTimer().singleShot(30000, self.clear_check_result)
            else:
                self.update_check_result.setText(
                    f'<span style="color: red">{result.error}</span>'
                )
        else:
            self.update_check_result.setText(
                f'<span style="color: green">Update available:</span> <a href="{result.url}">v{result.version}</a>'
            )
