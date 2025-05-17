import sys
from os.path import dirname

from PyQt6.QtGui import QIcon


def application_path() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # https://pyinstaller.org/en/stable/runtime-information.html#using-sys-executable-and-sys-argv-0
        return sys._MEIPASS  # pylint: disable=protected-access
    import __main__

    return dirname(__main__.__file__)


def get_icon() -> QIcon:
    return QIcon(f"{application_path()}/icon/ded.ico")
