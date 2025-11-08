from cogs.velmoria.core.base import Skill, SkillRegistry, Unit
import cogs.velmoria.core.events as events


@SkillRegistry.register
class ARTBlazingHeart(Skill):
    def __init__(self, owner: Unit = None):
        super().__init__(
            name='ART: Searing Fury',
            description='Manifest your mindscape in a blind surge of rage, channeled in a relentless flurry of punches.\n'
                        'Deals 50%% of your Attack to up to 5 designated targets. Targets can be chosen multiple times.',
            cost=2,
            owner=owner
        )

    async def use(self, target: Unit):
        # TODO: Multitarget
        for i in range(5):
            await self.hit(target)

    async def hit(self, target: Unit):
        base_damage = self.owner.attack * 0.5
        event = events.DamageAboutToBeDealtEvent(target, self.owner, base_damage)
        await self.owner.event_bus.emit(event)
        final_damage = getattr(event, "modified_amount", base_damage)
        await target.take_damage(self.owner, round(final_damage))
        if final_damage > 0:
            await self.owner.event_bus.emit(events.DamageDealtEvent(target, self.owner, final_damage))
