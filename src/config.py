import os
from argparse import Namespace
from typing import Literal, cast

from allslain.config import TOMLFile, executable_path, merge, mergeattr
from tomlkit import (
    TOMLDocument,
    comment,
    document,
    nl,
    table,
)


CONFIG_NAME = f"{executable_path()}/allslain_gui.conf.toml"


class Config(Namespace):
    overlay_position: Literal["top", "bottom"] = "top"
    auto_exit: bool = True


# fmt: off
def create_default_config() -> TOMLDocument:
    doc = document()

    main = table()

    main.add(comment("Whether the overlay should be on the top left of the screen or the bottom left."))
    main.add(comment('Default: "top"'))
    main.add("overlay_position", Config.overlay_position)
    main.add(nl())

    main.add(comment("Whether all-slain-gui should also quit when Star Citizen quits."))
    main.add(comment('Default: true'))
    main.add("auto_exit", Config.auto_exit)
    main.add(nl())

    doc.add("main", main)

    return doc
# fmt: on


def load_config() -> TOMLDocument:
    # Load defaults and config file
    config = create_default_config()
    if os.path.exists(CONFIG_NAME):
        _config = TOMLFile(CONFIG_NAME).read()
        # Do not use dict.update or |= here
        merge(_config, config)
    else:
        _config = document()

    TOMLFile(CONFIG_NAME).write_if_modified(config, _config)

    return config


def load_config_runtime(namespace: Namespace | None = None) -> Config:
    config = load_config()
    if not namespace:
        namespace = Config()
    mergeattr(config.pop("main"), namespace)
    mergeattr(config, namespace)

    return cast(Config, namespace)


def save_config(config: TOMLDocument) -> None:
    TOMLFile(CONFIG_NAME).write(config.as_string())
