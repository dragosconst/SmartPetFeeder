class PetTypes:
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

    WATER_DEFAULT_PORTION = 300
    WET_FOOD_DEFAULT_PORTION = 75
    DRY_FOOD_DEFAULT_PORTION = 150

    WATER_REFILL = 200
    WET_FOOD_REFILL = 500
    DRY_FOOD_REFILL = 400

class PetFeederClass:
    MAX_HEATING_TEMPERATURE = 100
    MIN_HEATING_TEMPERATURE = 10

    MAX_INACTIVITY_PERIOD = 720 # 12 hours
    MIN_INACTIVITY_PERIOD = 30

    MAX_FEEDING_LIMIT = 1000
    MIN_FEEDING_LIMIT = 5

    def __init__(self, feeding_hours, feeding_limit, inactivity_period, heating_temperature, tanks, pet):
        self.feeding_hours = feeding_hours
        self.feeding_limit = feeding_limit
        self.inactivity_period = inactivity_period
        self.heating_temperature = heating_temperature
        self.tanks = tanks
        self.pet = pet
    
    def __str__(self):
        return "feeding_hours = " + str(self.feeding_hours) + "\nfeeding_limit = " + str(self.feeding_limit) + "\ninactivity_period = " + str(self.inactivity_period) + "\nheating_temperature = " + str(self.heating_temperature) + "\ntanks = " + str(self.tanks) + "\npet = " + str(self.pet)