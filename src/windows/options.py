from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, cast

from allslain.data_providers.starcitizen_api import Mode as ScApiMode
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QStyle,
    QTabWidget,
    QWidget,
)

from ..allslain_patch import save_config as save_config_allslain
from ..config import OverlayPosition, save_config
from ..functions import get_icon


if TYPE_CHECKING:
    from ..app import MainWindow


logger = logging.getLogger("all-slain-gui").getChild("options")


DATA_PROVIDERS = {
    "": "",
    "Roberts Space Industries": "rsi",
    "Unofficial StarCitizen API": "starcitizen_api",
    "Wild Knight Squadron's NAVCOM API": "wks_navcom",
}

DATA_PROVIDERS_HELPTEXT = {
    "": "No data provider selected.",
    "rsi": "Roberts Space Industries",
    "starcitizen_api": "Unofficial Star Citizen API<br><b>Requires an API key!</b>",
    "wks_navcom": "Wild Knight Squadron's NAVCOM API",
}

DATA_PROVIDERS_HELPTEXTLINK = {
    "": "",
    "rsi": '<a href="https://robertsspaceindustries.com/">https://robertsspaceindustries.com/</a>',
    "starcitizen_api": '<a href="https://starcitizen-api.com/">https://starcitizen-api.com/</a>',
    "wks_navcom": '<a href="https://sentry.wildknightsquadron.com/">https://sentry.wildknightsquadron.com/</a>',
}


if __debug__:
    DATA_PROVIDERS["Dummy"] = "dummy"
    DATA_PROVIDERS_HELPTEXT["dummy"] = "aeiou"
    DATA_PROVIDERS_HELPTEXTLINK["dummy"] = (
        '<a href="https://example.com/">https://example.com/</a>'
    )


OVERLAY_POSITIONS = {
    "Top Left": "top",
    "Bottom Left": "bottom",
}


def hr() -> QFrame:
    _hr = QFrame()
    _hr.setFrameShape(QFrame.Shape.HLine)
    _hr.setFrameShadow(QFrame.Shadow.Sunken)
    return _hr


def QLabelDisabled(text: str) -> QLabel:  # pylint: disable=invalid-name
    ql = QLabel(text)
    ql.setDisabled(True)
    return ql


RED_ASTERISK = '<span style="color: red">*</span>'


class Options(QWidget):
    parent: Callable[[], MainWindow]
    overlay_update_screen = Signal(str)
    overlay_update_position = Signal(str)
    overlay_update_line_count = Signal(int)

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
        if screen is None:
            raise RuntimeError()
        qrect = QStyle.alignedRect(
            Qt.LayoutDirection.LayoutDirectionAuto,
            Qt.AlignmentFlag.AlignCenter,
            QSize(512, 512),
            screen.availableGeometry(),
        )
        self.setGeometry(qrect)

        form = QFormLayout()
        self.setLayout(form)

        widget_tab = QTabWidget()
        widget_tab.addTab(self.create_widget_overlay(), "Overlay")
        widget_tab.addTab(self.create_widget_allslain(), "Log")
        widget_tab.addTab(self.create_widget_misc(), "Misc.")
        form.addRow(widget_tab)

        restart_button = QPushButton()
        restart_button.setText("Restart")
        restart_button.clicked.connect(self.parent().slot_reboot)
        form.addRow(
            QLabel('<span style="color: red">*</span> Requires restart'),
            restart_button,
        )

    def create_widget_overlay(self):
        form = QFormLayout()

        input_overlay_screen = QComboBox()
        input_overlay_screen.addItems(s.name() for s in QApplication.screens())
        input_overlay_screen.setCurrentText(self.config_gui["main"]["screen"])
        input_overlay_screen.currentTextChanged.connect(self.overlay_update_screen.emit)
        input_overlay_screen.currentTextChanged.connect(self.save_overlay_screen)
        form.addRow(QLabel("Monitor"), input_overlay_screen)

        overlay_pos = next(
            (
                k
                for k, v in OVERLAY_POSITIONS.items()
                if v == self.config_gui["main"]["overlay_position"]
            ),
            next(iter(OVERLAY_POSITIONS.keys())),
        )

        input_overlay_pos = QComboBox()
        input_overlay_pos.addItems(OVERLAY_POSITIONS.keys())
        input_overlay_pos.setCurrentText(overlay_pos)
        input_overlay_pos.currentTextChanged.connect(self.overlay_update_position.emit)
        input_overlay_pos.currentTextChanged.connect(self.save_overlay_position)
        form.addRow(QLabel("Position"), input_overlay_pos)

        input_line_count = QSpinBox()
        input_line_count.setMinimum(3)
        input_line_count.setMaximum(5)
        input_line_count.setValue(self.config_gui["main"]["line_count"])
        input_line_count.valueChanged.connect(self.overlay_update_line_count.emit)
        input_line_count.valueChanged.connect(self.save_line_count)
        form.addRow(QLabel("Lines Shown"), input_line_count)

        widget = QWidget()
        widget.setLayout(form)
        return widget

    def create_widget_allslain_uscapi(self):
        form = QFormLayout()

        input_starcitizen_api_key = QLineEdit()
        input_starcitizen_api_key.setPlaceholderText("API Key")
        input_starcitizen_api_key.setText(
            self.parent().app.allslain.args.data_provider.starcitizen_api.api_key
        )
        input_starcitizen_api_key.textChanged.connect(self.save_starcitizen_api_key)

        form.addRow("API Key " + RED_ASTERISK, input_starcitizen_api_key)

        # TODO 3.11 StrEnum
        starcitizen_api_mode_text = cast(
            str, self.parent().app.allslain.args.data_provider.starcitizen_api.mode
        )

        input_starcitizen_api_mode = QComboBox()
        input_starcitizen_api_mode.addItems(v.value for v in ScApiMode)
        input_starcitizen_api_mode.setCurrentText(starcitizen_api_mode_text)
        input_starcitizen_api_mode.currentTextChanged.connect(
            self.save_starcitizen_api_mode
        )
        form.addRow("Mode " + RED_ASTERISK, input_starcitizen_api_mode)

        widget = QGroupBox("Unofficial Star Citizen API")
        widget.setLayout(form)
        return widget

    def create_widget_allslain(self):
        form = QFormLayout()

        self.input_player_lookup = QCheckBox()
        self.input_player_lookup.setChecked(
            self.parent().app.allslain.args.player_lookup
        )
        self.input_player_lookup.clicked.connect(self.save_player_lookup)
        form.addRow(QLabel("Display Player Org"), self.input_player_lookup)
        form.addRow(
            QLabelDisabled(
                "Whether to perform player org lookups. If checked, select a data provider below."
            )
        )
        form.addRow(hr())

        provider: tuple[str, str] = next(
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
        form.addRow("Data Provider " + RED_ASTERISK, input_dataprovider)
        self.label_dataprovider = QLabelDisabled(
            DATA_PROVIDERS_HELPTEXT.get(provider[1], provider[0])
        )
        form.addRow(self.label_dataprovider)
        self.label_dataprovider_link = QLabel(
            DATA_PROVIDERS_HELPTEXTLINK.get(provider[1], provider[0])
        )
        self.label_dataprovider_link.setOpenExternalLinks(True)
        form.addRow(self.label_dataprovider_link)
        form.addRow(hr())

        input_use_org_theme = QCheckBox()
        input_use_org_theme.setChecked(
            self.parent().app.allslain.args.data_provider.use_org_theme
        )
        input_use_org_theme.clicked.connect(self.save_org_theme)
        form.addRow("Use Org Theme", input_use_org_theme)
        form.addRow(
            QLabelDisabled(
                "Whether to display the org's theme color from Spectrum.<br>"
                "Currently only available with the <b>Roberts Space Industries</b> data provider."
            )
        )
        form.addRow(hr())

        self.widget_uscapi = self.create_widget_allslain_uscapi()
        self.widget_uscapi.setEnabled(provider[1] == "starcitizen_api")
        form.addRow(self.widget_uscapi)

        widget = QWidget()
        widget.setLayout(form)
        return widget

    def create_widget_misc(self):
        form = QFormLayout()

        input_auto_exit = QCheckBox()
        input_auto_exit.setChecked(self.config_gui["main"]["auto_exit"])
        input_auto_exit.clicked.connect(self.save_auto_exit)
        form.addRow(QLabel("Auto Exit " + RED_ASTERISK), input_auto_exit)
        form.addRow(QLabelDisabled("Exit when Star Citizen does."))
        form.addRow(hr())

        input_check_updates = QCheckBox()
        input_check_updates.setChecked(self.config_gui["main"]["check_updates"])
        input_check_updates.clicked.connect(self.save_check_updates)
        form.addRow(QLabel("Auto Update Check " + RED_ASTERISK), input_check_updates)
        form.addRow(QLabelDisabled("Checks for updates at startup."))
        form.addRow(hr())

        widget = QWidget()
        widget.setLayout(form)
        return widget

    def save_overlay_screen(self, screen: str):
        logger.debug("saving overlay screen")
        self.config_gui["main"]["screen"] = screen
        save_config(self.config_gui)

    def save_overlay_position(self, position: str):
        logger.debug("saving overlay position")
        pos = cast(OverlayPosition, OVERLAY_POSITIONS.get(position))
        self.config_gui["main"]["overlay_position"] = pos
        save_config(self.config_gui)

    def save_auto_exit(self, auto_exit: bool):
        self.config_gui["main"]["auto_exit"] = auto_exit
        save_config(self.config_gui)

    def save_line_count(self, line_count: int):
        self.config_gui["main"]["line_count"] = line_count
        save_config(self.config_gui)

    def save_check_updates(self, check_updates: bool):
        self.config_gui["main"]["check_updates"] = check_updates
        save_config(self.config_gui)

    def save_player_lookup(self, player_lookup: bool):
        # self.input_player_lookup.setDisabled(True)
        self.config_als["main"]["player_lookup"] = player_lookup
        self.parent().app.allslain.args.player_lookup = player_lookup
        save_config_allslain(self.config_als)
        # self.input_player_lookup.setDisabled(False)

    def save_dataprovider_provider(self, text: str):
        # Requires a restart
        dp = DATA_PROVIDERS.get(text, text)
        self.widget_uscapi.setEnabled(dp == "starcitizen_api")

        # try:
        #     # This destroys the C Qt objects too?
        #     # self._layout.removeRow(self.input_starcitizen_api_key)
        #     # self._layout.removeRow(self.input_starcitizen_api_mode)
        # except AttributeError:
        #     pass

        self.label_dataprovider.setText(DATA_PROVIDERS_HELPTEXT.get(dp))
        self.label_dataprovider_link.setText(DATA_PROVIDERS_HELPTEXTLINK.get(dp))

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
        self.config_als["data_provider"]["starcitizen_api"]["mode"] = ScApiMode[
            mode_text.upper()
        ]
        save_config_allslain(self.config_als)
