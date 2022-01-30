import time
from PetFeeder import Tanks
from utils import publish, subscribe
import utils
import copy
import requests

#the device's sensors
class Sensors():
    water_temp = 0
    wet_food_temp = 1
    pet_collar = 2
    water_mass = 3
    wet_food_mass = 4
    dry_food_mass = 5
    movement = 6


class myTime:
    passing_minutes = 7

    def __init__(self, hour, minute, day, month, year):
        self.hour = hour
        self.minute = minute
        self.day = day
        self.month = month
        self.year = year

    def increaseTime(self, increasing_minutes=passing_minutes):
        self.minute = self.minute + increasing_minutes
        if self.minute >= 60:
            self.hour = self.hour + 1
            self.minute = self.minute % 60
            if self.hour >= 24:
                self.hour = self.hour % 24
                self.day = self.day + 1
                # for simulation purposes only
                # we do not expect to simulate more that a month, hence we did not implement full functionality for this function

    def show(self):
        return str(self.hour).zfill(2) + ":" + str(self.minute).zfill(2) + " , " + str(self.day).zfill(2) \
            + "." + str(self.month).zfill(2) + "." + str(
            self.year)

    def __eq__(self, other):
        return self.hour == other.hour and self.minute == other.minute and self.day == other.day and self.month == other.month \
               and self.year == other.year

    def __le__(self, other):
        if self.year < other.year:
            return True
        if self.year == other.year:
            if self.month < other.month:
                return True
            if self.month == other.month:
                if self.day < other.day:
                    return True
                if self.day == other.day:
                    if self.hour < other.hour:
                        return True
                    if self.hour == other.hour:
                        if self.minute <= other.minute:
                            return True
        return False


def simulation(data_file, petFeeder, mqtt, thread_waiting):
    thread_waiting.join()
    utils.simMutex.acquire()
    turned_on = True
    currentTime = myTime(10, 0, 1, 1, 2022)  # 10:00, 1 January 2022
    timeSincePetDetection = 0
    readOn = True
    while turned_on:
        if (readOn):
            next_line = data_file.readline().split(",")
            readOn = False  # don't read again until the time is met
            try:
                for i in range(len(next_line)):
                    next_line[i] = int(next_line[i])
                next_data_time = myTime(next_line[0], next_line[1], next_line[2], next_line[3], next_line[4])
                next_data_sensor = next_line[5]
                next_data_value = next_line[6]
            except:
                next_data_time = myTime(0, 0, 1, 1, 3000)
                turned_on = False
        to_print1 = currentTime.show() + ": "
        to_print2 = " "

        # append ; and the fake date at the end, so the simulation is outputed as expected
        if next_data_time <= currentTime:
            readOn = True  # the time has been met, read again
            # next_data_time.year = 2000 # fix a bug where sometimes it writes the value twice
            if next_data_sensor == Sensors.water_temp:
                if next_data_value < petFeeder.heating_temperature:
                    to_print2 = "Water temperature at " + str(next_data_value) + " °C, heating"
                else:
                    to_print2 = "Water temperature at " + str(next_data_value) + " °C"
                publish(mqtt, '/SmartPetFeeder/water_temp', str(next_data_value) + ";" + currentTime.show())
            elif next_data_sensor == Sensors.wet_food_temp:
                if next_data_value < petFeeder.heating_temperature:
                    to_print2 = "Wet food temperature at " + str(next_data_value) + " °C, heating"
                else:
                    to_print2 = "Wet food temperature at " + str(next_data_value) + " °C"
                publish(mqtt, '/SmartPetFeeder/wet_food_temp', str(next_data_value) + ";" + currentTime.show())
            elif next_data_sensor == Sensors.pet_collar:
                timeSincePetDetection = 0
                to_print2 = "Pet detected"
                publish(mqtt, '/SmartPetFeeder/pet_detection_warning', to_print2 + ";" + currentTime.show())
            elif next_data_sensor == Sensors.water_mass:
                petFeeder.tanks[Tanks.WATER] = next_data_value
                to_print2 = f"Water mass has changed to {next_data_value} g"
                publish(mqtt, '/SmartPetFeeder/water_mass', str(next_data_value) + ";" + currentTime.show())
            elif next_data_sensor == Sensors.wet_food_mass:
                petFeeder.tanks[Tanks.WET_FOOD] = next_data_value
                to_print2 = f"Wet food mass has changed to {next_data_value} g"
                publish(mqtt, '/SmartPetFeeder/wet_food_mass', str(next_data_value) + ";" + currentTime.show())
            elif next_data_sensor == Sensors.dry_food_mass:
                petFeeder.tanks[Tanks.DRY_FOOD] = next_data_value
                to_print2 = f"Dry food mass has changed to {next_data_value} g"
                publish(mqtt, '/SmartPetFeeder/dry_food_mass', str(next_data_value) + ";" + currentTime.show())
            elif next_data_sensor == Sensors.movement:
                to_print2 = f"Movement detected!"
                publish(mqtt, '/SmartPetFeeder/movement_detection', to_print2 + ";" + currentTime.show())
            # repeat for every sensor
        else:
            if timeSincePetDetection > petFeeder.inactivity_period:
                to_print2 = f"Warning, pet has not eaten for {timeSincePetDetection} minutes!"
                publish(mqtt, '/SmartPetFeeder/pet_detection_warning', to_print2 + ";" + currentTime.show())

            futureTime = copy.deepcopy(currentTime)
            currentTime.increaseTime()
            timeSincePetDetection += myTime.passing_minutes

            for i in range(myTime.passing_minutes):
                futureTime.increaseTime(1)
                hour = futureTime.hour
                minute = futureTime.minute
                if (hour, minute) in petFeeder.feeding_hours:
                    requests.get('http://[::1]:5000/action/give_water/?q=50', headers={"simulation": str(True)})
                    requests.get('http://[::1]:5000/action/give_wet_food/', headers={"simulation": str(True)})
                    requests.get('http://[::1]:5000/action/give_dry_food/', headers={"simulation": str(True)})
                    to_print2 = f"Bowls refilled!"

        final = to_print1 + to_print2

        # print(final)

        time.sleep(1)
    print("Finished simulation")
    utils.simMutex.release()

def wait_for_response():
    utils.simMutex.acquire()
    noResponse = True
    while noResponse:
        try:
            status_code = requests.get('http://[::1]:5000/').status_code
            noResponse = False
        except:
            continue
    utils.simMutex.release()