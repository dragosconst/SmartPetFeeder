from enum import Enum

class PetTypes(Enum):
    CAT = 0
    DOG = 1
    SNAKE = 2
    HAMSTER = 3
    PARROT = 4
    TURTLE = 5
    TORTOISE = 6
    OTHER = 7

class PetFeeder:
    def __init__(self, feeding_intervals, feeding_limit, inactivity_period, heating_temperature, tanks, pet):
        self.feeding_intervals = feeding_intervals
        self.feeding_limit = feeding_limit
        self.inactivity_period = inactivity_period
        self.heating_temperature = heating_temperature
        self.tanks = tanks
        self.pet = pet