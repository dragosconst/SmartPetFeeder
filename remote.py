import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo
import requests
import app
from PetFeeder import PetFeederClass, PetTypes, Tanks
import re
import csv

petFeederCopy = PetFeederClass(feeding_hours = [], feeding_limit = 0, inactivity_period = 0, heating_temperature = 0, tanks = [0, 0, 0], pet = PetTypes.DOG)

dpg.create_context()

#  this is not called anywhere, the same function is redefined later on in the code (i refactored the name)
# def getFeedingHours():
#     req = requests.get('http://[::1]:5000/get/feeding_hours/')
#     if req.status_code == 200:
#         values = req.headers["feeding_hours"]
#         values = values.replace("[", "")
#         values = values.replace("]", "")
#         values = values.replace("),", ");")
#         new = []
#         for moment in values.split(";"):
#             moment = moment.replace(" ", "")
#             moment = moment.replace("(", "")
#             moment = moment.replace(")", "")
#
#             hour = int(moment.split(",")[0])
#             minute = int(moment.split(",")[1])
#             new.append((hour, minute))
#         objCopy.feeding_hours = new
#         print(type(new))

def get_feeding_limit():
    req = requests.get('http://[::1]:5000/get/feeding_limit/')
    if req.status_code == 200:
        value = float(req.headers["feeding_limit"])
        petFeederCopy.feeding_limit = value

def increase_feeding_limit():
    value = petFeederCopy.feeding_limit
    value += 10
    petFeederCopy.feeding_limit = value
    req = requests.post('http://[::1]:5000/set/feeding_limit/', headers = {"feeding_limit" : str(value)})
    dpg.set_value("feedingLimitText", str(value) + " g")

def decrease_feeding_limit():
    value = petFeederCopy.feeding_limit
    if value > 10:
        value -= 10
        petFeederCopy.feeding_limit = value
        req = requests.post('http://[::1]:5000/set/feeding_limit/', headers = {"feeding_limit" : str(value)})
        dpg.set_value("feedingLimitText", str(value) + " g")


def get_inactivity_period():
    req = requests.get('http://[::1]:5000/get/inactivity_period/')
    if req.status_code == 200:
        value = float(req.headers["inactivity_period"])
        petFeederCopy.inactivity_period = value

def increase_inactivity_period():
    value = petFeederCopy.inactivity_period
    value += 10
    petFeederCopy.inactivity_period = value
    req = requests.post('http://[::1]:5000/set/inactivity_period/', headers = {"inactivity_period" : str(value)})
    dpg.set_value("inactivityPeriodText", str(value) + " minutes")

def decrease_inactivity_period():
    value = petFeederCopy.inactivity_period
    value -= 10
    petFeederCopy.inactivity_period = value
    req = requests.post('http://[::1]:5000/set/inactivity_period/', headers = {"inactivity_period" : str(value)})
    dpg.set_value("inactivityPeriodText", str(value) + " minutes")

def get_heating_temperature():
    req = requests.get('http://[::1]:5000/get/heating_temperature/')
    if req.status_code == 200:
        value = float(req.headers["heating_temperature"])
        petFeederCopy.heating_temperature = value

def increase_heating_temperature():
    value = petFeederCopy.heating_temperature
    value += 1
    petFeederCopy.heating_temperature = value
    req = requests.post('http://[::1]:5000/set/heating_temperature/', headers = {"heating_temperature" : str(value)})
    dpg.set_value("HeatingTemperatureText", str(value) + " °C")

def decrease_heating_temperature():
    value = petFeederCopy.heating_temperature
    value -= 1
    petFeederCopy.heating_temperature = value
    req = requests.post('http://[::1]:5000/set/heating_temperature/', headers = {"heating_temperature" : str(value)})
    dpg.set_value("HeatingTemperatureText", str(value) + " °C")

def get_tank_status():
    req = requests.get('http://[::1]:5000/get/tanks_status/')
    if req.status_code == 200:
        value = req.headers["tanks_status"]
        value = value.replace("[", "")
        value = value.replace("]", "")
        value = value.replace(" ", "")
        newVal = []
        for i in value.split(","):
            newVal.append(float(i))
        petFeederCopy.tanks = newVal

def reload_tank_status():
    get_tank_status()
    dpg.set_value("WaterTank", "Water:    " + str(petFeederCopy.tanks[Tanks.WATER]) + " g")
    dpg.set_value("WetFoodTank", "Wet Food: " + str(petFeederCopy.tanks[Tanks.WET_FOOD]) + " g")
    dpg.set_value("DryFoodTank", "Dry food: " + str(petFeederCopy.tanks[Tanks.DRY_FOOD]) + " g")

def fill_tanks():
    req = requests.get('http://[::1]:5000/action/fill_tanks/')
    if req.status_code == 200:
        reload_tank_status()

def give_water():
    req = requests.get('http://[::1]:5000/action/give_water/?q=' + str(dpg.get_value("water mass")))
    if req.status_code == 200:
        reload_tank_status()

def give_wet_food():
    req = requests.get('http://[::1]:5000/action/give_wet_food/?q=' + str(dpg.get_value("wet food mass")))
    if req.status_code == 200:
        reload_tank_status()

def give_dry_food():
    req = requests.get('http://[::1]:5000/action/give_dry_food/?q=' + str(dpg.get_value("dry food mass")))
    if req.status_code == 200:
        reload_tank_status()

def set_feeding_hours(sender, app_data, user_data):
    values = user_data
    if values is None:
        values = dpg.get_value("Feeding Hours")
    req = requests.post('http://[::1]:5000/set/feeding_hours/', headers = {"feeding_hours" : values})
    
    re_moment = r'(\d?\d):(\d?\d)'
    new = []
    for moment in values.split(','):
        x = re.search(re_moment, moment)
        if x is None:
            raise ValueError
        hour = int(x.group(1))
        minute = int(x.group(2))
        if hour > 23 or minute > 59:
            raise ValueError
        new.append((hour, minute))
    petFeederCopy.feeding_hours = new

    dpg.set_value("CurrentFeedingHours", str(petFeederCopy.feeding_hours))

def get_feeding_hours():
    req = requests.get('http://[::1]:5000/get/feeding_hours/')
    if req.status_code == 200:
        values = req.headers["feeding_hours"]
        dpg.set_value("CurrentFeedingHours", values)

def get_recommended_values(pet_id):
    with open("recommendations.csv") as f:
        f_reader = csv.DictReader(f, quoting=csv.QUOTE_NONNUMERIC)
        for index, row in enumerate(f_reader):
            if row["pet"] != pet_id:
                continue
            return row["f_limit"], row["water_def"], row["wet_food_def"], row["dry_food_def"], row["fh"], \
                   row["heat_temp"]

def set_recommended_values(sender, app_data, user_data):
    pet_id = user_data[0]
    feeding_limit, water_def, wet_food_def, dry_food_def, feeding_hours, heating_temperature = get_recommended_values(pet_id)

    petFeederCopy.feeding_limit = feeding_limit
    req = requests.post('http://[::1]:5000/set/feeding_limit/', headers = {"feeding_limit" : str(feeding_limit)})
    dpg.set_value("feedingLimitText", str(feeding_limit) + " g")

    dpg.set_value("water mass", water_def)
    dpg.set_value("wet food mass", wet_food_def)
    dpg.set_value("dry food mass", dry_food_def)

    set_feeding_hours(None, None, feeding_hours)

    petFeederCopy.heating_temperature = heating_temperature
    req = requests.post('http://[::1]:5000/set/heating_temperature/', headers = {"heating_temperature" : str(heating_temperature)})
    dpg.set_value("HeatingTemperatureText", str(heating_temperature) + " °C")

#get values before running remote 
get_feeding_limit()
get_inactivity_period()
get_heating_temperature()
get_tank_status()

with dpg.window(label = "Feeding Limit", width = 180, height = 130, pos = (0, 0)):
    dpg.add_text(str(petFeederCopy.feeding_limit) + " g", tag ="feedingLimitText")
    dpg.add_button(label = "+", callback = increase_feeding_limit)
    dpg.add_button(label = "-", callback = decrease_feeding_limit)

with dpg.window(label = "Inactivity Period", width = 180, height = 130, pos = (180, 0)):
    dpg.add_text(str(petFeederCopy.inactivity_period) + " minutes", tag ="inactivityPeriodText")
    dpg.add_button(label = "+", callback = increase_inactivity_period)
    dpg.add_button(label = "-", callback = decrease_inactivity_period)

with dpg.window(label = "Heating Temperature", width = 180, height = 130, pos = (360, 0)):
    dpg.add_text(str(petFeederCopy.heating_temperature) + " °C", tag ="HeatingTemperatureText")
    dpg.add_button(label = "+", callback = increase_heating_temperature)
    dpg.add_button(label = "-", callback = decrease_heating_temperature)

with dpg.window(label = "Tanks Status", width = 180, height = 130, pos = (540, 0)):
    dpg.add_text("Water:    " + str(petFeederCopy.tanks[Tanks.WATER]) + " g", tag ="WaterTank")
    dpg.add_text("Wet Food: " + str(petFeederCopy.tanks[Tanks.WET_FOOD]) + " g", tag ="WetFoodTank")
    dpg.add_text("Dry food: " + str(petFeederCopy.tanks[Tanks.DRY_FOOD]) + " g", tag ="DryFoodTank")
    dpg.add_button(label = "Fill", callback = fill_tanks)

with dpg.window(label = "Actions", width = 220, height = 130, pos = (0, 130)):
    with dpg.group(horizontal=True, width=100):
        dpg.add_button(label = "Give Water", callback = give_water)
        dpg.add_input_float(tag="water mass", default_value=Tanks.WATER_DEFAULT)
    with dpg.group(horizontal=True, width=100):
        dpg.add_button(label = "Give Wet Food", callback = give_wet_food)
        dpg.add_input_float(tag="wet food mass", default_value=Tanks.WET_FOOD_DEFAULT)
    with dpg.group(horizontal=True, width=100):
        dpg.add_button(label = "Give Dry Food", callback = give_dry_food)
        dpg.add_input_float(tag="dry food mass", default_value=Tanks.DRY_FOOD_DEFAULT)

with dpg.window(label = "Feeding Hours", width = 3 * 180, height = 130, pos = (220, 130)):
    dpg.add_text(str(petFeederCopy.feeding_hours), tag="CurrentFeedingHours")
    dpg.add_input_text(label ="Feeding Hours", tag="Feeding Hours")
    dpg.add_button(label = "Set", callback = set_feeding_hours)
    get_feeding_hours()

with dpg.window(label="Recommendations", width=2 * 180, height=130, pos=(0, 260)):
    dpg.add_button(label="Cat", callback=set_recommended_values, user_data=(PetTypes.CAT,))
    dpg.add_button(label="Dog", callback=set_recommended_values, user_data=(PetTypes.DOG,))
    dpg.add_button(label="Snake")
    dpg.add_button(label="Hamster")
    dpg.add_button(label="Parrot")
    dpg.add_button(label="Turtle")
    dpg.add_button(label="Tortoise")

dpg.create_viewport(title = "SmartPetFeeder Remote", width = 800, height = 600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()