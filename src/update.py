from __future__ import annotations

import logging
from importlib.metadata import version
from typing import TYPE_CHECKING, cast

from allslain.version import VersionCheckResult, get_latest_version
from packaging.version import Version
from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal as Signal


if TYPE_CHECKING:
    pass


logger = logging.getLogger("all-slain-gui").getChild("update")


class UpdateCheck(QThread):
    result = Signal(VersionCheckResult)

    def __init__(self):
        super().__init__()
        self.setObjectName("UpdateCheck")

    def run(self):
        logger.debug("update check started")
        if not __debug__:
            response = get_latest_version("all-slain-gui")
        else:
            self.msleep(1000)
            response = VersionCheckResult(
                None,
                Version("1.0.0"),
                "file:///C:/Python313/Doc/html/index.html",
            )
        logger.debug("update check complete")
        if response.error or cast(Version, response.version) > Version(
            version("allslain_gui")
        ):
            self.result.emit(response)
        else:
            self.result.emit(
                VersionCheckResult("no updates", response.version, response.url)
            )
