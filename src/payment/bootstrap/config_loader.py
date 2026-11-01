import os
import tomllib
from typing import Any

from adaptix import Retort

DEFAULT_CONFIG_PATH = "./config/config.toml"


def read_toml(path: str) -> dict[str, Any]:
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_config[T](config_type: type[T], config_scope: str | None = None, path: str | None = None) -> T:
    if path is None:
        path = os.getenv("CONFIG_PATH", DEFAULT_CONFIG_PATH)

    data = read_toml(path)

    if config_scope is not None:
        data = data.get(config_scope, {})

    return Retort(strict_coercion=False).load(data, config_type)
