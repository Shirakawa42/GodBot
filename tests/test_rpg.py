""" RPG unit tests """


from GodBot.rpg_functions import compare_army_power, fight_simulator
from GodBot.player_class import Player
from GodBot.ship_class import Ship


def test_compare_army_power():
    "test compare_army_power()"
    assert compare_army_power(2500, 3240, 3.0) is True
    assert compare_army_power(2500, 540, 3.0) is False
    assert compare_army_power(2500, 540, 1.5) is False
    assert compare_army_power(2500, 540, 6.0) is True

def test_fight_simulator_playerinit_shipinit():
    "test fight simulator, player initialisation, create_ship()"
    attacker = Player("attacker", "test", money=5000)
    defender = Player("defender", "test2", money=30000)
    attacker.create_ship("testship", 1, 1, 100)
    attacker.create_ship("testship2", 2, 2, 4000)
    attacker.create_ship("testship3", 1, 1, 100)
    defender.create_ship("testship4", 1, 1, 50)
    assert fight_simulator(attacker, defender) == 'You are too strong to attack defender'
    defender.create_ship("testship5", 3, 3, 20000)
    assert fight_simulator(attacker, defender) is not None

def test_player_funcs():
    "test player class functions"
    player1 = Player("player1", "test", money=500)
    player2 = Player("player2", "test2", money=50)
    player1.send_money(player2, 25)
    assert player1.money == 475
    assert player2.money == 75
    player1.create_ship("test", 1, 1, 50)
    player1.send_ship(player2, "test")
    assert len(player1.army) == 0
    assert len(player2.army) == 1
    assert player2.tuple == ('player2', 'test2', 1, 1, 75)
    assert player2.army[0].tuple == ('test', 1, 165, 110, 1, 1, 'player2')
    player1.periodic_money()
    assert player1.money > 425
    player1.won(player2)
    assert player2.money < 75
    assert player1.get_infos() is not None


def test_ship_funcs():
    "test ship class functions"
    ship1 = Ship("ship1", 1, 5000, 100, 5, 5, "nobody")
    ship2 = Ship("ship2", 1, 5000, 100, 10, 10, "nobody")
    ship1.damages_ship(ship2)
    assert ship1.cur_hp < 5000
    ship1.level_up()
    assert ship1.level > 1
    assert ship1.power > 0
    assert ship1.percent > 0
    assert ship1.str is not None
    assert ship1.tuple is not None
    assert ship1.is_dead() is not None
