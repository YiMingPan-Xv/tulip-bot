from cogs.velmoria.core.base import Skill, SkillRegistry, Unit
import cogs.velmoria.core.events as events


@SkillRegistry.register
class Strike(Skill):
    def __init__(self, owner: Unit = None):
        super().__init__(
            name='Strike',
            description='Strike at a unit with your bare hands.\n'
                        'Deals 50%% of your attack to a single target.',
            cost=0,
            owner=owner
        )

    async def use(self, target: Unit):
        await super().use(target)
        base_damage = self.owner.attack * 0.5
        event = events.DamageAboutToBeDealtEvent(target, self.owner, base_damage)
        await self.owner.event_bus.emit(event)
        final_damage = getattr(event, "modified_amount", base_damage)
        await target.take_damage(self.owner, round(final_damage))
        if final_damage > 0:
            await self.owner.event_bus.emit(events.DamageDealtEvent(target, self.owner, final_damage))
