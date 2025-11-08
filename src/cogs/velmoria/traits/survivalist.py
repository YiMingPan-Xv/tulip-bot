from cogs.velmoria.core.base import Trait, TraitRegistry
import cogs.velmoria.core.events as events


@TraitRegistry.register
class Survivalist(Trait):
    def __init__(self, owner=None):
        super().__init__(
            name="Survivalist",
            description="The unit can handle extreme conditions and unexpected hitches.\n"
                        "When receiving a negative condition, heal by 2 Health.",
            owner=owner
        )
        if owner:
            self.owner.event_bus.subscribe(events.ConditionAppliedEvent, self.on_condition_applied)

    def unregister(self):
        self.owner.event_bus.unsubscribe(events.ConditionAppliedEvent, self.on_condition_applied)

    async def on_condition_applied(self, event):
        if event.target is self.owner:
            if event.condition.is_negative:
                await self.owner.heal(self.owner, 2)
