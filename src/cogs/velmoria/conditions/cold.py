import cogs.velmoria.core.events as events
from cogs.velmoria.core.base import Condition


class Cold(Condition):
    def __init__(self, owner, duration):
        super().__init__(
            name="Cold",
            description="Affected units have their speed reduced by 3 per stack of **Cold**.\n"
                        "They lose one stack at the end of their turn.",
            duration=duration,
            owner=owner,
            is_negative=True
        )
        self.is_stackable = True
        if owner:
            self.owner.event_bus.subscribe(events.TurnEndEvent, self.on_turn_end)

        self.apply_effect()

    def apply_effect(self):
        self.owner.remove_modifier("speed", self)  # clear old one if reapplying
        self.owner.add_modifier("speed", self, -3 * self.duration)

    async def on_turn_end(self, event):
        if event.unit is self.owner:
            self.duration -= 1
            if self.duration <= 0:
                self.owner.remove_modifier("speed", self)
                await self.owner.remove_condition(self)
            else:
                self.apply_effect()

    def unregister(self, bus=None):
        if not bus:
            bus = self.owner.event_bus
        bus.unsubscribe(events.TurnEndEvent, self.on_turn_end)
