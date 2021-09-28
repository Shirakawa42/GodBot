"This module contain the Ship() class"


from random import randint
from dataclasses import dataclass, field


@dataclass
class Ship():
    "Ship stats and functions"

    name: str
    aoe: int
    max_hp: int
    damages: int
    level: int
    tech: int
    owner_name: str
    cur_hp: int = field(init=False)

    def __post_init__(self):
        self.cur_hp = self.max_hp

    def damages_ship(self, other_ship: 'Ship'):
        "Damage this ship"
        bonus_damages = max((other_ship.level - self.level) / 10.0 + 1.0, 0.3)
        if randint(0, 100) < max(90 - ((self.tech - other_ship.tech) * 5), 25):
            self.cur_hp -= int(other_ship.damages * bonus_damages)

    def is_dead(self) -> bool:
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

    def attack_army(self, army: list['Ship']):
        "Order this ship to shoot randomly in an army"
        for _ in range(self.aoe):
            army[randint(0, len(army)-1)].damages_ship(self)

    @property
    def tuple(self):
        "Return a tuple containing ship datas ans player name"
        return (self.name, self.aoe, self.max_hp, self.damages,
                self.level, self.tech, self.owner_name)

    @property
    def power(self):
        "Return a number representing the powerfullness of this ship"
        return int((self.cur_hp / 20 + self.aoe * 50 + self.damages)
                   ** (1 + self.tech / 50) ** (1 + self.level / 50))

    @property
    def percent(self):
        "Return remaining HP as %"
        return int(self.cur_hp / self.max_hp * 100)

    @property
    def str(self):
        "Return the string of the ship"
        ship_str = f"{self.name}: {self.cur_hp}/{self.max_hp}hp - Aoe: {self.aoe} - "
        return ship_str + f"Damages: {self.damages} - Tech level: {self.tech} - Level: {self.level}"
