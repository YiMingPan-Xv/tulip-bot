from core.base import Condition


class Poisoned(Condition):
    def __init__(self, stacks=1):
        super().__init__(
            name="Poisoned",
            description="Poisoned units take 1 damage each turn. Remove a stack at the end of every turn.",
            is_negative=True
        )
        self.stacks = stacks

    def on_turn_end(self, unit):
        if unit.is_alive():
            print(f"{unit.name} suffers damage from poison!")
            unit.take_damage(1)
        super().on_turn_end(unit)
