import sys

from .app import App


def main():
    app = App(sys.argv)
    sys.exit(app.exec_())

    # TODO app restart "works", but the old ui doesn't get destroyed
    # while True:
    #     app = App(sys.argv)
    #     exit_code = app.exec()
    #     if exit_code != app.main_window.EXIT_CODE_REBOOT:
    #         app.quit()
    #         break
    # sys.exit(exit_code)
