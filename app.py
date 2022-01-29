from flask import Flask
from flask import request
from flask import Response
from flask_socketio import SocketIO
from flask_mqtt import Mqtt
from PetFeeder import PetFeederClass, PetTypes, Tanks
from simulation import simulation, wait_for_response
from utils import publish, subscribe
import utils
from enum import Enum
import re
import db
import eventlet
import ast
import time
from threading import Thread, Lock
import copy


eventlet.monkey_patch()

app = None
petFeeder = None
socketio = None
mqtt = None


def run_socketio_app():
    global socketio
    socketio = SocketIO(app, async_mode="eventlet")
    socketio.run(app, host='localhost', port=5000, use_reloader=False, debug=True)

def init_mqtt():
    global mqtt
    
    # Setup connection to mqtt broker
    app.config['MQTT_BROKER_URL'] = 'localhost'  # Mosquitto Broker
    app.config['MQTT_BROKER_PORT'] = 1883
    app.config['MQTT_USERNAME'] = ''
    app.config['MQTT_PASSWORD'] = ''
    app.config['MQTT_KEEPALIVE'] = 5 
    app.config['MQTT_TLS_ENABLED'] = False 

    
    try:
        mqtt = Mqtt(app)
        subscribe(mqtt,'/SmartPetFeeder/heating_temperature')
        subscribe(mqtt,'/SmartPetFeeder/feeding_limit')
        subscribe(mqtt,'/SmartPetFeeder/inactivity_period')
        subscribe(mqtt,'/SmartPetFeeder/feeding_hours')
        subscribe(mqtt,'/SmartPetFeeder/tanks_status')

        @mqtt.on_message()
        def handle_mqtt_message(client, userdata, message):
            data = dict(
                topic=message.topic,
                payload=message.payload.decode()
            )
            print(data)
        print("Connected to MQTT broker!")
    except:
        mqtt = None
        print("Could not connect to MQTT broker!")

    return mqtt

def init_app():
    global app, petFeeder
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    
    petFeeder = PetFeederClass(feeding_hours = [(10, 00)], feeding_limit = 100, inactivity_period = 450, heating_temperature = 15, tanks = [200, 500, 400], pet = PetTypes.DOG)

    db.init_app(app)
    with app.app_context():
        db.init_db()
        database = db.get_db()

        # Load the most recent values from the database.
        cursor = database.cursor()
        cursor.execute('SELECT hours FROM FEEDING_HOURS ORDER BY id')
        rows = cursor.fetchall()
        if len(rows) > 0:
            values = rows[-1]['hours']
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
            petFeeder.feeding_hours = new

        cursor = database.cursor()
        cursor.execute('SELECT val FROM FEEDING_LIMITS ORDER BY id')
        rows = cursor.fetchall()
        if len(rows) > 0:
            petFeeder.feeding_limit = float(rows[-1]['val'])

        cursor = database.cursor()
        cursor.execute('SELECT period FROM INACTIVITY_PERIODS ORDER BY id')
        rows = cursor.fetchall()
        if len(rows) > 0:
            petFeeder.inactivity_period = float(rows[-1]['period'])

        cursor = database.cursor()
        cursor.execute('SELECT temperature FROM HEATING_TEMPERATURES ORDER BY id')
        rows = cursor.fetchall()
        if len(rows) > 0:
            petFeeder.heating_temperature = float(rows[-1]['temperature'])

        cursor = database.cursor()
        cursor.execute('SELECT quantities FROM TANKS_STATES ORDER BY id')
        rows = cursor.fetchall()
        if len(rows) > 0:
            petFeeder.tanks = ast.literal_eval(rows[-1]['quantities'])
        print(petFeeder)
    

    @app.route("/")
    def hello_world():
        return "<p>SmartPetFeeder</p>"

    @app.route("/set/heating_temperature/", methods=['POST'])
    def set_heating_temperature():
        try:
            value = float(request.headers["heating_temperature"])
            oldTemp = petFeeder.heating_temperature
            petFeeder.heating_temperature = value
            msg = f"Heating temperature changed from {oldTemp} °C to {value} °C!"
            database = db.get_db()
            database.execute(
                'INSERT INTO HEATING_TEMPERATURES (temperature)'
                ' VALUES (?)',
                (value,)
            )
            database.commit()
            publish(mqtt, '/SmartPetFeeder/heating_temperature', value)
            return(msg)
        except ValueError:
            return "Invalid value!", 406

    @app.route("/set/feeding_limit/", methods=['POST'])
    def set_feeding_limit():
        try:
            value = float(request.headers["feeding_limit"])
            if value < 0:
                raise ValueError
            oldValue = petFeeder.feeding_limit
            petFeeder.feeding_limit = value
            msg = f"Feeding limit changed from {oldValue} g to {value} g!"
            database = db.get_db()
            database.execute(
                'INSERT INTO FEEDING_LIMITS (val)'
                ' VALUES (?)',
                (value,)
            )
            publish(mqtt, '/SmartPetFeeder/feeding_limit', value)
            database.commit()
            return(msg)
        except ValueError:
            return "Invalid value!", 406

    @app.route("/set/feeding_hours/", methods=['POST'])
    def set_feeding_hours():
        re_moment = r'(\d?\d):(\d?\d)'
        try:
            values = request.headers["feeding_hours"] # [11:30, 12:45, 19:20, 13:22]
            oldValues = petFeeder.feeding_hours
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
            petFeeder.feeding_hours = new
            msg = f"Feeding intervals changed from {oldValues} to {new}!"
            database = db.get_db()
            database.execute(
                'INSERT INTO FEEDING_HOURS (hours)'
                ' VALUES (?)',
                (values,)
            )
            database.commit()
            publish(mqtt, '/SmartPetFeeder/feeding_hours', values)
            return(msg)
        except ValueError:
            return "Invalid value!", 406

    @app.route("/set/inactivity_period/", methods=['POST'])
    def set_inactivity_period():
        try:
            value = float(request.headers["inactivity_period"])
            if value < 0:
                raise ValueError
            oldValue = petFeeder.inactivity_period
            petFeeder.inactivity_period = value
            msg = f"Inactivity period changed from {oldValue} minutes to {value} minutes!"
            database = db.get_db()
            database.execute(
                'INSERT INTO INACTIVITY_PERIODS (period)'
                ' VALUES (?)',
                (value,)
            )
            database.commit()
            publish(mqtt, '/SmartPetFeeder/inactivity_period', value)
            return(msg)
        except ValueError:
            return "Invalid value!", 406

    @app.route("/get/heating_temperature/", methods=['GET'])
    def get_heating_temperature():
        value = petFeeder.heating_temperature
        response = Response(f"The heating temperature is: {value} °C.")
        response.headers['heating_temperature'] = value
        return response

    @app.route("/get/feeding_limit/", methods=['GET'])
    def get_feeding_limit():
        value = petFeeder.feeding_limit
        response = Response(f"The feeding limit is : {value} g.")
        response.headers['feeding_limit'] = value
        return response

    @app.route("/get/feeding_hours/", methods=['GET'])
    def get_feeding_hours():
        value = petFeeder.feeding_hours
        response = Response(f"The feeding hours are: {value}.")
        response.headers['feeding_hours'] = value
        return response

    @app.route("/get/inactivity_period/", methods=['GET'])
    def get_inactivity_period():
        value = petFeeder.inactivity_period
        response = Response(f"The inactivity period is: {value} minutes.")
        response.headers['inactivity_period'] = value
        return response

    @app.route("/get/tanks_status/", methods=['GET'])
    def get_tanks_status():
        value = petFeeder.tanks
        response = Response(f"The remaining quantities of food in the tanks are: {value}.")
        response.headers['tanks_status'] = value
        return response

    @app.route("/action/give_water/", methods=['GET'])
    def give_water(): 
        args = request.args
        q = args.get("q", default=Tanks.WATER_DEFAULT, type=int)

        if q > petFeeder.tanks[Tanks.WATER]:
            return Response("Not enough water left in the tank!", status=406) 

        petFeeder.tanks[Tanks.WATER] -= q
        response = Response("Water bowl refilled!")
        database = db.get_db()
        database.execute(
            'INSERT INTO TANKS_STATES (quantities)'
            ' VALUES (?)',
            (str(petFeeder.tanks),)
        )
        database.commit()
        publish(mqtt, '/SmartPetFeeder/tanks_status', str(petFeeder.tanks))
        return response

    @app.route("/action/give_wet_food/", methods=['GET'])
    def give_wet_food():
        args = request.args
        q = args.get("q", default=Tanks.WET_FOOD_DEFAULT, type=int)

        if q > petFeeder.tanks[Tanks.WET_FOOD]:
            return Response("Not enough wet food left in the tank!", status=406) 

        petFeeder.tanks[Tanks.WET_FOOD] -= q
        response = Response("Wet food bowl refilled!")
        database = db.get_db()
        database.execute(
            'INSERT INTO TANKS_STATES (quantities)'
            ' VALUES (?)',
            (str(petFeeder.tanks),)
        )
        database.commit()
        publish(mqtt, '/SmartPetFeeder/tanks_status', str(petFeeder.tanks))
        return response

    @app.route("/action/give_dry_food/", methods=['GET'])
    def give_dry_food():
        args = request.args
        q = args.get("q", default=Tanks.DRY_FOOD_DEFAULT, type=int)

        if q > petFeeder.tanks[Tanks.DRY_FOOD]:
            return Response("Not enough dry food left in the tank!", status=406) 

        petFeeder.tanks[Tanks.DRY_FOOD] -= q
        response = Response("Dry food bowl refilled!")
        database = db.get_db()
        database.execute(
            'INSERT INTO TANKS_STATES (quantities)'
            ' VALUES (?)',
            (str(petFeeder.tanks),)
        )
        database.commit()
        publish(mqtt, '/SmartPetFeeder/tanks_status', str(petFeeder.tanks))
        return response

    @app.route("/action/fill_tanks/", methods=['GET'])
    def fill_tanks():
        petFeeder.tanks = [200, 500, 400]
        response = Response("All tanks refilled!")
        publish(mqtt, '/SmartPetFeeder/tanks_status', str(petFeeder.tanks))
        return response 

    return app
  
data_file = open("pet_data.csv", "r")
turned_on = True # why global?
data_file.readline() # read the header


if __name__ == '__main__':
    init_app()
    init_mqtt()

    choice = input('Run in simulation mode? Y/[N]\n')
    utils.simMutex = Lock()

    if choice.upper() == 'Y':
        thread_waiting_for_response = Thread(target = wait_for_response)
        thread_waiting_for_response.start()

        thread_simulation = Thread(target = simulation, args=(data_file, petFeeder, mqtt, thread_waiting_for_response))
        thread_simulation.start()

    run_socketio_app()