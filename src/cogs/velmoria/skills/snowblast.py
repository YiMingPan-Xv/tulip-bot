from cogs.velmoria.core.base import Skill, SkillRegistry, Unit
import cogs.velmoria.core.events as events
import cogs.velmoria.conditions as conditions


@SkillRegistry.register
class SnowBlast(Skill):
    def __init__(self, owner: Unit = None):
        super().__init__(
            name='Snow Blast',
            description='Shoot a ray of frost at the enemy, making snowflakes around the target explode to deal additional damage.\n\n'
                        'Deals 150%% of your attack to a single target.\n'
                        'Per every stack of cold, deal an additional instance of damage equal to 75%% of your attack.',
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
        cold = next((cond for cond in target.conditions if isinstance(cond, conditions.Cold)), None)
        if cold:
            for _ in range(cold.duration):
                await self.snowburst(target)

    async def snowburst(self, target: Unit):
        base_damage = self.owner.attack * 0.75
        event = events.DamageAboutToBeDealtEvent(target, self.owner, base_damage)
        await self.owner.event_bus.emit(event)
        final_damage = getattr(event, "modified_amount", base_damage)
        await target.take_damage(self.owner, round(final_damage))
        if final_damage > 0:
            await self.owner.event_bus.emit(events.DamageDealtEvent(target, self.owner, final_damage))
