import time
import random


ACTION_GAUGE = 1000


def update(units1, units2):
    # Initialize action values. This determines the units' action order
    all_units = units1 + units2
    for u in all_units:
        u.action_value = ACTION_GAUGE / u.speed[0]

    # Main loop
    while units1 and units2:
        acting_unit = min(all_units, key=lambda u: u.action_value)
        current_av = acting_unit.action_value

        for u in all_units:
            u.action_value -= current_av

        show_turn_order(all_units)

        if acting_unit in units1:
            player_turn(acting_unit, units1, units2)
        elif acting_unit in units2:
            ai_turn(acting_unit, units2, units1)

        acting_unit.action_value = ACTION_GAUGE / acting_unit.speed[0]

        check_death(units1, units2)
        all_units = units1 + units2

    if units1:
        print("Victory! You won!")
    else:
        print("Defeat! You lost!")


def show_turn_order(units, n=5):
    """
    Show the upcoming n actions with prediction of placement after acting.
    """
    # Copy current action values to avoid modifying the actual units
    timeline = sorted([(u, u.action_value) for u in units], key=lambda x: x[1])
    current = (timeline[0][0], (ACTION_GAUGE / timeline[0][0].speed[0]))

    print("Upcoming Turns:")
    predicted = False
    for turn in timeline:
        if current[1] < turn[1] and not predicted:
            predicted = True
            print(f"\t{current[0].name} [{int(current[1])}]")
        print(f"{turn[0].name} [{int(turn[1])}]")


def player_turn(unit, allies, enemies):
    print(f"It's {unit.name}'s turn!")
    move = input(f"Make a move:\n{"\n".join([f"{i+1}. {unit.skills[i].name}" for i in range(len(unit.skills))])}\n")
    move = int(move) - 1
    target = input(f"To who?\n{"\n".join([f"{i+1}. {enemies[i].name}" for i in range(len(enemies))])}\n")
    target = int(target) - 1
    unit.skills[move].use(unit, enemies[target])
    unit.on_turn_end()


def ai_turn(unit, allies, enemies):
    print(f"It's your opponent's {unit.name}'s turn!")
    time.sleep(1)
    skill = random.choice(unit.skills)
    print(f"{unit.name} uses {skill.name}!")
    target = random.choice(enemies)
    skill.use(unit, target)
    unit.on_turn_end()
    input()


def check_death(units1, units2):
    units1[:] = [u for u in units1 if u.is_alive()]
    units2[:] = [u for u in units2 if u.is_alive()]
