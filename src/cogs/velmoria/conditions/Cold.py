from ..core.base import Condition


class Cold(Condition):
    def __init__(self, stacks=1):
        super().__init__(
            name="Cold",
            description="Cold units lose 3 speed per stack. Remove a stack at the end of every turn.",
            is_negative=True
        )
        self.stacks = stacks

    def on_turn_end(self, unit):
        if unit.is_alive():
            unit.speed[0] = unit.speed[1] - (self.stacks * 3)
            print(f"{unit.name} is freezing! Their speed is reduced to {unit.speed[0]}!")
        super().on_turn_end(unit)
