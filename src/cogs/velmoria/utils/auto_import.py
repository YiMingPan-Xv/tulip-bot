import importlib
import pkgutil


def import_submodules(package_name):
    """Imports all submodules under a package (e.g., 'skills')."""
    package = importlib.import_module(package_name)
    print(package.__path__)
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        importlib.import_module(f"{package_name}.{name}")
        print("Imported a package!")
