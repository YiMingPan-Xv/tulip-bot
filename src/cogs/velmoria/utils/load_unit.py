import json
from pathlib import Path

from cogs.velmoria.core.base import Unit


data_path = str(Path(__file__).parents[4] / 'data' / 'units.json')


def load(name, bus, ctx):
    with open(data_path, 'r') as f:
        data = json.load(f)
    unit_data = data.get(name)
    return Unit(name, unit_data['health'], unit_data['attack'], unit_data['speed'], unit_data['cost'],
                unit_data['skills'], unit_data['traits'], bus, [], ctx)
