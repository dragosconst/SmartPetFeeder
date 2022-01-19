import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo
import requests
from PetFeeder import PetFeederClass, PetTypes

objCopy = PetFeederClass(feeding_intervals = [], feeding_limit = 0, inactivity_period = 0, heating_temperature = 0, tanks = [0, 0, 0], pet = PetTypes.DOG)

dpg.create_context()

def getFeedingIntervals():
    req = requests.get('http://127.0.0.1:5000/get/feeding_intervals')
    if req.status_code == 200:
        values = req.headers["feeding_intervals"]
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
        objCopy.feeding_intervals = new
        print(type(new))

def getFeedingLimit():
    req = requests.get('http://127.0.0.1:5000/get/feeding_limit')
    if req.status_code == 200:
        value = float(req.headers["feeding_limit"])
        objCopy.feeding_limit = value

def increaseFeedingLimit():
    value = objCopy.feeding_limit
    value += 10
    objCopy.feeding_limit = value
    req = requests.post('http://127.0.0.1:5000/set/feeding_limit', headers = {"feeding_limit" : str(value)})
    dpg.set_value("feedingLimitText", str(value) + " g")

def decreaseFeedingLimit():
    value = objCopy.feeding_limit
    value -= 10
    objCopy.feeding_limit = value
    req = requests.post('http://127.0.0.1:5000/set/feeding_limit', headers = {"feeding_limit" : str(value)})
    dpg.set_value("feedingLimitText", str(value) + " g")


def getInactivityPeriod():
    req = requests.get('http://127.0.0.1:5000/get/inactivity_period')
    if req.status_code == 200:
        value = float(req.headers["inactivity_period"])
        objCopy.inactivity_period = value

def increaseInactivityPeriod():
    value = objCopy.inactivity_period
    value += 10
    objCopy.inactivity_period = value
    req = requests.post('http://127.0.0.1:5000/set/inactivity_period', headers = {"inactivity_period" : str(value)})
    dpg.set_value("inactivityPeriodText", str(value) + " minutes")

def decreaseInactivityPeriod():
    value = objCopy.inactivity_period
    value -= 10
    objCopy.inactivity_period = value
    req = requests.post('http://127.0.0.1:5000/set/inactivity_period', headers = {"inactivity_period" : str(value)})
    dpg.set_value("inactivityPeriodText", str(value) + " minutes")

#get values before running remote 
getFeedingLimit()
getInactivityPeriod()

with dpg.window(label = "Feeding Limit", width = 180, pos = (0, 0)):
    dpg.add_text(str(objCopy.feeding_limit) + " g", id = "feedingLimitText")
    dpg.add_button(label = "+", callback = increaseFeedingLimit)
    dpg.add_button(label = "-", callback = decreaseFeedingLimit)

with dpg.window(label = "Inactivity Period", width = 180, pos = (180, 0)):
    dpg.add_text(str(objCopy.inactivity_period) + " minutes", id = "inactivityPeriodText")
    dpg.add_button(label = "+", callback = increaseInactivityPeriod)
    dpg.add_button(label = "-", callback = decreaseInactivityPeriod)

dpg.create_viewport(title = "SmartPetFeeder Remote", width = 800, height = 600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()