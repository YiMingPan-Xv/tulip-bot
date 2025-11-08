import logging
import aiosqlite
from pathlib import Path
import secrets
import asyncio
from PIL import Image, ImageDraw, ImageFont
import io
import random

import numpy as np
from discord import Embed, File, User
from discord.ext import commands
from discord.utils import get


logger = logging.getLogger("root")
root_path = Path(__file__).parents[2]
characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
database_path = str(root_path / "data" / "currency.db")


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = None
        self.bj_active_games = {}

    @commands.Cog.listener()
    async def on_ready(self):
        self.emoji = get(self.bot.emojis, name='flowers')
        async with aiosqlite.connect(database_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS currency (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER NOT NULL DEFAULT 0,
                    stolen INTEGER DEFAULT 0,
                    stolen_amount INTEGER DEFAULT 0
                )
            """)
            await db.commit()
            print("The database is correctly loaded!")

    # UTILITY
    @commands.command(  # FIXME
            aliases=['me'],
            help="If specified, this command shows the profile of a user. If the user is omitted, it shows your profile.",
            brief="Shows profile.")
    async def profile(self, ctx, user: User = None):
        if not user:
            user = ctx.author
        user_id = user.id
        balance = await read_currency(user_id)
        em = Embed(title="Net Worth", description=f"<@{user.id}>'s Profile", color=0x00aa00)
        em.add_field(name="Flowers", value=f"{balance}", inline=False)
        await ctx.send(embed=em)

    @commands.command(
            help="This command shows the profile of a user after deleting your command message.",
            brief="Silently shows a profile."
    )
    async def spy(self, ctx, user: User):
        await ctx.message.delete()
        user_id = user.id
        balance = await read_currency(user_id)
        em = Embed(title="Net Worth", description=f"<@{user.id}>'s Profile", color=0x00aa00)
        em.add_field(name="Flowers", value=f"{balance}", inline=False)
        await ctx.send(embed=em)

    @commands.command(
            aliases=['lb', 'top'],
            help="It displays all users in descending order based on the amount of flowers they have.",
            brief="Shows the leaderboard.")
    async def leaderboard(self, ctx):
        """Displays the top 10 users by flower count."""
        async with aiosqlite.connect(database_path) as db:
            async with db.execute("SELECT user_id, balance FROM currency") as cursor:
                rows = await cursor.fetchall()
                print(rows)

        sorted_rows = sorted(rows, key=lambda x: x[1], reverse=True)

        em = Embed(title=f"{self.emoji} Leaderboard", color=0xaaaa00)
        leaderboard_text = ""
        for i, (user_id, amount) in enumerate(sorted_rows[:10], start=1):
            leaderboard_text += f"**{i}.** <@{user_id}> --- {amount} flowers\n"

        em.description = leaderboard_text or "No data available yet!"
        await ctx.send(embed=em)

    @commands.command(
            help="It allows you to gift an amount of flowers to a user. Syntax: `give [user] [amount]`",
            brief="Gifts flowers to a user."
    )
    async def give(self, ctx, user: User, amount: int):
        if amount < 0:
            await ctx.send(f"You cannot gift negative {self.emoji} flowers!")
            return
        balance = await read_currency(ctx.author.id)

        if amount > balance:
            await ctx.send(f"You don't have enough {self.emoji} flowers to give!")
            return

        await update_balance(ctx.author.id, -amount)
        await update_balance(user.id, amount)

        await ctx.send(f"<@{ctx.author.id}> gifted {amount} {self.emoji} flowers to <@{user.id}>!")

    # EARN
    @commands.command(
            help="It grants you between 50 and 200 flowers.",
            brief="Gives you some flowers. "
    )
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def work(self, ctx):
        amount = np.random.randint(50, 200)
        balance = await read_currency(ctx.author.id)
        await update_balance(ctx.author.id, amount)
        await ctx.send(f"You collected {amount} {self.emoji} flowers!")
        await ctx.send(f"{ctx.author.mention}, you now have {balance + amount} {self.emoji} flowers.")

    # GAMBLING
    @commands.command(
            aliases=['bf'],
            help="Toss a coin, and bet on the result! Syntax: `betflip [h/t] [amount]`",
            brief="Bets on a coin flip.")
    async def betflip(self, ctx, bet: str, amount: int):
        if amount < 0:
            await ctx.send(f"You cannot bet negative {self.emoji} flowers!")
            return
        user_id = ctx.author.id
        balance = await read_currency(user_id)

        if bet not in ['h', 't']:
            await ctx.send(f"Results include 'h' and 't'! {bet} is invalid!")
            return

        if balance < amount:
            await ctx.send(f"You cannot bet more than what you have!\n"
                           f"You currently have {balance} {self.emoji} flowers!")
            return

        result = np.random.choice(['heads', 'tails'])
        await ctx.send(f"Result: {result}!")
        if bet == result[0]:
            final = round(amount)
            await update_balance(user_id, final)
            await ctx.send(f"You won! You gained {final} {self.emoji} flowers!")
        else:
            final = round(amount)
            await update_balance(user_id, -final)
            await ctx.send(f"You lose! You lost {final} {self.emoji} flowers!")

    @commands.command(
            help="Play a game of roulette! Syntax: `roulette [number/red/black/odd/even/high/low/first/second/third] [amount]`",
            brief="Bets on the roulette."
    )
    async def roulette(self, ctx, bet, amount: int):
        if amount < 0:
            await ctx.send(f"You cannot bet negative {self.emoji} flowers!")
            return
        user_id = ctx.author.id
        balance = await read_currency(user_id)
        allowed = ['red', 'black', 'odd', 'even', 'high', 'low', 'first', 'second', 'third']

        if balance < amount:
            await ctx.send(f"You cannot bet more than what you have!\n"
                           f"You currently have {balance} {self.emoji} flowers!")
            return

        if bet not in allowed:
            try:
                bet = int(bet)
                bet_payout = 35
            except ValueError:
                await ctx.send(f"You can only bet on a number, or on the following allowed types: \
                               {', '.join(allowed)}.")
                return
        else:  # Check which bet it is
            bet = bet.lower()
            if bet in ['first', 'second', 'third']:
                bet_payout = 2
            else:
                bet_payout = 1
        result = np.random.randint(0, 37)

        await ctx.send(file=File(str(root_path / 'assets' / 'roulette.png')))
        await ctx.send(f"Result: {result}!")

        if await _check_roulette_win(bet, result):
            final = amount * bet_payout
            await update_balance(user_id, final)
            await ctx.send(f"You won! You gained {final} {self.emoji} flowers!")
        else:
            await update_balance(user_id, -amount)
            await ctx.send(f"You lose! You lost {amount} {self.emoji} flowers!")

    @commands.command(
            help="Join the raffle: The winner takes it all!",
            brief="Starts a raffle."
    )
    async def rafflecur(self, ctx, amount: int):
        if amount < 0:
            await ctx.send(f"You cannot bet negative {self.emoji} flowers!")
            return
        user_id = ctx.author.id
        balance = await read_currency(user_id)

        if balance < amount:
            await ctx.send(f"You cannot raffle more than what you have!\n"
                           f"You currently have {balance} {self.emoji} flowers!")
            return

        await update_balance(balance, -amount)

        await ctx.send(f"{ctx.author.mention} has started a raffle with {amount} {self.emoji} flowers! "
                       f"React with 🎉 to join within 30 seconds!")

        participants = {ctx.author.id: amount}
        raffle_msg = await ctx.send("React below to join the raffle!")
        await raffle_msg.add_reaction("🎉")

        await asyncio.sleep(30)

        raffle_msg = await ctx.channel.fetch_message(raffle_msg.id)
        for reaction in raffle_msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if user.bot:
                        continue
                    participant_id = user.id
                    if participant_id not in participants:
                        participant_balance = await read_currency(participant_id)
                        if participant_balance >= amount:
                            await update_balance(participant_id, -amount)
                            participants[participant_id] = amount
                        else:
                            await ctx.send(f"{user.mention} does not have enough flowers to join!")

        if not participants:
            await ctx.send("No one joined the raffle. Flowers returned!")
            await update_balance(user_id, amount)
            return

        winner_id = np.random.choice(list(participants.keys()))
        total_flowers = sum(participants.values())

        await update_balance(winner_id, total_flowers)

        await ctx.send(f"Congratulations <@{winner_id}>! You won the raffle"
                       f"and received {total_flowers} {self.emoji} flowers!")

    @commands.command(
            aliases=['bj'],
            help="Play a game of blackjack!",
            brief="Bets on blackjack.")
    async def blackjack(self, ctx, amount: int):
        if amount < 0:
            await ctx.send(f"You cannot bet negative {self.emoji} flowers!")
            return
        user_id = ctx.author.id
        if user_id in self.bj_active_games:
            await ctx.send("You're already in a blackjack game!")
            return
        balance = await read_currency(user_id)

        if balance < amount:
            await ctx.send(f"You cannot bet more than what you have!\n"
                           f"You currently have {balance} {self.emoji} flowers!")
            return

        game = {
            "deck": [8, 8, 8, 8, 8, 8, 8, 8, 8, 32],
            "player_hand": [],
            "dealer_hand": [],
            "bet": amount
        }
        self.bj_active_games[user_id] = game

        # Draw a card from the player's deck
        def draw():
            card = random.choices([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], weights=game["deck"])[0]
            game["deck"][card-1] -= 1
            return card

        # Calculate hand value
        def hand_value(hand):
            total = sum(hand)
            aces = hand.count(1)
            while aces > 0 and total + 10 <= 21:
                total += 10
                aces -= 1
            return total

        def check(msg):
            return (
                msg.channel == ctx.channel
                and msg.author == ctx.author
                and msg.content.lower() in ['hit', 'stand']
            )

        game["player_hand"] = [draw(), draw()]
        game["dealer_hand"] = [draw(), draw()]

        await ctx.send(
            f"Your hand: {game['player_hand']} (Total: {hand_value(game['player_hand'])})\n"
            f"Dealer shows: [{game['dealer_hand'][0]}, ?]\n"
            f"Type `hit` or `stand`."
        )

        # Player turn: loop until player satisfied
        while True:
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send("You took too long. Dealer wins by default!")
                await update_balance(user_id, amount)
                del self.bj_active_games[user_id]
                return

            if msg.content.lower() == 'hit':
                game["player_hand"].append(draw())
                total = hand_value(game["player_hand"])
                await ctx.send(f"You drew a {game['player_hand'][-1]} — total: {total}")
                if total > 21:
                    await ctx.send("You busted! Dealer wins!")
                    await update_balance(user_id, -amount)
                    del self.bj_active_games[user_id]
                    return
            elif msg.content.lower() == 'stand':
                break

        # Dealer turn: hit until >= 17
        await ctx.send(f"Dealer reveals hand: {game['dealer_hand']} (Total: {hand_value(game['dealer_hand'])})")
        while hand_value(game["dealer_hand"]) < 17:
            game["dealer_hand"].append(draw())
            await asyncio.sleep(1)
            await ctx.send(f"Dealer draws a card... Total: {hand_value(game['dealer_hand'])}")

        dealer_total = hand_value(game["dealer_hand"])
        player_total = hand_value(game["player_hand"])

        # Determine winner
        result_msg = f"Your total: {player_total}\nDealer total: {dealer_total}\n"
        if dealer_total > 21 or player_total > dealer_total:
            result_msg += f"You win! You gained {amount} {self.emoji} flowers!"
            await update_balance(user_id, amount)
        elif player_total == dealer_total:
            result_msg += "It's a push! Nobody wins."
        else:
            result_msg += f"Dealer wins! You lost {amount} {self.emoji} flowers."
            await update_balance(user_id, -amount)

        await ctx.send(result_msg)
        del self.bj_active_games[user_id]

    # CHALLENGE
    @commands.command(
            help="Search flowers beyond the breach! Type in the password to claim flowers before the breach closes.",
            brief="Gives some flowers after typing a password."
    )
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def breach(self, ctx):
        amount = np.random.randint(250, 600)
        password = ''.join(secrets.choice(characters) for _ in range(8))
        img = Image.new("RGB", (400, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), password, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2
        draw.text((x, y), password, fill=(0, 0, 0), font=font)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        await ctx.send(
            f"Breaching through the vines and roots for **{amount} {self.emoji} flowers**!\n"
            f"Type the password shown in the image below:",
            file=File(fp=buffer, filename="password.png")
        )

        def check(msg):
            return (
                msg.channel == ctx.channel
                and not msg.author.bot
                and msg.content == password
            )

        try:
            winner_msg = await self.bot.wait_for("message", check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send("No one typed the password in time... The breach closes.")
            return

        winner = winner_msg.author
        user_id = winner.id
        await update_balance(user_id, amount)

        await ctx.send(
            f"{winner.mention} breached through the dangers, and earned {amount} {self.emoji} flowers!\n"
        )

    @commands.command(
            help="Steal flowers from a user! They won't know who it was unless they were already looking at the channel!",
            brief="Steals someone else's flowers."
    )
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def steal(self, ctx, user: User):
        await ctx.message.delete()
        stealer_id = ctx.author.id
        victim_id = user.id
        victim_balance = await read_currency(victim_id)

        amount = int((np.random.randint(25, 50) / 100) * victim_balance)

        await update_balance(victim_id, -amount)
        await update_steal_data(victim_id, stealer_id, amount)
        await update_balance(stealer_id, amount)

        await ctx.send(f"Someone stole from you <@{victim_id}>! You lost {amount} {self.emoji} flowers!")
        await ctx.send("You can use `!accuse` to accuse who you think it was! You only have one chance at it.")

    @commands.command(
            help="Use this command to accuse someone of stealing from you! If you guess correctly, you get some flowers from the stealer!",
            brief="Accuses someone of stealing."
    )
    async def accuse(self, ctx, user: User):
        accuser_id = ctx.author.id
        accused_id = user.id
        culprit_id, stolen_amount = await read_steal_data(accuser_id)

        if culprit_id == 0:
            await ctx.send("No one did anything to you yet! You cannot accuse someone!")
            return

        if culprit_id == accused_id:
            reward = int(stolen_amount * 1.3)

            await update_balance(accuser_id, reward)
            await update_balance(accused_id, -reward)

            await ctx.send(f"You correctly accused <@{accused_id}>! "
                           f"You got {reward} {self.emoji} flowers out of the case!")
        else:
            await ctx.send(f"You accused the wrong person! <@{accused_id}> was innocent!")

        await update_steal_data(accuser_id, 0, 0)


async def _check_roulette_win(bet, result):
    if isinstance(bet, int):
        return bet == result

    if result == 0:
        return False

    red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    black = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    if (
        (bet == 'red' and result in red) or
        (bet == 'black' and result in black) or
        (bet == 'odd' and result % 2 == 1) or
        (bet == 'even' and result % 2 == 0) or
        (bet == 'high' and result > 18) or
        (bet == 'low' and result <= 18) or
        (bet == 'first' and result <= 12) or
        (bet == 'second' and 13 <= result <= 24) or
        (bet == 'third' and 25 <= result <= 36)
    ):
        return True

    else:
        return False


async def read_currency(user_id):
    async with aiosqlite.connect(database_path) as db:
        async with db.execute("SELECT balance FROM currency WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def read_steal_data(user_id):
    async with aiosqlite.connect(database_path) as db:
        async with db.execute("SELECT stolen, stolen_amount FROM currency WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0, 0


async def update_balance(user_id, delta):
    async with aiosqlite.connect(database_path) as db:
        await db.execute("""
            INSERT INTO currency (user_id, balance)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET balance = balance + excluded.balance
        """, (user_id, delta))
        await db.commit()


async def update_steal_data(user_id, stealer_id, steal_amount):
    async with aiosqlite.connect(database_path) as db:
        await db.execute("""
            INSERT INTO currency (user_id, stolen, stolen_amount)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id)
                DO UPDATE SET stolen = excluded.stolen, stolen_amount = excluded.stolen_amount
        """, (user_id, stealer_id, steal_amount))
        await db.commit()


async def setup(bot):
    await bot.add_cog(Currency(bot))
