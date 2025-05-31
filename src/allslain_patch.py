"""

Surgery, surgery

"""

from __future__ import annotations

import datetime
import logging
from io import TextIOWrapper
from pathlib import Path
from struct import pack
from typing import TYPE_CHECKING, cast

from allslain.args import Args
from allslain.colorize import Color
from allslain.config import load_config, load_config_runtime
from allslain.config import save_config as _save_config
from allslain.data_providers.starcitizen_api import Mode
from allslain.handlers.handler import Handler
from allslain.log_parser import LogParser
from psutil import process_iter
from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal as Signal
from tomlkit import TOMLDocument


if TYPE_CHECKING:
    from typing import TypedDict

    from .args import Args as GuiArgs

    class StarCitizenApi(TypedDict):
        api_key: str
        mode: Mode

    class DataProvider(TypedDict):
        provider: str
        use_org_theme: bool

        starcitizen_api: StarCitizenApi

    class AlsConfigMain(TypedDict):
        player_lookup: bool
        planespotting: bool

    class ConfigDocument(TOMLDocument, TypedDict):  # type: ignore
        main: AlsConfigMain
        data_provider: DataProvider

else:
    ConfigDocument = TOMLDocument


def save_config(config: ConfigDocument) -> None:
    _save_config(cast(TOMLDocument, config))


COLOR_MAP = {
    "BLACK": "#0C0C0C",
    "RED": "#C50F1F",
    "GREEN": "#13A10D",
    "YELLOW": "#C19C00",
    "BLUE": "#0037DA",
    "MAGENTA": "#881798",
    "CYAN": "#3A96DD",
    "WHITE": "#CCCCCC",
}

COLOR_MAP_BOLD = {
    "BLACK": "#767676",
    "RED": "#E74856",
    "GREEN": "#16C60C",
    "YELLOW": "#E6E600",
    "BLUE": "#3B78FF",
    "MAGENTA": "#B4009E",
    "CYAN": "#61D6D6",
    "WHITE": "#F2F2F2",
}

ColorTerminal = Color


GAME_EXE = "StarCitizen.exe" if not __debug__ else "mpv.exe"


def color2__call__(
    self: Color, text: object, bold: bool = False, bg=None, bg_bold: bool = False
) -> str:
    name = COLOR_MAP_BOLD[self.name] if bold else COLOR_MAP[self.name]
    return f'<span style="color: {name}">{str(text).replace(" ", "&nbsp;")}</span>'


def color2_rgb(
    fg: tuple[int, int, int] | None = None,
    bg: tuple[int, int, int] | None = None,
    bold: bool = False,
    text: str = "",
) -> str:
    if not fg:
        return ""
    return f'<span style="color: #{pack("BBB", *fg).hex()}">{text.replace(" ", "&nbsp;")}</span>'


Color.__call__ = color2__call__
Color.rgb = color2_rgb


logger = logging.getLogger("all-slain-gui").getChild("all-slain")


class AllSlain(QThread):
    output = Signal(object)
    game_exit = Signal()

    def __init__(_self, gui_args: GuiArgs):
        super().__init__()
        _self.setObjectName("AllSlain")
        _self._initialized = False
        _self._stopping = False

        def handler_output(self: Handler, text: str):
            dt_local = (
                datetime.datetime.strptime(
                    self.state.curr_event_timestr, "%Y-%m-%d %H:%M:%S"
                )
                .replace(tzinfo=datetime.timezone.utc)
                .astimezone()
            ).strftime("%Y-%m-%d %H:%M:%S")
            _self.output.emit(f"{dt_local}{self.header_text}: {text}")

        Handler.output = handler_output

        def logparser_follow(self: LogParser, f: TextIOWrapper):
            if gui_args.auto_exit:
                check_running_counter = 0
                while not _self._stopping:
                    if line := f.readline():
                        yield line.rstrip(self.LOG_NEWLINE)
                    else:
                        _self.msleep(1000)
                        if check_running_counter > 5:
                            if _self.get_game_proc() is None:
                                break
                            check_running_counter = 0
                        check_running_counter += 1
            else:
                while not _self._stopping:
                    if line := f.readline():
                        yield line.rstrip(self.LOG_NEWLINE)
                    else:
                        _self.msleep(1000)

        LogParser.follow = logparser_follow

        _self.args = cast(Args, load_config_runtime(gui_args))
        _self.args.file = None
        _self.args.replay = False

        _self.config = cast(ConfigDocument, load_config())

    def stopping(self):
        self._stopping = True

    def get_game_proc(self):
        return next(
            (
                proc
                for proc in process_iter(attrs=["name", "exe"])
                if proc.info["name"] == GAME_EXE
            ),
            None,
        )

    def wait_game(self):
        while not self._stopping:
            proc = self.get_game_proc()
            if proc is None:
                self.msleep(1000)
                continue

            self.args.file = str(Path(Path(proc.info["exe"]).parent.parent, "Game.log"))
            break

        self._initialized = True

    def run(self):
        if not self._initialized:
            logger.debug("waiting for game")
            self.wait_game()
        if self.args.file is None:
            logger.debug("quit before game start")
            return
        logger.debug("game started")
        with LogParser(self.args) as log_parser:
            log_parser.run()
        logger.debug("allslain done")
        self.game_exit.emit()
