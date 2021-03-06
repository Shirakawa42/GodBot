"""This file is used by GodBot() to handle messages and commands from users"""


from typing import Union

from discord.ext import commands, tasks
from GodBot.player_class import Player
from GodBot.exceptions import NotEnoughMoney, TooLowInvestment, NoShip
from GodBot.parser_grammars import GRAMMAR_COMMAND_INITPLAYER, GRAMMAR_COMMAND_SEND
from GodBot.parser_grammars import GRAMMAR_COMMAND_BUILDSHIP, GRAMMAR_COMMAND_ATTACK
from GodBot.parser_functions import parse_grammar
from GodBot.rpg_functions import fight_simulator
from GodBot.postgresql import db_command, db_insert_rows
from GodBot.ship_class import Ship


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
        db_players = db_command("select * from players")
        db_ships = db_command("select * from ships")
        for db_player in db_players:
            db_player_army = []
            for db_ship in db_ships:
                if db_ship["player_name"] == db_player["name"]:
                    db_player_army.append(Ship(*db_ship))
            self.players[db_player["name"]] = Player(*db_player, army=db_player_army)

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
        db_command("delete from players")
        db_command("delete from ships")
        all_ships = []
        all_players = []
        for _, player in self.players.items():
            for ship in player.army:
                all_ships.append(ship.tuple)
            all_players.append(player.tuple)
        if len(all_players) > 0:
            db_insert_rows("players", all_players)
        if len(all_ships) > 0:
            db_insert_rows("ships", all_ships)

    @commands.command("initPlayer")
    @parse_grammar(grammar=GRAMMAR_COMMAND_INITPLAYER)
    async def init_player(self, ctx: commands.Context, player_race: str):
        "!initPlayer \"race\": Initialize yourself"
        if str(ctx.message.author) not in self.players:
            self.players[str(ctx.message.author)] = Player(
                str(ctx.message.author), player_race)
        else:
            await ctx.message.channel.send(f"{ctx.message.author} already initialized.")

    @commands.command("showMe")
    @is_player_initialized
    async def show_me(self, ctx: commands.Context):
        "!showMe: Show all informations about yourself"
        await ctx.message.channel.send(self.players[str(ctx.message.author)].get_infos())

    @commands.command("buildShip")
    @is_player_initialized
    @parse_grammar(grammar=GRAMMAR_COMMAND_BUILDSHIP)
    async def build_ship(self, ctx: commands.Context, ship_name: str,
                         ship_aoe: int, ship_tankiness: int, investment: int):
        """
        !buildShip name nb_targets tankiness investment: Use money to build a ship
        """
        try:
            self.players[str(ctx.message.author)].create_ship(
                ship_name, ship_aoe, ship_tankiness, investment)
            await ctx.message.channel.send(f"{ship_name} created !")
        except TooLowInvestment as error_msg:
            await ctx.message.channel.send(error_msg)
        except NotEnoughMoney as error_msg:
            await ctx.message.channel.send(error_msg)

    @commands.command("attack")
    @is_player_initialized
    @parse_grammar(grammar=GRAMMAR_COMMAND_ATTACK)
    async def attack(self, ctx: commands.Context, other_player: str):
        "!attack other_player: Fight against another player"
        if (other_player in self.players and other_player != str(ctx.message.author)):
            fight_msg = fight_simulator(
                self.players[str(ctx.message.author)], self.players[other_player])
            await ctx.message.channel.send(fight_msg)
        else:
            await ctx.message.channel.send("You can't fight against yourself !")

    async def send_money(self, ctx: commands.Context, other_player: str, amount: int):
        "Send money from the !give command"
        try:
            self.players[str(ctx.message.author)].send_money(
                self.players[other_player], amount)
        except NotEnoughMoney:
            await ctx.message.channel.send("Not enough money")

    async def send_ship(self, ctx: commands.Context, other_player: str, ship_name: str):
        "Send ship from the !give command"
        try:
            self.players[str(ctx.message.author)].send_ship(
                self.players[other_player], ship_name)
        except NoShip:
            await ctx.message.channel.send("Ship name does not exist")

    @commands.command("send")
    @is_player_initialized
    @parse_grammar(grammar=GRAMMAR_COMMAND_SEND)
    async def give(self, ctx: commands.Context, other_player: str,
                   action: str, action_parameter: Union[str, int]):
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
    async def save(self, ctx: commands.Context):
        """Save the game, an auto save is done every 5 minutes"""
        self.save_in_db_rpg()
        await ctx.message.channel.send("Game saved")

    @commands.command("players")
    async def players_cmd(self, ctx: commands.Context):
        """List all players"""
        msg = "```"
        for player_name, player in self.players.items():
            msg += f'''{player_name}: level {player.level} | army power: {player.army_power} | '''
            msg += f'''money: {player.money} | tech: {player.tech}\n'''
        msg += "```"
        if len(self.players) != 0:
            await ctx.message.channel.send(msg)
        else:
            await ctx.message.channel.send("```No players```")
