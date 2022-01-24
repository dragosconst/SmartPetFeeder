import threading
from flask import Flask
from flask import request
from flask import Response
from flask_socketio import SocketIO
from PetFeeder import PetFeederClass, PetTypes, Tanks
import re
import db
import eventlet
from enum import Enum
import time

app = None
myObj = None
socketio = None

def run_socketio_app():
    global socketio 
    socketio = SocketIO(app, async_mode="eventlet")
    socketio.run(app, host='localhost', port=5000, use_reloader=False, debug=True)

def init_app():
    global app, myObj
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    
    myObj = PetFeederClass(feeding_hours = [], feeding_limit = 10, inactivity_period = 450, heating_temperature = 15, tanks = [200, 500, 400], pet = PetTypes.DOG)
    db.init_app(app)
    with app.app_context():
        db.init_db()

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
            database = db.get_db()
            database.execute(
                'INSERT INTO HEATING_TEMPERATURES (temperature)'
                ' VALUES (?)',
                (value,)
            )
            database.commit()
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

    @app.route("/set/feeding_hours/", methods=['POST'])
    def set_feeding_hours():
        re_moment = r'(\d?\d):(\d?\d)'
        try:
            values = request.headers["feeding_hours"] # [11:30, 12:45, 19:20, 13:22]
            oldValues = myObj.feeding_hours
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
            myObj.feeding_hours = new
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

    @app.route("/get/feeding_hours/", methods=['GET'])
    def get_feeding_hours():
        value = myObj.feeding_hours
        response = Response(f"The feeding hours are: {value}.")
        response.headers['feeding_hours'] = value
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

    @app.route("/action/give_water", methods=['GET'])
    def give_water(): 
        args = request.args
        q = args.get("q", default=Tanks.WATER_DEFAULT, type=int)

        if q > myObj.tanks[Tanks.WATER]:
            return Response("Not enough water left in the tank!") 

        myObj.tanks[Tanks.WATER] -= q
        response = Response("Water bowl refilled!")
        print(myObj)
        return response

    @app.route("/action/give_wet_food", methods=['GET'])
    def give_wet_food():
        args = request.args
        q = args.get("q", default=Tanks.WET_FOOD_DEFAULT, type=int)

        if q > myObj.tanks[Tanks.WET_FOOD]:
            return Response("Not enough wet food left in the tank!") 

        myObj.tanks[Tanks.WET_FOOD] -= q
        response = Response("Wet food bowl refilled!")
        print(myObj)
        return response

    @app.route("/action/give_dry_food", methods=['GET'])
    def give_dry_food():
        args = request.args
        q = args.get("q", default=Tanks.DRY_FOOD_DEFAULT, type=int)

        if q > myObj.tanks[Tanks.DRY_FOOD]:
            return Response("Not enough dry food left in the tank!") 

        myObj.tanks[Tanks.DRY_FOOD] -= q
        response = Response("Dry food bowl refilled!")
        print(myObj)
        return response

    return app


data_file = open("pet_data.csv", "r")
turned_on = True
data_file.readline() # read the header

# the device's sensors
class Sensors(Enum):
    water_temp = 0
    wet_food_temp = 1
    dry_food_temp = 2
    pet_leash = 3

class myTime:
    def __init__(self, hour, minute, day, month, year):
        self.hour = hour
        self.minute = minute
        self.day = day
        self.month = month
        self.year = year
    
    def increaseTime(self):
        self.minute = self.minute + 5
        if self.minute == 60:
            self.hour = self.hour + 1
            self.minute = 0
            if self.hour == 24:
                self.hour = 0
                self.day = self.day + 1
                # for simulation purposes only
                # we do not expect to simulate more that a month, hence we did not implement full functionality for this function
    def show(self):
        return str(self.hour) + ":" + str(self.minute) + " , " + str(self.day) + "." + str(self.month) + "." + str(self.year)

    def __eq__(self, other):
        return self.hour == other.hour and self.minute == other.minute and self.day == other.day and self.month == other.month \
            and self.year == other.year

currentTime = myTime(10, 0, 1, 1, 2022) # 10:00, 1 January 2022
def simulation():
    global turned_on
    global currentTime
    readOn = True
    while turned_on:
        if(readOn):
            next_line = data_file.readline().split(",")
            readOn = False # don't read again until the time is met
            try:
                for i in range(len(next_line)):
                    next_line[i] = int(next_line[i])
                next_data_time = myTime(next_line[0], next_line[1], next_line[2], next_line[3], next_line[4])
                next_data_sensor = next_line[5]
                next_data_value = next_line[6]
            except:
                turned_on = False
        to_print1 = currentTime.show() + ": "
        to_print2 = " "
        
        if currentTime == next_data_time:
            readOn = True # the time has been met, read again
            next_data_time.year = 2000 # fix a bug where sometimes it writes the value twice
            if next_data_sensor == 0:
                if next_data_value < myObj.heating_temperature:
                    to_print2 = "Water temperature at " + str(next_data_value) + " °C, starting heating"
                else:
                    to_print2 = "Water temperature at " + str(next_data_value) + " °C"
            # repeat for every sensor

        else:
            currentTime.increaseTime()
        final = to_print1 + to_print2
        
        print(final)
        
        
        time.sleep(1)
    print("Finished simulation")
        



if __name__ == '__main__':
    init_app()
    
    x = threading.Thread(target = simulation)
    x.start()
    
    run_socketio_app()