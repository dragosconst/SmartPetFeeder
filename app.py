from flask import Flask
from flask import request
from flask import Response
from PetFeeder import PetFeederClass, PetTypes
import re

myObj = PetFeederClass(feeding_intervals = [], feeding_limit = 10, inactivity_period = 450, heating_temperature = 15, tanks = [200, 500, 400], pet = PetTypes.DOG)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>SmartPetFeeder</p>"

@app.route("/set/heating_temperature/", methods=['POST'])
def set_heating_temperature():
    try:
        value = float(request.headers["heating_temperature"])
        oldTemp = myObj.heating_temperature
        myObj.heating_temperature = value
        msg = f"Heating temperature changed from {oldTemp} °C to {value} °C!"
        print(myObj)
        return(msg)
    except ValueError:
        return "Invalid value!", 406

@app.route("/set/feeding_limit/", methods=['POST'])
def set_feeding_limit():
    try:
        value = float(request.headers["feeding_limit"])
        if value < 0:
            raise ValueError
        oldValue = myObj.feeding_limit
        myObj.feeding_limit = value
        msg = f"Feeding limit changed from {oldValue} g to {value} g!"
        print(myObj)
        return(msg)
    except ValueError:
        return "Invalid value!", 406

@app.route("/set/feeding_intervals/", methods=['POST'])
def set_feeding_intervals():
    re_moment = r'(\d?\d):(\d?\d)'
    try:
        values = request.headers["feeding_intervals"] # [11:30, 12:45, 19:20, 13:22]
        oldValues = myObj.feeding_intervals
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
        myObj.feeding_intervals = new
        msg = f"Feeding intervals changed from {oldValues} to {new}!"
        #print(myObj)
        return(msg)
    except ValueError:
        return "Invalid value!", 406

@app.route("/set/inactivity_period/", methods=['POST'])
def set_inactivity_period():
    try:
        value = float(request.headers["inactivity_period"])
        if value < 0:
            raise ValueError
        oldValue = myObj.inactivity_period
        myObj.inactivity_period = value
        msg = f"Inactivity period changed from {oldValue} minutes to {value} minutes!"
        print(myObj)
        return(msg)
    except ValueError:
        return "Invalid value!", 406

@app.route("/get/heating_temperature/", methods=['GET'])
def get_heating_temperature():
    value = myObj.heating_temperature
    response = Response(f"The heating temperature is: {value} °C.")
    response.headers['heating_temperature'] = value
    return response

@app.route("/get/feeding_limit/", methods=['GET'])
def get_feeding_limit():
    value = myObj.feeding_limit
    response = Response(f"The feeding limit is : {value} g.")
    response.headers['feeding_limit'] = value
    return response

@app.route("/get/feeding_intervals/", methods=['GET'])
def get_feeding_intervals():
    value = myObj.feeding_intervals
    response = Response(f"The feeding intervals are: {value}.")
    response.headers['feeding_intervals'] = value
    return response

@app.route("/get/inactivity_period/", methods=['GET'])
def get_inactivity_period():
    value = myObj.inactivity_period
    response = Response(f"The inactivity period is: {value} minutes.")
    response.headers['inactivity_period'] = value
    return response

@app.route("/get/tanks_status/", methods=['GET'])
def get_tanks_status():
    value = myObj.tanks
    response = Response(f"The remaining quantities of food in the tanks are: {value}.")
    response.headers['tanks_status'] = value
    return response
