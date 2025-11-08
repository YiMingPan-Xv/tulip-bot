from cogs.velmoria.core.base import Skill, SkillRegistry, Unit, ACTION_THRESHOLD
import random


@SkillRegistry.register
class CinnamonRollTakeOff(Skill):
    def __init__(self, owner: Unit = None):
        super().__init__(
            name='Cinnamon Roll: Take Off!',
            description='Gear up, we\'re departing now! Cinnamon roll, take off to the skies!\n'
                        'Immediately advance the next acting ally\'s turn by 10% times the result of a die roll.',
            cost=4,
            owner=owner
        )

    async def use(self, target: Unit):
        await super().use(target)
        roll = random.randint(1, 6)
        target.action_value += roll * 0.1 * ACTION_THRESHOLD
