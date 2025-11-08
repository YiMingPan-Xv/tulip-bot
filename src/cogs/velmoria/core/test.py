# flake8: noqa
import sys
from pathlib import Path
import random

# Add project root (two levels up)
sys.path.append(str(Path(__file__).resolve().parents[3]))

from cogs.velmoria.core.base import Unit, EventBus
import cogs.velmoria.conditions as conditions
from cogs.velmoria.utils.auto_import import import_submodules
from cogs.velmoria.utils.load_unit import load

bus = EventBus()
import_submodules("cogs.velmoria.traits")
import_submodules("cogs.velmoria.skills")

# Create a unit with one trait
hero = load('Elena Frost', bus)

villain = Unit(
    name="Villain",
    health=47,
    attack=15,
    speed=5,
    cost=1,
    skills=["Strike", "ART: Blazing Heart"],
    traits=["Tough"],
    event_bus=bus
)

# Apply poison condition
hero.apply_condition(conditions.Poisoned, duration=3, damage_per_turn=2)

# Simulate turns
for i in range(4):
    print("\n--- Combat Simulation ---")
    hero.skills[1].use(villain)
    print(f"Hero HP: {hero.health[0]}/{hero.health[1]}")
    print(f"Villain HP: {villain.health[0]}/{villain.health[1]}")
    hero.end_turn()

    print("Villain monologues!")
    print(f"Villain HP: {villain.health[0]}/{villain.health[1]}")
    villain.end_turn()

hero.skills[3].use(villain)
print(f"Hero HP: {hero.health[0]}/{hero.health[1]}")
print(f"Villain HP: {villain.health[0]}/{villain.health[1]}")
hero.end_turn()

i = 0

while villain.health[0] > 0:
    print(f"\n--- Turn {i + 1} End ---")
    hero.skills[random.choices([0, 1], weights=[1.0, 0.0])[0]].use(villain)
    print(f"Hero HP: {hero.health[0]}/{hero.health[1]}")
    print(f"Villain HP: {villain.health[0]}/{villain.health[1]}")
    hero.end_turn()
    
    hero.apply_condition(conditions.Cold, duration=1)

    print("Villain monologues!")
    print(f"Hero HP: {hero.health[0]}/{hero.health[1]}")
    print(f"Villain HP: {villain.health[0]}/{villain.health[1]}")
    villain.end_turn()
    i += 1

print(bus.listeners)