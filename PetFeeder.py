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

class PetFeederClass:
    def __init__(self, feeding_intervals, feeding_limit, inactivity_period, heating_temperature, tanks, pet):
        self.feeding_intervals = feeding_intervals
        self.feeding_limit = feeding_limit
        self.inactivity_period = inactivity_period
        self.heating_temperature = heating_temperature
        self.tanks = tanks
        self.pet = pet
    
    def __str__(self):
        return "feeding_intervals = " + str(self.feeding_intervals) + "\nfeeding_limit = " + str(self.feeding_limit) + "\ninactivity_period = " + str(self.inactivity_period) + "\nheating_temperature = " + str(self.heating_temperature) + "\ntanks = " + str(self.tanks) + "\npet = " + str(self.pet)