"This module contains the Player() class"


from ship_class import Ship
from rpg_exceptions import NotEnoughMoney, TooLowInvestment


class Player():

    """This class contains player data"""

    def __init__(self, name, race, player_data=None):
        if player_data is None:
            player_data = {}
        self.name = name
        self.level = 1 if "level" not in player_data else player_data["level"]
        self.tech = 1 if "tech" not in player_data else player_data["tech"]
        self.money = 500 if "money" not in player_data else player_data["money"]
        self.race = race
        self.army = []
        if "army" in player_data:
            for ship in player_data["army"]:
                self.army.append(Ship(ship["name"], ship["aoe"], ship["max_hp"],
                                      ship["damages"], ship["level"], ship["tech"]))

    def won(self, looser):
        "called when the player win a fight"
        self.money += int(looser.money / 2)
        looser.money /= 2

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
                              int(ship_damages), self.level, self.tech))

    def get_infos(self):
        "Return the player informations beautifully"
        beauty = f"""```\nPlayer name: {self.name}\nPlayer race: {self.race}\nPlayer level: """
        beauty += f"""{self.level}\nTechnologie level: {self.tech}\nMoney: {self.money}\nArmy:"""
        for ship in self.army:
            beauty += "\n\t" + ship.str
        beauty += "```"
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
