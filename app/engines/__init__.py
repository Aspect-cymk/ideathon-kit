"""Auto-discovery: drop a new Engine subclass into this folder and it is registered."""
import importlib
import pkgutil

from .base import Engine, EngineError, make_result  # noqa: F401

_REGISTRY = {}


def _load():
    for mod in pkgutil.iter_modules(__path__):
        if mod.name == "base":
            continue
        module = importlib.import_module(f"{__name__}.{mod.name}")
        for obj in vars(module).values():
            if isinstance(obj, type) and issubclass(obj, Engine) and obj is not Engine and obj.name:
                _REGISTRY[obj.name] = obj()


def all_engines():
    if not _REGISTRY:
        _load()
    return _REGISTRY


def get_engine(name):
    return all_engines().get(name)
