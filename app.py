from flask import Flask
from flask import request
from PetFeeder import PetFeederClass

myObj = PetFeederClass(feeding_intervals = [], feeding_limit = 10, inactivity_period = 5, heating_temperature = 15, tanks = 3, pet = 1)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/set/heating_temperature/", methods=['POST'])
def heating_temperature():
    value = request.headers["heating_temperature"]
    myObj.heating_temperature = value
    print("Heating temperature changed!")
    print(myObj)
    return("Heating temperature changed!")