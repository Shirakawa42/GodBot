"""This module contains all functions needed for the RPG to work"""


ARMY_POWER_DIFFERENCE = 3
ARMY_HONORABLE_DIFFERENCE = 1.5


def compare_army_power(attacker_army_power, defender_army_power, multiplier):
    """Return True if the attacker army power is less than
    defender army power * multiplier, else return False"""
    if attacker_army_power >= multiplier * defender_army_power:
        return False
    return True


def check_war_winner(attacker, defender):
    """Check who won the war, call the win() function
    and level up ships if the fight was honorable"""
    if len(attacker.army) > 0:
        attacker.won(defender)
        winner, looser = attacker, defender
        win_string = f"{attacker.name} won the war against {defender.name}"
    defender.won(attacker)
    winner, looser = defender, attacker
    win_string = f"{defender.name} won the war against {attacker.name}"
    if compare_army_power(winner, looser, ARMY_HONORABLE_DIFFERENCE):
        for ship in winner.army:
            ship.level_up()
    return win_string


def fight_simulator(attacker, defender):
    "Simulate the fight between 2 players !"
    fight_msg = ""
    army_powers = [attacker.army_power, defender.army_power]
    if not compare_army_power(army_powers[0], army_powers[1], ARMY_POWER_DIFFERENCE):
        return f"You are too strong to attack {defender.name}"
    while len(attacker.army) > 0 and len(defender.army) > 0:
        for ship in attacker.army:
            ship.attack_army(defender.army)
        for player in [attacker, defender]:
            for ship in player.army:
                if ship.is_dead():
                    fight_msg += f"{ship.name} from {player.name}"
                    fight_msg += f" died with {ship.percent}% of his HP\n"
                    player.army.remove(ship)
    return fight_msg + check_war_winner(attacker, defender)
