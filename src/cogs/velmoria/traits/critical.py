import random

from cogs.velmoria.core.base import Trait, TraitRegistry
import cogs.velmoria.core.events as events


@TraitRegistry.register
class Critical(Trait):
    def __init__(self, owner=None):
        super().__init__(
            name="Critical",
            description="The unit strikes with exceptional precision and ferocity, turning well-placed hits into devastating blows.\n"
                        "**Critical** allows attacks to be critical hits (base chance 5%), dealing triple the damage.",
            owner=owner
        )
        self.critical_chance = 0.05
        if owner:
            self.owner.event_bus.subscribe(events.DamageAboutToBeTakenEvent, self.on_about_to_deal_damage)

    def unregister(self):
        self.bus.unsubscribe(events.DamageAboutToBeTakenEvent, self.on_about_to_deal_damage)

    async def on_about_to_deal_damage(self, event):
        if (event.source is self.owner and random.random() < self.critical_chance):
            event.modified_amount = event.amount * 3
            await self.owner.ctx.send(f"{self.owner.name} lands a critical hit!")
