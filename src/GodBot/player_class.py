"This module contains the Player() class"


from random import randint
from typing import Optional

from GodBot.ship_class import Ship
from GodBot.rpg_exceptions import NotEnoughMoney, TooLowInvestment, NoShip


class Player():

    """This class contains player data"""

    def __init__(
        self,
        name: str,
        race: str,
        level: Optional[int] = 1,
        tech: Optional[int] = 1,
        money: Optional[int] = 500,
        army: list[Ship] = None
        ):
        self.name = name
        self.level = level
        self.tech = tech
        self.money = money
        self.race = race
        self.army = army or []

    def periodic_money(self):
        "Add money based on level and tech"
        self.money += self.level + self.tech

    def won(self, looser):
        "called when the player win a fight"
        self.money += int(looser.money / 2)
        looser.money /= 2

    def send_money(self, other_player, amount):
        "send money to another player"
        if self.money >= amount:
            self.money -= amount
            other_player.money += amount
        else:
            raise NotEnoughMoney

    def send_ship(self, other_player, ship_name):
        "send ship to another player"
        ship_found = False
        for ship in self.army:
            if ship.name == ship_name:
                other_player.army.append(ship)
                self.army.remove(ship)
                ship_found = True
        if not ship_found:
            raise NoShip

    def luck(self):
        "with luck, some free ships may appear"
        if (randint(0, 100)) <= 2:
            investment = randint(50 * self.level, 150 * self.level)
            self.money += investment
            self.create_ship("lucky", randint(1, 4), randint(1, 5), investment)

    def create_ship(self, ship_name, ship_aoe, ship_tankiness, investment):
        "ship: {ship_name, aoe, hp, max_hp, damages, tech}"
        if investment > self.money:
            raise NotEnoughMoney
        if investment < 50:
            raise TooLowInvestment
        ship_aoe = max(1, ship_aoe)
        ship_tankiness = max(1, ship_tankiness)
        if ship_aoe > investment / 2:
            ship_aoe = max(int(investment / 2), 1)
        if ship_tankiness > investment / 2:
            ship_tankiness = max(int(investment / 2), 1)
        ship_hp = ship_tankiness * (investment * 3 * (1.1 ** self.tech))
        ship_damages = investment / ship_aoe / ship_tankiness * (1.1 ** self.tech) * 2
        self.money -= investment
        self.army.append(Ship(ship_name, ship_aoe, int(ship_hp),
                              int(ship_damages), 1, self.tech))

    def get_infos(self):
        "Return the player informations beautifully"
        beauty = f"""```\nPlayer name: {self.name}\nPlayer race: {self.race}\nPlayer level: """
        beauty += f"""{self.level}\nTechnologie level: {self.tech}\nMoney: {self.money}\nArmy:"""
        for ship in self.army:
            beauty += "\n\t" + ship.str
        beauty += f"\nArmy power: {self.army_power}```"
        return beauty

    @property
    def army_power(self):
        "Return the total army power of this player"
        army_power = 0
        for ship in self.army:
            army_power += ship.power
        return army_power

    @property
    def dict(self):
        "Return a dict containing all player datas"
        player_data = {
            "name": self.name,
            "level": self.level,
            "money": self.money,
            "race": self.race,
            "tech": self.tech,
            "army": []}
        for ship in self.army:
            player_data["army"].append(ship.dict)
        return player_data
