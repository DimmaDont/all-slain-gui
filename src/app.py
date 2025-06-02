from PyQt6.QtWidgets import QApplication

from .allslain_patch import AllSlain
from .args import parse_args
from .config import load_config, load_config_runtime
from .windows.main import MainWindow


class App(QApplication):
    def __init__(self, argv: list[str]):
        super().__init__(argv)
        self.config = load_config()
        self.args = parse_args(namespace=load_config_runtime())
        self.allslain = AllSlain(self.args, self.config)
        self.main_window = MainWindow(self)
        self.aboutToQuit.connect(self.allslain.stopping)
        self.allslain.game_exit.connect(self.quit)

    def exec_(self) -> int:
        self.allslain.start()
        s = App.exec()
        self.allslain.wait()
        return s
