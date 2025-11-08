from cogs.velmoria.core.base import Trait, TraitRegistry
import cogs.velmoria.core.events as events


@TraitRegistry.register
class Tough(Trait):
    def __init__(self, owner=None):
        super().__init__(
            name="Tough",
            description="The unit's thick skin protects them from weaker attacks.\n"
                        "**Tough** reduces damage by 2, if the damage is less than 5. The final damage cannot be less than 1.",
            owner=owner
        )
        if owner:
            self.owner.event_bus.subscribe(events.DamageAboutToBeTakenEvent, self.on_about_to_take_damage)

    def unregister(self):
        self.bus.unsubscribe(events.DamageAboutToBeTakenEvent, self.on_about_to_take_damage)

    async def on_about_to_take_damage(self, event):
        # only react if this trait’s unit is the target
        if event.target is not self.owner:
            return

        if event.amount < 5:
            event.modified_amount = max(1, event.amount - 2)
            await self.owner.ctx.send(f"{self.owner.name}'s Tough reduces damage from {event.amount} to {event.modified_amount}.")
