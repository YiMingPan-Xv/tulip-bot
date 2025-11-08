import random
import asyncio

from discord.ext import commands

from cogs.velmoria.utils.auto_import import import_submodules
from cogs.velmoria.utils.load_unit import load
from cogs.velmoria.core.base import Unit, EventBus, ACTION_THRESHOLD


import_submodules("cogs.velmoria.traits")
import_submodules("cogs.velmoria.skills")


class Velmoria(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def starter(self, ctx, index: int = 0):
        if not index:
            await ctx.send("Welcome to Velmoria: The last deal!\n"
                           "This is a text-based, ATB-card hybrid game. Here, units will fight each others for victory, as you and your "
                           "opponent will supply them with power-ups and support cards.\n"
                           "...But this feature is still WIP, you can test the combat with `testvelmoria` or `tv`.")

    @commands.command(aliases=['tv'])
    async def testvelmoria(self, ctx):
        bus = EventBus()
        unit_name = random.choice(["Elena Frost", "Amber Hyland"])
        player = load(unit_name, bus, ctx)
        await ctx.send(f"Testing unit: {unit_name}")
        dummy_enemy = Unit(
            name="Dummy",
            health=50,
            attack=4,
            speed=30,
            cost=1,
            skills=["Strike"],
            traits=[],
            event_bus=bus,
            ctx=ctx
        )

        await self.update([player], [dummy_enemy], ctx)

    async def update(self, units1, units2, ctx):
        try:
            # Initialize action values. This determines the units' action order
            all_units = units1 + units2
            for u in all_units:
                u.action_value = ACTION_THRESHOLD / u.speed

            # Main loop
            while units1 and units2:
                acting_unit = min(all_units, key=lambda u: u.action_value)
                current_av = acting_unit.action_value

                for u in all_units:
                    u.action_value -= current_av

                await show_turn_order(all_units, 5, ctx)

                if acting_unit in units1:
                    await self.player_turn(acting_unit, units1, units2, ctx)
                elif acting_unit in units2:
                    await self.ai_turn(acting_unit, units2, units1, ctx)

                acting_unit.action_value = ACTION_THRESHOLD / acting_unit.speed

                await check_death(units1, units2)
                all_units = units1 + units2

            if units1:
                await ctx.send("Victory! You won!")
            else:
                await ctx.send("Defeat! You lost!")
        except Exception as e:
            print(e)

    async def player_turn(self, unit, allies, enemies, ctx):
        def check(msg):
            return (
                msg.channel == ctx.channel
                and msg.author == ctx.author
                and msg.content.lower() in [str(i) for i in range(0, 10)]
            )
        print(f"It's {unit.name}'s turn!")
        await ctx.send(f"Make a move:\n{"\n".join([f"{i+1}. {unit.skills[i].name}" for i in range(len(unit.skills))])}\n")
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            move = int(msg.content) - 1
        except asyncio.TimeoutError:
            await ctx.send("You took too long. Your opponent wins by default!")
            return
        await ctx.send(f"To who?\n{"\n".join([f"{i+1}. {enemies[i].name}" for i in range(len(enemies))])}\n")
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            target = int(msg.content) - 1
        except asyncio.TimeoutError:
            await ctx.send("You took too long. Your opponent wins by default!")
            return
        await unit.skills[move].use(enemies[target])
        await unit.end_turn()

    async def ai_turn(self, unit, allies, enemies, ctx):
        await ctx.send(f"It's your opponent's {unit.name}'s turn!")
        skill = random.choice(unit.skills)
        await ctx.send(f"{unit.name} uses {skill.name}!")
        target = random.choice(enemies)
        await skill.use(target)
        await unit.end_turn()


async def show_turn_order(units, n, ctx):
    """
    Show the upcoming n actions with prediction of placement after acting.
    """
    # Copy current action values to avoid modifying the actual units
    timeline = sorted([(u, u.action_value) for u in units], key=lambda x: x[1])
    current = (timeline[0][0], (ACTION_THRESHOLD / timeline[0][0].speed))

    await ctx.send("Upcoming Turns:")
    predicted = False
    for turn in timeline:
        if current[1] < turn[1] and not predicted:
            predicted = True
            await ctx.send(f"\t{current[0].name} [{int(current[1])}]")
        await ctx.send(f"{turn[0].name} [{int(turn[1])}]")


async def check_death(units1, units2):
    units1[:] = [u for u in units1 if u.is_alive()]
    units2[:] = [u for u in units2 if u.is_alive()]


async def setup(bot):
    await bot.add_cog(Velmoria(bot))
