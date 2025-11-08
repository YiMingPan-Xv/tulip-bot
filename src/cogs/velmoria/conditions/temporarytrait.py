from cogs.velmoria.core.base import Condition
import cogs.velmoria.core.events as events


class TemporaryTrait(Condition):
    def __init__(self, trait_cls, duration, owner=None):
        super().__init__(
            name=f"{trait_cls.__name__} (Temporary)",
            description=f"Grants the {trait_cls.__name__} trait temporarily.",
            owner=owner,
            duration=duration,
            is_negative=False
        )
        self.trait_cls = trait_cls
        self.trait_instance = None
        if owner:
            self.owner.event_bus.subscribe(events.TurnEndEvent, self.on_turn_end)
            self.trait_instance = self.trait_cls(owner=owner)

    async def on_turn_end(self, event):
        if event.unit is self.owner:
            self.duration -= 1
            if self.duration <= 0:
                await self.expire()

    async def expire(self):
        await self.owner.ctx.send(f"[CONDITION] {self.owner.name}'s {self.trait_cls.__name__} has worn off.")
        await self.owner.remove_condition(self)

    def unregister(self, bus=None):
        if self.trait_instance:
            self.trait_instance.unregister()
        if not bus:
            bus = self.owner.event_bus
        bus.unsubscribe(events.TurnEndEvent, self.on_turn_end)
