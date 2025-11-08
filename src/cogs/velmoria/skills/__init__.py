import os
import importlib

package_name = __name__

for filename in os.listdir(os.path.dirname(__file__)):
    if filename.endswith(".py") and filename not in ("__init__.py",):
        module_name = filename[:-3]
        module = importlib.import_module(f".{module_name}", package_name)
        for name, obj in vars(module).items():
            if isinstance(obj, type):
                globals()[name] = obj
