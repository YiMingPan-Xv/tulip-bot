from cogs.velmoria.core.base import Skill, SkillRegistry, Unit
import cogs.velmoria.conditions as conditions


@SkillRegistry.register
class ARTBlazingHeart(Skill):
    def __init__(self, owner: Unit = None):
        super().__init__(
            name='ART: Blazing Heart',
            description='Manifest your mindscape in wild flames engulfing your body and soul.\n'
                        'For 2 turns, deal an additional instance of 4 damage after a successful attack.'
                        'After eliminating an enemy target, extend these effects for another turn.',
            cost=3,
            owner=owner
        )

    async def use(self, target: Unit):
        await super().use(target)
        await self.owner.apply_condition(conditions.BlazingHeart, duration=3)
