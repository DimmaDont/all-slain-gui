import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import cast

from allslain.colorize import Color

from .config import Config


class Args(Config):
    debug: bool


logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("all-slain-gui")


def parse_args(namespace) -> Args:
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=(
            "all-slain-gui: Star Citizen Game Log Overlay\n"
            + Color.BLUE("https://github.com/DimmaDont/all-slain-gui", bold=True)
        ),
    )
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-v", "--verbose", action="count", default=0)

    args = cast(Args, parser.parse_args(namespace=namespace))

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("allslain").setLevel(logging.DEBUG)

    return args
