import time
from PetFeeder import Tanks
from utils import publish, subscribe
import utils
import copy
import requests

#the device's sensors
class Sensors:
    water_temp = 0
    wet_food_temp = 1
    pet_collar = 2
    water_mass = 3
    wet_food_mass = 4
    dry_food_mass = 5
    movement = 6


class MyTime:
    passing_minutes = 7

    def __init__(self, hour, minute, day, month, year):
        self.hour = hour
        self.minute = minute
        self.day = day
        self.month = month
        self.year = year

    def increase_time(self, increasing_minutes=passing_minutes):
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
        return str(self.hour) + ":" + str(self.minute) + " , " + str(self.day) + "." + str(self.month) + "." + str(
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
    turned_on = True
    current_time = MyTime(10, 0, 1, 1, 2022)  # 10:00, 1 January 2022
    time_since_pet_detection = 0
    read_on = True
    while turned_on:
        if (read_on):
            next_line = data_file.readline().split(",")
            read_on = False  # don't read again until the time is met
            try:
                for i in range(len(next_line)):
                    next_line[i] = int(next_line[i])
                next_data_time = MyTime(next_line[0], next_line[1], next_line[2], next_line[3], next_line[4])
                next_data_sensor = next_line[5]
                next_data_value = next_line[6]
            except:
                next_data_time = MyTime(0, 0, 1, 1, 3000)
                turned_on = False
        to_print1 = current_time.show() + ": "
        to_print2 = " "

        if next_data_time <= current_time:
            read_on = True  # the time has been met, read again
            # next_data_time.year = 2000 # fix a bug where sometimes it writes the value twice
            if next_data_sensor == Sensors.water_temp:
                if next_data_value < petFeeder.heating_temperature:
                    to_print2 = "Water temperature at " + str(next_data_value) + " °C, heating"
                else:
                    to_print2 = "Water temperature at " + str(next_data_value) + " °C"
                publish(mqtt, '/SmartPetFeeder/water_temp', next_data_value)
            elif next_data_sensor == Sensors.wet_food_temp:
                if next_data_value < petFeeder.heating_temperature:
                    to_print2 = "Wet food temperature at " + str(next_data_value) + " °C, heating"
                else:
                    to_print2 = "Wet food temperature at " + str(next_data_value) + " °C"
                publish(mqtt, '/SmartPetFeeder/wet_food_temp', next_data_value)
            elif next_data_sensor == Sensors.pet_collar:
                time_since_pet_detection = 0
                to_print2 = "Pet detected"
                publish(mqtt, '/SmartPetFeeder/pet_detection_warning', to_print2)
            elif next_data_sensor == Sensors.water_mass:
                petFeeder.tanks[Tanks.WATER] = next_data_value
                to_print2 = f"Water mass has changed to {next_data_value} g"
                publish(mqtt, '/SmartPetFeeder/water_mass', next_data_value)
            elif next_data_sensor == Sensors.wet_food_mass:
                petFeeder.tanks[Tanks.WET_FOOD] = next_data_value
                to_print2 = f"Wet food mass has changed to {next_data_value} g"
                publish(mqtt, '/SmartPetFeeder/wet_food_mass', next_data_value)
            elif next_data_sensor == Sensors.dry_food_mass:
                petFeeder.tanks[Tanks.DRY_FOOD] = next_data_value
                to_print2 = f"Dry food mass has changed to {next_data_value} g"
                publish(mqtt, '/SmartPetFeeder/dry_food_mass', next_data_value)
            elif next_data_sensor == Sensors.movement:
                to_print2 = f"Movement detected!"
                publish(mqtt, '/SmartPetFeeder/movement_detection', to_print2)
            # repeat for every sensor
        else:
            if time_since_pet_detection > petFeeder.inactivity_period:
                to_print2 = f"Warning, pet has not eaten for {time_since_pet_detection} minutes!"
                publish(mqtt, '/SmartPetFeeder/pet_detection_warning', to_print2)

            future_time = copy.deepcopy(current_time)
            current_time.increase_time()
            time_since_pet_detection += MyTime.passing_minutes

            for i in range(MyTime.passing_minutes):
                future_time.increase_time(1)
                hour = future_time.hour
                minute = future_time.minute
                if (hour, minute) in petFeeder.feeding_hours:
                    requests.get('http://[::1]:5000/action/give_water/?q=50', headers={"simulation": str(True)})
                    requests.get('http://[::1]:5000/action/give_wet_food/', headers={"simulation": str(True)})
                    requests.get('http://[::1]:5000/action/give_dry_food/', headers={"simulation": str(True)})
                    to_print2 = f"Bowls refilled!"

        final = to_print1 + to_print2

        print(final)

        time.sleep(1)
    print("Finished simulation")

def wait_for_response():
    no_response = True
    while no_response:
        try:
            status_code = requests.get('http://[::1]:5000/').status_code
            if status_code == 200:
                no_response = False
        except:
            continue