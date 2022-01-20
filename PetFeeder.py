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

class Tanks:
    WATER = 0
    WET_FOOD = 1
    DRY_FOOD = 2

    WATER_DEFAULT = 300
    WET_FOOD_DEFAULT = 75
    DRY_FOOD_DEFAULT = 150

class PetFeederClass:
    def __init__(self, feeding_hours, feeding_limit, inactivity_period, heating_temperature, tanks, pet):
        self.feeding_hours = feeding_hours
        self.feeding_limit = feeding_limit
        self.inactivity_period = inactivity_period
        self.heating_temperature = heating_temperature
        self.tanks = tanks
        self.pet = pet
    
    def __str__(self):
        return "feeding_hours = " + str(self.feeding_hours) + "\nfeeding_limit = " + str(self.feeding_limit) + "\ninactivity_period = " + str(self.inactivity_period) + "\nheating_temperature = " + str(self.heating_temperature) + "\ntanks = " + str(self.tanks) + "\npet = " + str(self.pet)