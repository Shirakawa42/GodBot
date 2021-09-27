"This mondule contains custom exceptions for the RPG"


class NotEnoughMoney(Exception):
    "Not enough money"
    def __init__(self, current_money):
        super().__init__(f"You don't have enough money to do this. Current money: {current_money}")


class TooLowInvestment(Exception):
    "Investment too low"
    def __init__(self, investment, req_investment):
        super().__init__(f"{investment} is too low, you must invest at least {req_investment}.")


class NoShip(Exception):
    "Ship not found"


class WrongInput(Exception):
    "Called when the user input is not well formated"


class DataBaseNotConnected(Exception):
    "Called when the database is used but not connected"


class NoEnvException(Exception):
    "Exception raised when an environment variable is not found"
    def __init__(self, environment_variable) -> None:
        super().__init__(f"{environment_variable} not found in environment variables.")
