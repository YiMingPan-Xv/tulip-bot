class Event:
    pass


# UNIT BASED EVENTS

class DamageAboutToBeTakenEvent:
    def __init__(self, target, source, amount):
        self.target = target
        self.source = source
        self.amount = amount
        self.modified_amount = amount
        self.cancel = False


class DamageTakenEvent(Event):
    def __init__(self, target, source, amount):
        self.target = target
        self.source = source
        self.amount = amount


class DamageAboutToBeDealtEvent:
    def __init__(self, target, source, amount):
        self.target = target
        self.source = source
        self.amount = amount
        self.modified_amount = amount
        self.cancel = False


class DamageDealtEvent:
    def __init__(self, target, source, amount):
        self.target = target
        self.source = source
        self.amount = amount


class HealingAboutToBeTaken:
    def __init__(self, target, source, amount):
        self.target = target
        self.source = source
        self.amount = amount
        self.modified_amount = amount
        self.cancel = False


class HealingTakenEvent(Event):
    def __init__(self, target, source, amount):
        self.target = target
        self.source = source
        self.amount = amount


class ConditionAppliedEvent(Event):
    def __init__(self, target, condition):
        self.target = target
        self.condition = condition


class ConditionRemovedEvent(Event):
    def __init__(self, target, condition):
        self.target = target
        self.condition = condition


class SkillChargingEvent(Event):
    def __init__(self, source, skill):
        self.source = source
        self.skill = skill


class TurnStartEvent(Event):
    def __init__(self, unit):
        self.unit = unit


class TurnEndEvent(Event):
    def __init__(self, unit):
        self.unit = unit
