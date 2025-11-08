from cogs.velmoria.core.base import Skill, SkillRegistry, Unit
import cogs.velmoria.core.events as events
import cogs.velmoria.conditions as conditions


@SkillRegistry.register
class Frostbite(Skill):
    def __init__(self, owner: Unit = None):
        super().__init__(
            name='Frostbite',
            description='Hurl a sphere of cold winds that freezes the enemy from within.\n'
                        'Deals 150%% of your attack to a single target, and inflicts 3 stack of **Cold**.',
            cost=3,
            owner=owner
        )

    async def use(self, target: Unit):
        await super().use(target)
        base_damage = self.owner.attack * 1.5
        event = events.DamageAboutToBeDealtEvent(target, self.owner, base_damage)
        await self.owner.event_bus.emit(event)
        final_damage = getattr(event, "modified_amount", base_damage)
        await target.take_damage(self.owner, round(final_damage))
        if final_damage > 0:
            await self.owner.event_bus.emit(events.DamageDealtEvent(target, self.owner, final_damage))
            await target.apply_condition(conditions.Cold, duration=3)
