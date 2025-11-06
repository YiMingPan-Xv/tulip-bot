from ..core.base import Skill, SkillRegistry, Unit
from ..conditions import Cold


@SkillRegistry.register
class IcyBreeze(Skill):
    def __init__(self):
        super().__init__(
            name="Icy Breeze",
            description="Conjure a freezing wind that bites on your enemy's flesh.\n"
                        "Deal 1 damage, and apply 2 stacks of *Cold*.",
            cost=1
        )

    def use(self, user: Unit, target: Unit):
        target.take_damage(1)
        cold = Cold(3)
        target.apply_status(cold)
