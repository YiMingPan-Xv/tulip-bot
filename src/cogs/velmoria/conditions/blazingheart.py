import cogs.velmoria.core.events as events
from cogs.velmoria.core.base import Condition


class BlazingHeart(Condition):
    def __init__(self, duration, owner=None):
        super().__init__(name="Blazing Heart",
                         description="Successful attacks deals an additional 4 damage.",
                         owner=owner,
                         duration=duration,
                         is_negative=False)
        if owner:
            self.owner.event_bus.subscribe(events.DamageDealtEvent, self.on_damage_dealt)
            self.owner.event_bus.subscribe(events.TurnEndEvent, self.on_turn_end)

    async def on_damage_dealt(self, event):
        if event.source is self.owner:
            if event.amount > 0:
                await event.target.take_damage(self.owner, 4)

    async def on_turn_end(self, event):
        if not self.is_active or event.unit != self.owner:
            return
        self.duration -= 1
        if self.duration <= 0:
            await self.expire()

    async def expire(self):
        self.owner.ctx.send(f"{self.owner.name}'s blazing heart calms down.")
        await self.owner.remove_condition(self)

    def unregister(self, bus=None):
        if not bus:
            bus = self.owner.event_bus
        bus.unsubscribe(events.DamageDealtEvent, self.on_damage_dealt)
        bus.unsubscribe(events.TurnEndEvent, self.on_turn_end)
