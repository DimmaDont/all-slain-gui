from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, cast

from allslain.config import save_config as save_config_allslain
from allslain.data_providers.starcitizen_api import Mode as ScApiMode
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QStyle,
    QWidget,
)

from ..config import save_config
from ..functions import get_icon


if TYPE_CHECKING:
    from src.app import MainWindow


logger = logging.getLogger("all-slain-gui").getChild("options")


DATA_PROVIDERS = {
    "": "",
    "Roberts Space Industries": "rsi",
    "Unofficial StarCitizen API": "starcitizen_api",
    "Wild Knight Squadron's NAVCOM API": "wks_navcom",
}

if __debug__:
    DATA_PROVIDERS["Dummy"] = "dummy"


OVERLAY_POSITIONS = {
    "Top Left": "top",
    "Bottom Left": "bottom",
}


def hr() -> QFrame:
    _hr = QFrame()
    _hr.setFrameShape(QFrame.Shape.HLine)
    _hr.setFrameShadow(QFrame.Shadow.Sunken)
    return _hr


RED_ASTERISK = '<span style="color: red">*</span>'


class Options(QWidget):
    parent: Callable[[], MainWindow]
    overlay_update_position = Signal(str)

    def show(self):
        super().show()
        self.raise_()

    def __init__(self, parent: MainWindow):
        super().__init__(parent)

        self.config_gui = self.parent().app.config
        self.config_als = self.parent().app.allslain.config

        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowTitle("Options")
        self.setWindowIcon(get_icon())

        screen = QApplication.primaryScreen()
        if not screen:
            raise RuntimeError()
        qrect = QStyle.alignedRect(
            Qt.LayoutDirection.LayoutDirectionAuto,
            Qt.AlignmentFlag.AlignCenter,
            QSize(512, 512),
            screen.availableGeometry(),
        )
        self.setGeometry(qrect)

        self.form = QFormLayout()
        self.setLayout(self.form)

        # layout.setSpacing(0)

        self.form.addRow(QLabel("<b>Overlay</b>"))

        input_overlay_pos = QComboBox()
        input_overlay_pos.addItems(OVERLAY_POSITIONS.keys())
        input_overlay_pos.setCurrentText(
            next(
                (
                    k
                    for k, v in OVERLAY_POSITIONS.items()
                    if v == self.config_gui["main"]["overlay_position"]
                ),
                next(iter(OVERLAY_POSITIONS.keys())),
            )
        )
        input_overlay_pos.currentTextChanged.connect(self.overlay_update_position.emit)
        input_overlay_pos.currentTextChanged.connect(self.save_overlay_position)
        self.form.addRow(QLabel("Position"), input_overlay_pos)

        input_auto_exit = QCheckBox()
        input_auto_exit.setChecked(self.config_gui["main"]["auto_exit"])
        input_auto_exit.clicked.connect(self.save_auto_exit)
        input_auto_exit.setToolTip(
            "Exit with Star Citizen.<br>"
            "Every 5 seconds, checks to see if the game is still running."
        )
        self.form.addRow(QLabel("Auto Exit " + RED_ASTERISK), input_auto_exit)

        self.form.addRow(hr())

        self.form.addRow(QLabel("<b>all-slain Settings</b>"))

        self.input_player_lookup = QCheckBox()
        self.input_player_lookup.setChecked(
            self.parent().app.allslain.args.player_lookup
        )
        self.input_player_lookup.clicked.connect(self.save_player_lookup)
        self.form.addRow(QLabel("Display Player Org"), self.input_player_lookup)

        provider = next(
            (
                (k, v)
                for k, v in DATA_PROVIDERS.items()
                if v == self.parent().app.allslain.args.data_provider.provider
            ),
            ("", ""),
        )

        input_dataprovider = QComboBox()
        input_dataprovider.addItems(DATA_PROVIDERS.keys())
        input_dataprovider.setCurrentText(provider[0])
        input_dataprovider.currentTextChanged.connect(self.save_dataprovider_provider)
        self.form.addRow("Data Provider " + RED_ASTERISK, input_dataprovider)

        input_use_org_theme = QCheckBox()
        input_use_org_theme.setToolTip(
            "Whether to pull and display the org's Spectrum theme color when displaying an org.<br>"
            "Currently only available with the <b><code>RSI</code></b> data provider."
        )
        input_use_org_theme.setChecked(
            self.parent().app.allslain.args.data_provider.use_org_theme
        )
        input_use_org_theme.clicked.connect(self.save_org_theme)
        self.form.addRow("Use Org Theme", input_use_org_theme)

        self.form.addRow(hr())
        self.scapi_layout = QFormLayout()
        self.scapi_layout.setHorizontalSpacing(5)
        self.form.addRow(QLabel("<b>Unofficial Star Citizen API</b>"))

        self.input_starcitizen_api_key = QLineEdit()
        self.input_starcitizen_api_key.setPlaceholderText("API Key")
        self.input_starcitizen_api_key.setText(
            self.parent().app.allslain.args.data_provider.starcitizen_api.api_key
        )
        self.input_starcitizen_api_key.setDisabled(provider[1] != "starcitizen_api")
        self.input_starcitizen_api_key.textChanged.connect(
            self.save_starcitizen_api_key
        )

        self.form.addRow("API Key " + RED_ASTERISK, self.input_starcitizen_api_key)

        # TODO 3.11 StrEnum
        starcitizen_api_mode_text = cast(
            str, self.parent().app.allslain.args.data_provider.starcitizen_api.mode
        )

        self.input_starcitizen_api_mode = QComboBox()
        self.input_starcitizen_api_mode.addItems(v.value for v in ScApiMode)
        self.input_starcitizen_api_mode.setCurrentText(starcitizen_api_mode_text)
        self.input_starcitizen_api_mode.currentTextChanged.connect(
            self.save_starcitizen_api_mode
        )
        self.input_starcitizen_api_mode.setDisabled(provider[1] != "starcitizen_api")
        self.form.addRow("Mode " + RED_ASTERISK, self.input_starcitizen_api_mode)

        self.form.addItem(self.scapi_layout)
        self.form.addRow(hr())

        # self.restart_button = QPushButton()
        # self.restart_button.setText("Restart")
        # self.restart_button.clicked.connect(self.parent().slot_reboot)
        # self.form.addRow(QLabel('<span style="color: red">*</span> Requires restart'), self.restart_button)
        self.form.addRow(QLabel(RED_ASTERISK + " Requires restart"))

    def save_overlay_position(self, position: str):
        logger.debug("saving overlay position")
        pos = OVERLAY_POSITIONS.get(position)
        self.config_gui["main"]["overlay_position"] = pos
        save_config(self.config_gui)

    def save_auto_exit(self, auto_exit: bool):
        self.config_gui["main"]["auto_exit"] = auto_exit
        save_config(self.config_gui)

    def save_player_lookup(self, player_lookup: bool):
        # self.input_player_lookup.setDisabled(True)
        self.config_als["main"]["player_lookup"] = player_lookup
        self.parent().app.allslain.args.player_lookup = player_lookup
        save_config_allslain(self.config_als)
        # self.input_player_lookup.setDisabled(False)

    def save_dataprovider_provider(self, text: str):
        # Requires a restart
        dp = DATA_PROVIDERS.get(text)
        self.input_starcitizen_api_key.setDisabled(dp != "starcitizen_api")
        self.input_starcitizen_api_mode.setDisabled(dp != "starcitizen_api")

        # try:
        #     # This destroys the C Qt objects too?
        #     # self._layout.removeRow(self.input_starcitizen_api_key)
        #     # self._layout.removeRow(self.input_starcitizen_api_mode)
        # except AttributeError:
        #     pass

        self.config_als["data_provider"]["provider"] = dp
        save_config_allslain(self.config_als)

    def save_org_theme(self, use_org_theme: bool):
        self.config_als["data_provider"]["use_org_theme"] = use_org_theme
        self.parent().app.allslain.args.data_provider.use_org_theme = use_org_theme
        save_config_allslain(self.config_als)

    def save_starcitizen_api_key(self, api_key: str):
        logger.debug("saving scapi key")
        self.config_als["data_provider"]["starcitizen_api"]["api_key"] = api_key
        save_config_allslain(self.config_als)

    def save_starcitizen_api_mode(self, mode_text: str):
        logger.debug("saving scapi mode")
        self.config_als["data_provider"]["starcitizen_api"]["mode"] = mode_text.lower()
        save_config_allslain(self.config_als)
