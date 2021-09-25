"""This file is used by GodBot() to handle messages and commands from users"""


from typing import Union

from discord.ext import commands, tasks
from GodBot.player_class import Player
from GodBot.rpg_exceptions import NotEnoughMoney, TooLowInvestment, NoShip
from GodBot.parser_grammars import GRAMMAR_COMMAND_INITPLAYER, GRAMMAR_COMMAND_SEND
from GodBot.parser_grammars import GRAMMAR_COMMAND_BUILDSHIP, GRAMMAR_COMMAND_ATTACK
from GodBot.parser_functions import parse_grammar
from GodBot.rpg_functions import fight_simulator


def is_player_initialized(function):
    """Decorator that check if player is initialized or not,
    if not, function is not called and print error"""
    async def new_function(self, ctx):
        if str(ctx.message.author) in self.players:
            await function(self, ctx)
        else:
            msg = f"Player '{ctx.message.author}' not initialized, please use !initPlayer \"race\""
            await ctx.message.channel.send(msg)
    new_function.__doc__ = function.__doc__
    return new_function


class RpgCommands(commands.Cog):

    """This class is used by GodBot() to handle RPG commands from users"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players = {}
        # load players from DB

    @tasks.loop(seconds=8)
    async def eight_sec_loop(self):
        "looping every 8 seconds"
        for _, player in self.players.items():
            player.periodic_money()

    @tasks.loop(minutes=5)
    async def five_min_loop(self):
        "looping every 5 minutes"
        for _, player in self.players.items():
            player.luck()
        self.save_in_db_rpg()

    @commands.Cog.listener()
    async def on_ready(self):
        "starts time_loop() functions"
        # pylint: disable=no-member
        self.eight_sec_loop.start()
        self.five_min_loop.start()

    def save_in_db_rpg(self):
        "save everything related to the RPG inside the RDS DB"

    @commands.command("initPlayer")
    @parse_grammar(grammar=GRAMMAR_COMMAND_INITPLAYER)
    async def init_player(self, ctx, player_race: str):
        "!initPlayer \"race\": Initialize yourself"
        if str(ctx.message.author) not in self.players:
            self.players[str(ctx.message.author)] = Player(
                str(ctx.message.author), player_race)
        else:
            await ctx.message.channel.send(f"{ctx.message.author} already initialized.")

    @commands.command("showMe")
    @is_player_initialized
    async def show_me(self, ctx):
        "!showMe: Show all informations about yourself"
        await ctx.message.channel.send(self.players[str(ctx.message.author)].get_infos())

    @commands.command("buildShip")
    @is_player_initialized
    @parse_grammar(grammar=GRAMMAR_COMMAND_BUILDSHIP)
    async def build_ship(
        self, ctx, ship_name: str, ship_aoe: int, ship_tankiness: int, investment: int):
        """
        !buildShip name nb_targets tankiness investment: Use money to build a ship
        """
        try:
            self.players[str(ctx.message.author)].create_ship(
                ship_name, ship_aoe, ship_tankiness, investment)
            await ctx.message.channel.send(f"{ship_name} created !")
        except TooLowInvestment:
            await ctx.message.channel.send("Minimum investment: 50")
        except NotEnoughMoney:
            await ctx.message.channel.send("Not enough money")

    @commands.command("attack")
    @is_player_initialized
    @parse_grammar(grammar=GRAMMAR_COMMAND_ATTACK)
    async def attack(self, ctx, other_player: str):
        "!attack other_player: Fight against another player"
        if (other_player in self.players and other_player != str(ctx.message.author)):
            fight_msg = fight_simulator(
                self.players[str(ctx.message.author)], self.players[other_player])
            await ctx.message.channel.send(fight_msg)
        else:
            await ctx.message.channel.send("You can't fight against yourself !")

    async def send_money(self, ctx, other_player: str, amount: int):
        "Send money from the !give command"
        try:
            self.players[str(ctx.message.author)].send_money(
                self.players[other_player], amount)
        except NotEnoughMoney:
            await ctx.message.channel.send("Not enough money")

    async def send_ship(self, ctx, other_player: str, ship_name: str):
        "Send ship from the !give command"
        try:
            self.players[str(ctx.message.author)].send_ship(
                self.players[other_player], ship_name)
        except NoShip:
            await ctx.message.channel.send("Ship name does not exist")

    @commands.command("send")
    @is_player_initialized
    @parse_grammar(grammar=GRAMMAR_COMMAND_SEND)
    async def give(self, ctx, other_player: str, action: str, action_parameter: Union[str, int]):
        """Send money or ship to another player
        example1: !send "playername" money 300
        example2: !send "playername" ship "shipname"
        """
        if other_player in self.players:
            if action == "money":
                await self.send_money(ctx, other_player, int(action_parameter))
            else:
                await self.send_ship(ctx, other_player, action_parameter)
        else:
            await ctx.message.channel.send("Targeted player does not exist.")

    @commands.command("save")
    async def save(self, ctx):
        """Save the game, an auto save is done every 5 minutes"""
        self.save_in_db_rpg()
        await ctx.message.channel.send("Game saved")

    @commands.command("players")
    async def players_cmd(self, ctx):
        """List all players"""
        msg = "```"
        for player_name, player in self.players.items():
            msg += f'''{player_name}: level {player.level} | '''
            msg += f'''army power: {player.army_power} | money: {player.money}\n'''
        msg += "```"
        await ctx.message.channel.send(msg)
