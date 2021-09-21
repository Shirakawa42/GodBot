"""This file is used by GodBot() to handle messages and commands from users"""


import json
import os.path
from pathlib import Path

from discord.ext import commands, tasks
import parsimonious
from player_class import Player
from rpg_exceptions import NotEnoughMoney, TooLowInvestment, NoShip
from parser_grammars import GRAMMAR_COMMAND_INITPLAYER, GRAMMAR_COMMAND_SEND
from parser_grammars import GRAMMAR_COMMAND_BUILDSHIP, GRAMMAR_COMMAND_ATTACK
from parser_functions import formated_tree_from_grammar
from rpg_functions import fight_simulator


def is_player_initialized(function):
    """Decorator that check if player is initialized or not,
    if not, function is not called and print error"""
    async def new_function(self, ctx):
        if str(ctx.message.author) in self.players:
            await function(self, ctx)
        else:
            msg = f"Player '{ctx.message.author}' not initialized, please use !initPlayer \"race\""
            await ctx.message.channel.send(msg)
    return new_function


def parse_grammar(grammar):
    """Decorator that check if grammar is valid or not with the input,
        if not, function is not called and print error"""
    def parse_grammar_dec(function):
        async def new_function(self, ctx):
            try:
                formated_tree = formated_tree_from_grammar(grammar, ctx.message.content)
                await function(self, ctx, formated_tree)
            except parsimonious.exceptions.ParseError:
                await ctx.message.channel.send(
                    "Command not well formated, use !help \"command name\"")
        return new_function
    return parse_grammar_dec


class RpgCommands(commands.Cog):

    """This class is used by GodBot() to handle RPG commands from users"""

    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        try:
            with open(os.path.join(Path.home(), "RPG_players.json"), "r",
                      encoding="utf-8") as players_file:
                players_json = json.load(players_file)
                self.players_json_to_players(players_json)
        except FileNotFoundError:
            pass

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
        self.save_in_json_rpg()

    @commands.Cog.listener()
    async def on_ready(self):
        "starts time_loop() functions"
        # pylint: disable=no-member
        self.eight_sec_loop.start()
        self.five_min_loop.start()

    def players_json_to_players(self, players_json):
        "Transform rpg_data loaded from the json into useable rpg_data"
        players = {}
        for player_dict in players_json:
            players[player_dict["name"]] = Player(
                player_dict["name"], player_dict["race"], player_dict)
        self.players = players

    def players_to_players_json(self):
        "Transform rpg_data into json-able rpg_data"
        players_json = []
        for player in self.players.items():
            players_json.append(player[1].dict)
        return players_json

    def save_in_json_rpg(self):
        "save everything related to the RPG inside RPG_players.json"
        with open(os.path.join(Path.home(), "RPG_players.json"), "w",
                  encoding="utf-8") as players_file:
            json.dump(self.players_to_players_json(), players_file)

    @commands.command("initPlayer")
    @parse_grammar(grammar=GRAMMAR_COMMAND_INITPLAYER)
    async def init_player(self, ctx, formated_tree):
        "!initPlayer \"race\": Initialize yourself"
        if str(ctx.message.author) not in self.players:
            self.players[str(ctx.message.author)] = Player(
                str(ctx.message.author), formated_tree[1][0])
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
    async def build_ship(self, ctx, formated_tree):
        """
        !buildShip name nb_targets tankiness investment: Use money to build a ship
        """
        try:
            self.players[str(ctx.message.author)].create_ship(
                formated_tree[1][0], int(formated_tree[2][0]), int(formated_tree[3][0]),
                int(formated_tree[4][0]))
            await ctx.message.channel.send(f"{formated_tree[1][0]} created !")
        except TooLowInvestment:
            await ctx.message.channel.send("Minimum investment: 50")
        except NotEnoughMoney:
            await ctx.message.channel.send("Not enough money")

    @commands.command("attack")
    @is_player_initialized
    @parse_grammar(grammar=GRAMMAR_COMMAND_ATTACK)
    async def attack(self, ctx, formated_tree):
        "!attack other_player: Fight against another player"
        if (formated_tree[1][0] in self.players and formated_tree[1][0] != str(ctx.message.author)):
            fight_msg = fight_simulator(
                self.players[str(ctx.message.author)], self.players[formated_tree[1][0]])
            await ctx.message.channel.send(fight_msg)
        else:
            await ctx.message.channel.send("You can't fight against yourself !")

    async def send_money(self, ctx, formated_tree):
        "Send money from the !give command"
        try:
            self.players[str(ctx.message.author)].send_money(
                self.players[formated_tree[1][0]], int(formated_tree[2][1]))
        except NotEnoughMoney:
            await ctx.message.channel.send("Not enough money")

    async def send_ship(self, ctx, formated_tree):
        "Send ship from the !give command"
        try:
            self.players[str(ctx.message.author)].send_ship(
                self.players[formated_tree[1][0]], formated_tree[2][1])
        except NoShip:
            await ctx.message.channel.send("Ship name does not exist")

    @commands.command("send")
    @is_player_initialized
    @parse_grammar(grammar=GRAMMAR_COMMAND_SEND)
    async def give(self, ctx, formated_tree):
        """Send money or ship to another player
        example1: !send "playername" money 300
        example2: !send "playername" ship "shipname"
        """
        if formated_tree[1][0] in self.players:
            if formated_tree[2][0] == "money":
                await self.send_money(ctx, formated_tree)
            else:
                await self.send_ship(ctx, formated_tree)
        else:
            await ctx.message.channel.send("Targeted player does not exist.")

    @commands.command("save")
    async def save(self, ctx):
        """Save the game, an auto save is done every 5 minutes"""
        self.save_in_json_rpg()
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
