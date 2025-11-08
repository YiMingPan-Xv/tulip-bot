from cogs.velmoria.core.base import Trait, TraitRegistry
import cogs.velmoria.core.events as events


@TraitRegistry.register
class ColdDemeanor(Trait):
    def __init__(self, owner=None):
        super().__init__(
            name="Cold Demeanor",
            description="The unit is distant and icy, reducing negative condition "
                        "duration by 1 turn if they have no other negative conditions.",
            owner=owner
        )
        if owner:
            self.owner.event_bus.subscribe(events.ConditionAppliedEvent, self.on_condition_applied)

    def unregister(self):
        self.owner.event_bus.unsubscribe(events.ConditionAppliedEvent, self.on_condition_applied)

    async def on_condition_applied(self, event):
        if event.target is self.owner:
            if event.condition.is_negative:
                event.condition.duration -= 1
