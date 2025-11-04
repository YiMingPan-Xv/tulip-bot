import logging
import json
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


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = None
        self.active_games = {}

    @commands.Cog.listener()
    async def on_ready(self):
        self.emoji = get(self.bot.emojis, name='flowers')

    # UTILITY
    @commands.command(
            aliases=['me'],
            help="If specified, this command shows the profile of a user. If the user is omitted, it shows your profile.",
            brief="Shows profile.")
    async def profile(self, ctx, user: User = None):
        if not user:
            user = ctx.author
        userid = str(user.id)
        file = await read_currency(userid)
        em = Embed(title="Net Worth", description=f"<@{user.id}>'s Profile", color=0x00aa00)
        em.add_field(name="Flowers", value=f"{file[userid]['flowers']}", inline=False)
        await ctx.send(embed=em)

    @commands.command(
            help="This command shows the profile of a user after deleting your command message.",
            brief="Silently shows a profile."
    )
    async def spy(self, ctx, user: User):
        await ctx.message.delete()
        userid = str(user.id)
        file = await read_currency(userid)
        em = Embed(title="Net Worth", description=f"<@{user.id}>'s Profile", color=0x00aa00)
        em.add_field(name="Flowers", value=f"{file[userid]['flowers']}", inline=False)
        await ctx.send(embed=em)

    @commands.command(
            aliases=['lb', 'top'],
            help="It displays all users in descending order based on the amount of flowers they have.",
            brief="Shows the leaderboard.")
    async def leaderboard(self, ctx):
        """Displays the top 10 users by flower count."""
        data = await read_currency(str(ctx.author.id))

        sorted_data = sorted(data.items(), key=lambda x: x[1]['flowers'], reverse=True)

        em = Embed(title=f"{self.emoji} Leaderboard", color=0xaaaa00)
        leaderboard_text = ""
        for i, (userid, info) in enumerate(sorted_data[:10], start=1):
            user = await ctx.bot.fetch_user(int(userid))
            leaderboard_text += f"**{i}.** {user.mention} --- {info['flowers']} flowers\n"

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
        authorid = str(ctx.author.id)
        userid = str(user.id)
        file = await read_currency(authorid)

        if amount > file[authorid]['flowers']:
            await ctx.send(f"You don't have enough {self.emoji} flowers to give!")
            return

        file[authorid]['flowers'] -= amount
        file[userid]['flowers'] += amount

        await ctx.send(f"<@{authorid}> gifted {amount} {self.emoji} flowers to <@{userid}>!")

        await write_currency(file)

    # EARN
    @commands.command(
            help="It grants you between 50 and 200 flowers.",
            brief="Gives you some flowers. "
    )
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def work(self, ctx):
        amount = np.random.randint(50, 200)
        userid = str(ctx.author.id)
        file = await read_currency(userid)
        file[userid]['flowers'] += amount
        await ctx.send(f"You collected {amount} {self.emoji} flowers!")
        await ctx.send(f"{ctx.author.mention}, you now have {file[userid]['flowers']} {self.emoji} flowers.")
        await write_currency(file)

    # GAMBLING
    @commands.command(
            aliases=['bf'],
            help="Toss a coin, and bet on the result! Syntax: `betflip [h/t] [amount]`",
            brief="Bets on a coin flip.")
    async def betflip(self, ctx, bet: str, amount: int):
        if amount < 0:
            await ctx.send(f"You cannot bet negative {self.emoji} flowers!")
            return
        userid = str(ctx.author.id)
        file = await read_currency(userid)
        win_mul = 1
        lose_mul = 1

        if bet not in ['h', 't']:
            await ctx.send(f"Results include 'h' and 't'! {bet} is invalid!")
            return

        if file[userid]['flowers'] < amount:
            await ctx.send(f"You cannot bet more than what you have!\n"
                           f"You currently have {file[userid]['flowers']} {self.emoji} flowers!")
            return

        result = np.random.choice(['heads', 'tails'])
        await ctx.send(f"Result: {result}!")
        if bet == result[0]:
            final = round(amount * win_mul)
            file[userid]['flowers'] += final
            await ctx.send(f"You won! You gained {final} {self.emoji} flowers!")
        else:
            final = round(amount * lose_mul)
            file[userid]['flowers'] -= final
            await ctx.send(f"You lose! You lost {final} {self.emoji} flowers!")

        await write_currency(file)

    @commands.command(
            help="Play a game of roulette! Syntax: `roulette [number/red/black/odd/even/high/low/first/second/third] [amount]`"
    )
    async def roulette(self, ctx, bet, amount: int):
        if amount < 0:
            await ctx.send(f"You cannot bet negative {self.emoji} flowers!")
            return
        userid = str(ctx.author.id)
        file = await read_currency(userid)
        allowed = ['red', 'black', 'odd', 'even', 'high', 'low', 'first', 'second', 'third']

        if file[userid]['flowers'] < amount:
            await ctx.send(f"You cannot bet more than what you have!\n"
                           f"You currently have {file[userid]['flowers']} {self.emoji} flowers!")
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
            file[userid]['flowers'] += final
            await ctx.send(f"You won! You gained {final} {self.emoji} flowers!")
        else:
            file[userid]['flowers'] -= amount
            await ctx.send(f"You lose! You lost {amount} {self.emoji} flowers!")

        await write_currency(file)

    @commands.command()
    async def rafflecur(self, ctx, amount: int):
        if amount < 0:
            await ctx.send(f"You cannot bet negative {self.emoji} flowers!")
            return
        userid = str(ctx.author.id)
        file = await read_currency(userid)

        if file[userid]['flowers'] < amount:
            await ctx.send(f"You cannot raffle more than what you have!\n"
                           f"You currently have {file[userid]['flowers']} {self.emoji} flowers!")
            return

        file[userid]['flowers'] -= amount
        await write_currency(file)

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
                    userid = str(user.id)
                    if userid not in participants:
                        user_file = await read_currency(userid)
                        if user_file[userid]['flowers'] >= amount:
                            user_file[userid]['flowers'] -= amount
                            await write_currency(user_file)
                            participants[userid] = amount
                        else:
                            await ctx.send(f"{user.mention} does not have enough flowers to join!")

        if not participants:
            await ctx.send("No one joined the raffle. Flowers returned!")
            file[userid]['flowers'] += amount
            await write_currency(file)
            return

        winner_id = np.random.choice(list(participants.keys()))
        total_flowers = sum(participants.values())

        winner_file = await read_currency(str(winner_id))
        winner_file[str(winner_id)]['flowers'] += total_flowers
        await write_currency(winner_file)

        await ctx.send(f"Congratulations <@{winner_id}>! You won the raffle"
                       f"and received {total_flowers} {self.emoji} flowers!")

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx, amount: int):
        if amount < 0:
            await ctx.send(f"You cannot bet negative {self.emoji} flowers!")
            return
        userid = str(ctx.author.id)
        if userid in self.active_games:
            await ctx.send("You're already in a blackjack game!")
            return
        file = await read_currency(userid)

        if file[userid]['flowers'] < amount:
            await ctx.send(f"You cannot bet more than what you have!\n"
                           f"You currently have {file[userid]['flowers']} {self.emoji} flowers!")
            return

        game = {
            "deck": [8, 8, 8, 8, 8, 8, 8, 8, 8, 32],
            "player_hand": [],
            "dealer_hand": [],
            "bet": amount
        }
        self.active_games[userid] = game

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
                file[userid]['flowers'] -= amount
                await write_currency(file)
                del self.active_games[userid]
                return

            if msg.content.lower() == 'hit':
                game["player_hand"].append(draw())
                total = hand_value(game["player_hand"])
                await ctx.send(f"You drew a {game['player_hand'][-1]} — total: {total}")
                if total > 21:
                    await ctx.send("You busted! Dealer wins!")
                    file[userid]['flowers'] -= amount
                    await write_currency(file)
                    del self.active_games[userid]
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
            file[userid]['flowers'] += amount
        elif player_total == dealer_total:
            result_msg += "It's a push! Nobody wins."
        else:
            result_msg += f"Dealer wins! You lost {amount} {self.emoji} flowers."
            file[userid]['flowers'] -= amount

        await ctx.send(result_msg)
        await write_currency(file)
        del self.active_games[userid]

    # CHALLENGE
    @commands.command()
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
        userid = str(winner.id)
        file = await read_currency(userid)
        file[userid]['flowers'] += amount

        await ctx.send(
            f"{winner.mention} breached through the dangers, and earned {amount} {self.emoji} flowers!\n"
        )
        await write_currency(file)

    @commands.command()
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def steal(self, ctx, user: User):
        await ctx.message.delete()
        stealerid = str(ctx.author.id)
        victimid = str(user.id)
        file = await read_currency(victimid)

        amount = int((np.random.randint(25, 75) / 100) * file[victimid]['flowers'])

        file[victimid]['flowers'] -= amount
        file[victimid]['stolen'][0] = stealerid
        file[victimid]['stolen'][1] = amount
        file[stealerid]['flowers'] += amount

        await ctx.send(f"Someone stole from you <@{victimid}>! You lost {amount} {self.emoji} flowers!")
        await ctx.send("You can use `!accuse` to accuse who you think it was! You only have one chance at it.")
        await write_currency(file)

    @commands.command()
    async def accuse(self, ctx, user: User):
        accuserid = str(ctx.author.id)
        accusedid = str(user.id)
        file = await read_currency(accuserid)

        if file[accuserid]['stolen'][0] is None:
            await ctx.send("No one did anything to you yet! You cannot accuse someone!")
            return

        if file[accuserid]['stolen'][0] == accusedid:
            reward = int(file[accuserid]['stolen'][1] * 1.3)
            file[accuserid]['flowers'] += reward
            file[accusedid]['flowers'] -= reward
            await ctx.send(f"You correctly accused <@{accusedid}>! "
                           f"You got {reward} {self.emoji} flowers out of the case!")
        else:
            await ctx.send(f"You accused the wrong person! <@{accusedid}> was innocent!")

        file[accuserid]['stolen'] = [None, 0]

        await write_currency(file)


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


async def _update_user(file, userid):
    if userid not in file:
        file[userid] = {}

    file_path = root_path / "data" / "currency_template.json"
    with open(file_path, "r") as f:
        template = json.load(f)
    for key, value in template.items():
        if key not in file[userid]:
            file[userid][key] = value
    return file


async def read_currency(userid):
    file_path = root_path / "data" / "currency.json"
    with open(file_path, "r") as f:
        file = json.load(f)
    file = await _update_user(file, userid)
    logging.debug(f"Loaded JSON file: {file}")
    return file


async def write_currency(file):
    file_path = root_path / "data" / "currency.json"
    with open(file_path, "w") as f:
        json.dump(file, f)


async def setup(bot):
    await bot.add_cog(Currency(bot))
