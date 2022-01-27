from imp import reload
import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo
import requests
import app
from PetFeeder import PetFeederClass, PetTypes, Tanks
import re

objCopy = PetFeederClass(feeding_hours = [], feeding_limit = 0, inactivity_period = 0, heating_temperature = 0, tanks = [0, 0, 0], pet = PetTypes.DOG)

dpg.create_context()

def getFeedingHours():
    req = requests.get('http://[::1]:5000/get/feeding_hours/')
    if req.status_code == 200:
        values = req.headers["feeding_hours"]
        values = values.replace("[", "")
        values = values.replace("]", "")
        values = values.replace("),", ");")
        new = []
        for moment in values.split(";"):
            moment = moment.replace(" ", "")
            moment = moment.replace("(", "")
            moment = moment.replace(")", "")
            
            hour = int(moment.split(",")[0])
            minute = int(moment.split(",")[1])
            new.append((hour, minute))
        objCopy.feeding_hours = new
        print(type(new))

def getFeedingLimit():
    req = requests.get('http://[::1]:5000/get/feeding_limit/')
    if req.status_code == 200:
        value = float(req.headers["feeding_limit"])
        objCopy.feeding_limit = value

def increaseFeedingLimit():
    value = objCopy.feeding_limit
    value += 10
    objCopy.feeding_limit = value
    req = requests.post('http://[::1]:5000/set/feeding_limit/', headers = {"feeding_limit" : str(value)})
    dpg.set_value("feedingLimitText", str(value) + " g")

def decreaseFeedingLimit():
    value = objCopy.feeding_limit
    if value > 10:
        value -= 10
        objCopy.feeding_limit = value
        req = requests.post('http://[::1]:5000/set/feeding_limit/', headers = {"feeding_limit" : str(value)})
        dpg.set_value("feedingLimitText", str(value) + " g")


def getInactivityPeriod():
    req = requests.get('http://[::1]:5000/get/inactivity_period/')
    if req.status_code == 200:
        value = float(req.headers["inactivity_period"])
        objCopy.inactivity_period = value

def increaseInactivityPeriod():
    value = objCopy.inactivity_period
    value += 10
    objCopy.inactivity_period = value
    req = requests.post('http://[::1]:5000/set/inactivity_period/', headers = {"inactivity_period" : str(value)})
    dpg.set_value("inactivityPeriodText", str(value) + " minutes")

def decreaseInactivityPeriod():
    value = objCopy.inactivity_period
    value -= 10
    objCopy.inactivity_period = value
    req = requests.post('http://[::1]:5000/set/inactivity_period/', headers = {"inactivity_period" : str(value)})
    dpg.set_value("inactivityPeriodText", str(value) + " minutes")

def getHeatingTemperature():
    req = requests.get('http://[::1]:5000/get/heating_temperature/')
    if req.status_code == 200:
        value = float(req.headers["heating_temperature"])
        objCopy.heating_temperature = value

def increaseHeatingTemperature():
    value = objCopy.heating_temperature
    value += 1
    objCopy.heating_temperature = value
    req = requests.post('http://[::1]:5000/set/heating_temperature/', headers = {"heating_temperature" : str(value)})
    dpg.set_value("HeatingTemperatureText", str(value) + " °C")

def decreaseHeatingTemperature():
    value = objCopy.heating_temperature
    value -= 1
    objCopy.heating_temperature = value
    req = requests.post('http://[::1]:5000/set/heating_temperature/', headers = {"heating_temperature" : str(value)})
    dpg.set_value("HeatingTemperatureText", str(value) + " °C")

def getTanksStatus():
    req = requests.get('http://[::1]:5000/get/tanks_status/')
    if req.status_code == 200:
        value = req.headers["tanks_status"]
        value = value.replace("[", "")
        value = value.replace("]", "")
        value = value.replace(" ", "")
        newVal = []
        for i in value.split(","):
            newVal.append(float(i))
        objCopy.tanks = newVal

def reloadTanksStatus():
    getTanksStatus()
    dpg.set_value("WaterTank", "Water:    " + str(objCopy.tanks[Tanks.WATER]) + " g")
    dpg.set_value("WetFoodTank", "Wet Food: " + str(objCopy.tanks[Tanks.WET_FOOD]) + " g")
    dpg.set_value("DryFoodTank", "Dry food: " + str(objCopy.tanks[Tanks.DRY_FOOD]) + " g")

def fillTanks():
    req = requests.get('http://[::1]:5000/action/fill_tanks/')
    if req.status_code == 200:
        reloadTanksStatus()

def giveWater():
    req = requests.get('http://[::1]:5000/action/give_water/?q=50')
    if req.status_code == 200:
        reloadTanksStatus()

def giveWetFood():
    req = requests.get('http://[::1]:5000/action/give_wet_food/')
    if req.status_code == 200:
        reloadTanksStatus()

def giveDryFood():
    req = requests.get('http://[::1]:5000/action/give_dry_food/')
    if req.status_code == 200:
        reloadTanksStatus()

def setFeedingHours():
    global feedinghours_input
    values = dpg.get_value(feedinghours_input)
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
    objCopy.feeding_hours = new

    dpg.set_value("CurrentFeedingHours", str(objCopy.feeding_hours))

def getFeedingHours():
    req = requests.get('http://[::1]:5000/get/feeding_hours/')
    if req.status_code == 200:
        values = req.headers["feeding_hours"]
        dpg.set_value("CurrentFeedingHours", values)

#get values before running remote 
getFeedingLimit()
getInactivityPeriod()
getHeatingTemperature()
getTanksStatus()

with dpg.window(label = "Feeding Limit", width = 180, height = 130, pos = (0, 0)):
    dpg.add_text(str(objCopy.feeding_limit) + " g", id = "feedingLimitText")
    dpg.add_button(label = "+", callback = increaseFeedingLimit)
    dpg.add_button(label = "-", callback = decreaseFeedingLimit)

with dpg.window(label = "Inactivity Period", width = 180, height = 130, pos = (180, 0)):
    dpg.add_text(str(objCopy.inactivity_period) + " minutes", id = "inactivityPeriodText")
    dpg.add_button(label = "+", callback = increaseInactivityPeriod)
    dpg.add_button(label = "-", callback = decreaseInactivityPeriod)

with dpg.window(label = "Heating Temperature", width = 180, height = 130, pos = (360, 0)):
    dpg.add_text(str(objCopy.heating_temperature) + " °C", id = "HeatingTemperatureText")
    dpg.add_button(label = "+", callback = increaseHeatingTemperature)
    dpg.add_button(label = "-", callback = decreaseHeatingTemperature)

with dpg.window(label = "Tanks Status", width = 180, height = 130, pos = (540, 0)):
    dpg.add_text("Water:    " + str(objCopy.tanks[Tanks.WATER]) + " g", id = "WaterTank")
    dpg.add_text("Wet Food: " + str(objCopy.tanks[Tanks.WET_FOOD]) + " g", id = "WetFoodTank")
    dpg.add_text("Dry food: " + str(objCopy.tanks[Tanks.DRY_FOOD]) + " g", id = "DryFoodTank")
    dpg.add_button(label = "Fill", callback = fillTanks)

with dpg.window(label = "Actions", width = 180, height = 130, pos = (0, 130)):
    dpg.add_button(label = "Give Water", callback = giveWater)
    dpg.add_button(label = "Give Wet Food", callback = giveWetFood)
    dpg.add_button(label = "Give Dry Food", callback = giveDryFood)

with dpg.window(label = "Feeding Hours", width = 3 * 180, height = 130, pos = (180, 130)):
    global feedinghours_input
    dpg.add_text(str(objCopy.feeding_hours), id="CurrentFeedingHours")
    feedinghours_input = dpg.add_input_text(label = "Feeding Hours")
    dpg.add_button(label = "Set", callback = setFeedingHours)
    getFeedingHours()

dpg.create_viewport(title = "SmartPetFeeder Remote", width = 800, height = 600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()