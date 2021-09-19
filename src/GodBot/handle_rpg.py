"""This module contains all datas needed for the RPG to work"""


from random import randint


class NotEnoughMoney(Exception):
    "Not enough money"


class TooLowInvestment(Exception):
    "Investment too low"


def fight_simulator(player1, player2):
    "Simulate the fight between 2 players !"
    fight_msg = ""
    if len(player1.army) == 0 or len(player2.army) == 0:
        return "One of the players have no army to fight"
    while len(player1.army) > 0 and len(player2.army) > 0:
        for player, other_player in zip([player1, player2], [player2, player1]):
            for ship in player.army:
                for _ in range(ship.aoe):
                    other_player.army[randint(0, len(other_player.army) -
                                              1)].damages_ship(ship.damages, ship.tech, ship.level)
        for player in [player1, player2]:
            for ship in player.army:
                if ship.is_dead():
                    fight_msg += f"{ship.name} from {player.name}"
                    fight_msg += f" died with {ship.percent}% of his HP\n"
                    player.army.remove(ship)
    for player, other_player in zip([player1, player2], [player2, player1]):
        if len(player.army) > 0:
            player.won()
            return fight_msg + f"{player.name} won the war against {other_player.name}"

class Ship():
    "Ship stats"
    def __init__(self, *args):
        self.name = args[0]
        self.aoe = args[1]
        self.cur_hp = args[2]
        self.max_hp = args[2]
        self.damages = args[3]
        self.level = args[4]
        self.tech = args[5]

    def damages_ship(self, damages, other_tech, other_level):
        "Reduce HP oh the ship"
        bonus_damages = max((other_level - self.level) / 10.0 + 1.0, 0.3)
        if randint(0, 100) < max(90 - ((self.tech - other_tech) * 5), 25):
            self.cur_hp -= int(damages * bonus_damages)

    def is_dead(self):
        "Return true if ship is dead"
        if self.cur_hp <= 0 or (self.cur_hp/self.max_hp < 0.6
                                and randint(0, 80) > (self.cur_hp/self.max_hp)*100):
            return True
        return False

    def level_up(self):
        "Level up the ship"
        self.level += 1
        self.max_hp = int(self.max_hp * 1.05)
        self.cur_hp = self.max_hp
        self.damages = int(self.damages * 1.05)

    @property
    def percent(self):
        "Return remaining HP as %"
        return int(self.cur_hp / self.max_hp * 100)

    @property
    def str(self):
        "Return the string of the ship"
        ship_str = f"{self.name}: {self.cur_hp}/{self.max_hp}hp - Aoe: {self.aoe} - "
        return ship_str + "Damages: {self.damages} - Tech level: {self.tech} - Level: {self.level}"

    @property
    def dict(self):
        "Return a dict containing all ship datas"
        ship_data = {
            "name": self.name,
            "max_hp": self.max_hp,
            "level": self.level,
            "tech": self.tech,
            "aoe": self.aoe,
            "damages": self.damages}
        return ship_data


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

    def won(self):
        "called when the player win a fight"
        for ship in self.army:
            ship.level_up()
        self.money += int(150 ** (1 + self.tech / 30))

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
        beauty = "`"
        beauty += "Player name: " + str(self.name)
        beauty += "\nPlayer race: " + str(self.race)
        beauty += "\nPlayer level: " + str(self.level)
        beauty += "\nTechnologie level: " + str(self.tech)
        beauty += "\nMoney: " + str(self.money)
        beauty += "\nArmy: "
        for ship in self.army:
            beauty += "\n\t" + ship.str
        beauty += "`"
        return beauty

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
