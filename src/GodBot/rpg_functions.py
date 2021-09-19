"""This module contains all functions needed for the RPG to work"""


from random import randint


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
