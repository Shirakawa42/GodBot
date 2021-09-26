"This mondule contains custom exceptions for the RPG"


class NotEnoughMoney(Exception):
    "Not enough money"
    def __init__(self, current_money):
        super().__init__(f"You don't have enough money to do this. Current money: {current_money}")


class TooLowInvestment(Exception):
    "Investment too low"
    def __init__(self, investment):
        super().__init__(f"{investment} is too low, you must invest at least 50.")


class NoShip(Exception):
    "Ship not found"


class WrongInput(Exception):
    "Called when the user input is not well formated"
