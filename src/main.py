import sys
from gc import collect

from .app import App


def main():
    while True:
        app = App(sys.argv)
        exit_code = app.exec_()
        if exit_code != app.main_window.EXIT_CODE_REBOOT:
            break
        del app
        collect()
    sys.exit(exit_code)
