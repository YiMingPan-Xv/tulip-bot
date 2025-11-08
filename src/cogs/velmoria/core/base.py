import cogs.velmoria.core.events as events


ACTION_THRESHOLD = 1000


class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, listener):
        self.listeners.setdefault(event_type, []).append(listener)

    def unsubscribe(self, event_type, listener):
        if event_type in self.listeners:
            self.listeners[event_type].remove(listener)

    async def emit(self, event):
        for listener in self.listeners.get(type(event), []):
            await listener(event)


class Skill:
    def __init__(self, name, description="", cost=0, owner=None):
        self.name = name
        self.description = description
        self.cost = cost
        self.owner = owner

    async def use(self, target):
        await self.owner.ctx.send(f"{self.owner.name} uses {self.name}!")


class Trait:
    def __init__(self, name, description, owner):
        self.name = name
        self.description = description
        self.owner = owner

    async def register(self):
        pass


class Condition:
    def __init__(self, name, description, owner, duration, is_negative=False):
        self.name = name
        self.description = description
        self.owner = owner
        self.duration = duration
        self.is_negative = is_negative
        self.is_active = True


class SkillRegistry:
    _skills = {}

    @classmethod
    def register(cls, skill_cls):
        instance = skill_cls()
        cls._skills[instance.name] = skill_cls
        return skill_cls

    @classmethod
    def create(cls, name, owner):
        try:
            return cls._skills[name](owner)
        except KeyError:
            raise KeyError(f"Skill '{name}' not found in SkillRegistry. "
                           f"Available: {list(cls._skills.keys())}")


class TraitRegistry:
    _traits = {}

    @classmethod
    def register(cls, trait_cls):
        instance = trait_cls()
        cls._traits[instance.name] = trait_cls
        return trait_cls

    @classmethod
    def create(cls, name, owner):
        try:
            return cls._traits[name](owner)
        except KeyError:
            raise KeyError(f"Trait '{name}' not found in TraitRegistry. "
                           f"Available: {list(cls._traits.keys())}")


class Unit:
    def __init__(self,
                 name: str,
                 health: int,
                 attack: int,
                 speed: int,
                 cost: int,
                 skills: list,
                 traits: list,
                 event_bus: EventBus,
                 allies: list = None,
                 ctx=None
                 ):
        self.name = name
        self.health = [health, health]  # current, max
        self.base_attack = attack
        self.base_speed = speed
        self.modifiers = {
            "attack": [],
            "speed": []
        }
        self.cost = cost
        self.conditions = []
        self.event_bus = event_bus
        self.skills, self.traits = self._initialize_skills_and_traits(skills, traits)
        self.allies = allies if allies else [self]
        self.action_value = 0
        self.ctx = ctx

    @property
    def speed(self):
        total_mod = sum(value for _, value in self.modifiers["speed"])
        return self.base_speed + total_mod

    @property
    def attack(self):
        total_mod = sum(value for _, value in self.modifiers["attack"])
        return self.base_attack + total_mod

    def _initialize_skills_and_traits(self, skills, traits):
        skill_instances = []
        trait_instances = []
        for skill in skills:
            skill_instances.append(SkillRegistry.create(skill, self))
        for trait in traits:
            trait_instances.append(TraitRegistry.create(trait, self))
        return skill_instances, trait_instances

    def add_modifier(self, stat, source, value):
        self.modifiers.setdefault(stat, []).append((source, value))

    def remove_modifier(self, stat, source):
        self.modifiers[stat] = [
            (s, v) for (s, v) in self.modifiers[stat] if s != source
        ]

    async def take_damage(self, source, amount):
        pre_event = events.DamageAboutToBeTakenEvent(self, source, amount)
        await self.event_bus.emit(pre_event)

        if getattr(pre_event, "cancel", False):
            await self.ctx.send(f"{self.name} avoided the attack!")
            return

        final_damage = getattr(pre_event, "modified_amount", amount)
        self.health[0] -= final_damage
        await self.ctx.send(f"{self.name} took {final_damage} damage!")
        await self.event_bus.emit(events.DamageTakenEvent(self, source, amount))

    async def heal(self, source, amount):
        pre_event = events.HealingAboutToBeTaken(self, source, amount)
        self.event_bus.emit(pre_event)

        if getattr(pre_event, "cancel", False):
            await self.ctx.send(f"{self.name} can't get healed!")
            return

        final_healing = getattr(pre_event, "modified_amount", amount)
        self.health[0] = min(self.health[0] + final_healing, self.health[1])
        await self.ctx.send(f"{self.name} healed for {final_healing} health!")
        await self.event_bus.emit(events.HealingTakenEvent(self, source, amount))

    async def apply_condition(self, condition_class, *args, **kwargs):
        new_condition = condition_class(owner=self, *args, **kwargs)
        existing = next((cond for cond in self.conditions if isinstance(cond, condition_class)), None)
        if existing and hasattr(existing, "is_stackable"):
            existing.duration += new_condition.duration
        else:
            self.conditions.append(new_condition)
        await self.event_bus.emit(events.ConditionAppliedEvent(self, new_condition))

    async def remove_condition(self, condition):
        if condition in self.conditions:
            self.conditions.remove(condition)
            condition.active = False
            condition.unregister(self.event_bus)
            await self.event_bus.emit(events.ConditionRemovedEvent(self, condition))
            await self.ctx.send(f"{condition.__class__.__name__} removed from {self.name}.")

    async def end_turn(self):
        await self.event_bus.emit(events.TurnEndEvent(self))

    def is_alive(self):
        return self.health[0] > 0
