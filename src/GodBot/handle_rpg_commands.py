"""This file is used by GodBot() to handle messages and commands from users"""


import json
import os.path
from pathlib import Path

from discord.ext import commands
import parsimonious
from player_class import Player
from rpg_exceptions import NotEnoughMoney, TooLowInvestment
from parser_grammars import GRAMMAR_COMMAND_INITPLAYER
from parser_grammars import GRAMMAR_COMMAND_BUILDSHIP, GRAMMAR_COMMAND_ATTACK
from parser_functions import formated_tree_from_grammar
from rpg_functions import fight_simulator


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

    def players_json_to_players(self, players_json):
        "Transform rpg_data loaded from the json into useable rpg_data"
        players = {}
        for player_dict in players_json:
            players[player_dict["name"]] = Player(player_dict["name"],
                                                  player_dict["race"], player_dict)
        self.players = players

    def players_to_players_json(self):
        "Transform rpg_data into json-able rpg_data"
        players_json = []
        for player in self.players.items():
            players_json.append(player[1].dict)
        return players_json

    def save_in_json_rpg(self):
        "save everything related to the RPG inside RPG.json"
        with open(os.path.join(Path.home(), "RPG_players.json"), "w",
                  encoding="utf-8") as players_file:
            json.dump(self.players_to_players_json(), players_file)

    @commands.command("initPlayer")
    async def init_player(self, ctx):
        "!initPlayer \"race\": Initialize yourself"
        if str(ctx.message.author) not in self.players:
            try:
                formated_tree = formated_tree_from_grammar(GRAMMAR_COMMAND_INITPLAYER,
                                                           ctx.message.content)
                self.players[str(ctx.message.author)] = Player(str(ctx.message.author),
                                                               formated_tree[1][0])
            except parsimonious.exceptions.ParseError as error:
                await ctx.message.channel.send(error)
        else:
            await ctx.message.channel.send(f"{ctx.message.author} already initialized.")

    @commands.command("showMe")
    async def show_me(self, ctx):
        "!showMe: Show all informations about yourself"
        if str(ctx.message.author) in self.players:
            await ctx.message.channel.send(self.players[str(ctx.message.author)].get_infos())
        else:
            msg = f"Player '{ctx.message.author}' not initialized, please use '!initPlayer race'"
            await ctx.message.channel.send(msg)

    @commands.command("buildShip")
    async def build_ship(self, ctx):
        """
        !buildShip name nb_targets tankiness investment: Use money to build a ship
        """
        if str(ctx.message.author) in self.players:
            try:
                formated_tree = formated_tree_from_grammar(GRAMMAR_COMMAND_BUILDSHIP,
                                                           ctx.message.content)
                self.players[str(ctx.message.author)].create_ship(formated_tree[1][0],
                                                                  int(formated_tree[2][0]),
                                                                  int(formated_tree[3][0]),
                                                                  int(formated_tree[4][0]))
                self.save_in_json_rpg()
                await ctx.message.channel.send(f"{formated_tree[1][0]} created !")
            except parsimonious.exceptions.ParseError:
                await ctx.message.channel.send("error, use: \"!help buildShip\"")
            except TooLowInvestment:
                await ctx.message.channel.send("Minimum investment: 50")
            except NotEnoughMoney:
                await ctx.message.channel.send("Not enough money")
        else:
            msg = f"Player '{ctx.message.author}' not initialized, please use '!initPlayer race'"
            await ctx.message.channel.send(msg)

    @commands.command("attack")
    async def attack(self, ctx):
        "!attack other_player: Fight against another player"
        if str(ctx.message.author) in self.players:
            try:
                formated_tree = formated_tree_from_grammar(GRAMMAR_COMMAND_ATTACK,
                                                           ctx.message.content)
                if (formated_tree[1][0] in self.players and
                        formated_tree[1][0] != str(ctx.message.author)):
                    fight_msg = fight_simulator(self.players[str(ctx.message.author)],
                                                self.players[formated_tree[1][0]])
                    await ctx.message.channel.send(fight_msg)
                    self.save_in_json_rpg()
                else:
                    await ctx.message.channel.send("You can't fight against yourself !")
            except parsimonious.exceptions.ParseError:
                await ctx.message.channel.send("error, use \"help attack\"")
        else:
            msg = f"Player '{ctx.message.author}' not initialized, please use '!initPlayer race'"
            await ctx.message.channel.send(msg)
