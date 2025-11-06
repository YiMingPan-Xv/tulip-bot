import importlib
import pkgutil

__all__ = []

for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")
    class_name = module_name
    if hasattr(module, class_name):
        globals()[class_name] = getattr(module, class_name)
        __all__.append(class_name)
