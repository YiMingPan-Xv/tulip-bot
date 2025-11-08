from cogs.velmoria.core.base import Skill, SkillRegistry, Unit
import cogs.velmoria.conditions as conditions
import cogs.velmoria.traits as traits


@SkillRegistry.register
class QuickMapping(Skill):
    def __init__(self, owner: Unit = None):
        super().__init__(
            name='Quick Mapping',
            description='Quickly scan your surroundings, and map important landmarks.\n'
                        'For 3 turns, all your allied units gain the **Survivalist** trait.',
            cost=3,
            owner=owner
        )

    async def use(self, target: Unit):
        await super().use(target)
        allies = self.owner.allies
        for ally in allies:
            if not any(isinstance(trait, traits.Survivalist) for trait in self.owner.traits):
                await ally.apply_condition(conditions.TemporaryTrait, traits.Survivalist, duration=3)
