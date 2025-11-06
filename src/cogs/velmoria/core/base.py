class Unit:
    def __init__(self, name, health, speed, cost, skills=None, traits=None):
        self.name = name
        self.health = [health, health]  # Current health, Max health
        self.speed = [speed, speed]  # Current speed, Max speed
        self.cost = cost
        self.skills, self.traits = self._initialize_skills_and_traits(skills, traits)
        self.statuses = {}
        self.action_value = 0
        self.damage_mitigation = 0

    def _initialize_skills_and_traits(self, skills, traits):
        skill_instances = []
        trait_instances = []
        for skill in skills:
            skill_instances.append(SkillRegistry.create(skill))
        for trait in traits:
            trait_instances.append(TraitRegistry.create(trait))
        return skill_instances, trait_instances

    def apply_status(self, condition):
        if condition.name in self.statuses:
            existing = self.statuses[condition.name]
            existing.stacks += condition.stacks
            print(f"{self.name} gains {condition.stacks} stack(s) of {condition .name}. "
                  f"Now at {existing.stacks} stacks.")
        else:
            self.statuses[condition.name] = condition
            print(f"{self.name} gains {condition.stacks} stack(s) of {condition.name}.")

    def apply_traits(self, timing=""):
        for trait in self.traits:
            method = getattr(trait, timing, None)
            if callable(method):
                method(timing)
                print(f"{self.name}'s {trait.name} triggers!")

    def take_damage(self, dmg):
        self.apply_traits("about_to_take_damage")
        self.health[0] = max(self.health[0] - (dmg - self.damage_mitigation), 0)
        self.damage_mitigation = 0
        print(f"{self.name} takes {dmg} damage! ({self.health[0]} HP left)")

    def heal(self, heal):
        self.health[0] = min(self.health[0] + heal, self.health[1])
        print(f"{self.name} heals for {heal} health! ({self.health[0]} HP left)")

    def is_alive(self):
        return self.health[0] > 0

    def on_turn_end(self):
        to_remove = []
        for name, condition in self.statuses.items():
            condition.on_turn_end(self)
            if condition.stacks <= 0:
                to_remove.append(name)
        for name in to_remove:
            print(f"{self.name} is no longer {name}.")
            del self.statuses[name]


class Skill:
    def __init__(self, name, description="", cost=0):
        self.name = name
        self.description = description
        self.cost = cost

    def use(user, target):
        pass


class Trait:
    name = "Unnamed Trait"
    description = "Traits are treated like event listeners."

    def on_receive_condition(self, unit, condition):
        pass

    def on_action_end(self, unit):
        pass

    def on_turn_start(self, unit):
        pass

    def on_turn_end(self, unit):
        pass

    def about_to_receive_damage(self, unit, damage):
        pass

    def on_damage_received(self, unit, damage):
        pass

    def on_healing_received(self, unit, healing):
        pass

    def on_damage_dealt(self, unit, damage):
        pass

    def on_healing_dealt(self, unit, healing):
        pass


class Condition:
    def __init__(self, name="", description="", is_negative=False, stacks=1):
        self.name = name
        self.description = description
        self.is_negative = is_negative
        self.stacks = stacks

    def apply_effect(self, unit):
        pass

    def on_turn_end(self, unit):
        if self.stacks > 0:
            self.stacks -= 1


class SkillRegistry:
    """Registers and instantiates skills for better JSON compatibility."""
    _skills = {}

    @classmethod
    def register(cls, skill_cls):
        instance = skill_cls()
        cls._skills[instance.name] = skill_cls
        return skill_cls

    @classmethod
    def create(cls, name):
        try:
            return cls._skills[name]()
        except KeyError:
            raise KeyError(f"Skill '{name}' not found in SkillRegistry. "
                           f"Available: {list(cls._skills.keys())}")


class TraitRegistry:
    """Registers and instantiates traits for better JSON compatibility."""
    _traits = {}

    @classmethod
    def register(cls, trait_cls):
        instance = trait_cls()
        cls._traits[instance.name] = trait_cls
        return trait_cls

    @classmethod
    def create(cls, name):
        try:
            return cls._skills[name]()
        except KeyError:
            raise KeyError(f"Skill '{name}' not found in SkillRegistry. "
                           f"Available: {list(cls._skills.keys())}")
