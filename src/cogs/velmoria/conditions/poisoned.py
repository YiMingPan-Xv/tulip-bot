import cogs.velmoria.core.events as events
from cogs.velmoria.core.base import Condition


class Poisoned(Condition):
    def __init__(self, duration, damage_per_turn, owner=None):
        super().__init__("Poisoned",
                         "Poisoned units take a fixed amount of damage at the end of their turn.",
                         owner,
                         duration,
                         True)
        self.damage_per_turn = damage_per_turn
        if owner:
            self.owner.event_bus.subscribe(events.TurnEndEvent, self.on_turn_end)

    async def on_turn_end(self, event):
        if not self.is_active or event.unit != self.owner:
            return
        self.owner.health[0] -= self.damage_per_turn
        await self.owner.ctx.send(f"[CONDITION] {self.owner.name} takes {self.damage_per_turn} poison damage!")
        self.duration -= 1
        if self.duration <= 0:
            await self.expire()

    async def expire(self):
        await self.owner.ctx.send(f"{self.owner.name} is no longer poisoned.")
        await self.owner.remove_condition(self)

    def unregister(self, bus=None):
        if not bus:
            bus = self.owner.event_bus
        bus.unsubscribe(events.TurnEndEvent, self.on_turn_end)
