import os
from argparse import Namespace
from typing import TYPE_CHECKING, Literal, cast

from allslain.config import TOMLFile, executable_path, merge, mergeattr
from tomlkit import TOMLDocument, comment, document, nl, table


CONFIG_NAME = f"{executable_path()}/allslain_gui.conf.toml"


OverlayPosition = Literal["top", "bottom"]


if TYPE_CHECKING:
    from typing import TypedDict

    class ConfigMain(TypedDict):
        screen: str
        overlay_position: OverlayPosition
        auto_exit: bool
        line_count: int
        check_updates: bool

    # Not allowed, but it works™
    class ConfigDocument(TOMLDocument, TypedDict):  # type: ignore
        main: ConfigMain

else:
    ConfigDocument = TOMLDocument


class Config(Namespace):
    screen: str = ""
    overlay_position: OverlayPosition = "top"
    auto_exit: bool = True
    line_count: int = 4
    check_updates: bool = True


# fmt: off
def create_default_config() -> TOMLDocument:
    doc = document()

    main = table()

    main.add(comment("Which monitor the overlay is displayed on."))
    main.add("screen", Config.screen)
    main.add(nl())

    main.add(comment("Whether the overlay should be on the top left of the screen or the bottom left."))
    main.add(comment('Default: "top"'))
    main.add("overlay_position", Config.overlay_position)
    main.add(nl())

    main.add(comment("Whether all-slain-gui should also quit when Star Citizen quits."))
    main.add(comment('Default: true'))
    main.add("auto_exit", Config.auto_exit)
    main.add(nl())

    main.add(comment("Number of lines to display in the overlay"))
    main.add(comment('Default: 4'))
    main.add("line_count", Config.line_count)
    main.add(nl())

    main.add(comment("Check for updates on startup"))
    main.add(comment('Default: true'))
    main.add("check_updates", Config.check_updates)
    main.add(nl())

    doc.add("main", main)

    return doc
# fmt: on


def load_config() -> ConfigDocument:
    # Load defaults and config file
    config = create_default_config()
    if os.path.exists(CONFIG_NAME):
        _config = TOMLFile(CONFIG_NAME).read()
        # Do not use dict.update or |= here
        merge(_config, config)
    else:
        _config = document()

    TOMLFile(CONFIG_NAME).write_if_modified(config, _config)

    return cast(ConfigDocument, config)


def load_config_runtime(namespace: Namespace | None = None) -> Config:
    config = cast(TOMLDocument, load_config())
    if not namespace:
        namespace = Config()
    mergeattr(config.pop("main"), namespace)
    mergeattr(config, namespace)

    return cast(Config, namespace)


def save_config(config: ConfigDocument) -> None:
    TOMLFile(CONFIG_NAME).write(cast(TOMLDocument, config).as_string())
