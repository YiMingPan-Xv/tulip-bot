from ..core.base import Trait


class Resilient(Trait):
    name = "Resilient"
    description = "The unit's resilience reduces any damage taken higher than 3 by 1."

    def about_to_receive_damage(self, unit, damage):
        if damage > 3:
            unit.damage_mitigation += 1
