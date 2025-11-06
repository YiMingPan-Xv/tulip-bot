from core.base import SkillRegistry, Skill, Unit
from conditions.Poisoned import Poisoned


@SkillRegistry.register
class BasicAttack(Skill):
    def __init__(self):
        super().__init__(
            name="Test-Basic Attack",
            description="Testing Use Skill Functionality"
        )

    def use(self, user: Unit, target: Unit):
        target.take_damage(2)


@SkillRegistry.register
class PoisonousBite(Skill):
    def __init__(self):
        super().__init__(
            name="Test-Poisonous Bite",
            description="Testing Use Skill Functionality"
        )

    def use(self, user: Unit, target: Unit):
        target.take_damage(1)
        poisoned = Poisoned(3)
        target.apply_status(poisoned)


@SkillRegistry.register
class DoNothing(Skill):
    def __init__(self):
        super().__init__(
            name="Test-Do Nothing",
            description="Testing Use Skill Functionality"
        )

    def use(self, user: Unit, target: Unit):
        print("Nothin happened!")
        pass