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
    cur_hp: int = field(init=False)

    def __post_init__(self):
        self.cur_hp = self.max_hp

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
        return ship_str + f"Damages: {self.damages} - Tech level: {self.tech} - Level: {self.level}"

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
