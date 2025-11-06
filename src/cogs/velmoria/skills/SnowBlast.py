from ..core.base import Skill, SkillRegistry, Unit


@SkillRegistry.register
class SnowBlast(Skill):
    def __init__(self):
        super().__init__(
            name="Snow Blast",
            description="Pierce your enemy from within, every snowflake exploding to deal additional damage.\n"
                        "Deal 3 damage plus 2 per *Cold* stack on the target.",
            cost=2
        )

    def use(self, user: Unit, target: Unit):
        if "Cold" in target.statuses:
            target.take_damage(3 + 2 * target.statuses["Cold"].stacks)
        else:
            target.take_damage(3)
