import app
import unittest
from PetFeeder import PetFeederClass, PetTypes, Tanks
import db
import ast

class PetFeederIntegrationTests(unittest.TestCase):
    def setUp(self):
        app.init_app()
        self.app = app.app.test_client()

    def test_temperature_feeding_limit_give_wet_food(self):
        # initialize object to custom values
        app.petFeeder = PetFeederClass(feeding_hours=[(10, 00)], feeding_limit=100, inactivity_period=450,
                                   heating_temperature=15, tanks=[200, 500, 400], pet=PetTypes.DOG)
        temperature_value = 20
        t_data = {'heating_temperature': str(temperature_value)}
        t_response = self.app.post('/set/heating_temperature/', headers=t_data)
        self.assertTrue(app.petFeeder.heating_temperature == temperature_value)

        with app.app.app_context():
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute('SELECT temperature FROM HEATING_TEMPERATURES ORDER BY id')
            rows = cursor.fetchall()
            temperature_db = rows[-1]["temperature"]
            self.assertTrue(temperature_db == temperature_value)

            # remove test from database
            database.execute('DELETE FROM HEATING_TEMPERATURES WHERE id = (SELECT MAX(id) FROM HEATING_TEMPERATURES)')
            database.commit()

        feeding_value = 150
        f_data = {'feeding_limit': str(feeding_value)}
        f_response = self.app.post('/set/feeding_limit/', headers=f_data)
        self.assertTrue(app.petFeeder.feeding_limit == feeding_value)

        with app.app.app_context():
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute('SELECT val FROM FEEDING_LIMITS ORDER BY id')
            rows = cursor.fetchall()
            feeding_db = rows[-1]["val"]
            self.assertTrue(feeding_db == feeding_value)

            # remove test from database
            database.execute('DELETE FROM FEEDING_LIMITS WHERE id = (SELECT MAX(id) FROM FEEDING_LIMITS)')
            database.commit()

        # try to give more food than the feeding limit
        give_wet_food = 200
        initial_tank_level = app.petFeeder.tanks[Tanks.WET_FOOD]
        _ = self.app.get('/action/give_wet_food/?q=' + str(give_wet_food))
        self.assertTrue(app.petFeeder.tanks[Tanks.WET_FOOD] == initial_tank_level - feeding_value)

        with app.app.app_context():
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute('SELECT quantities FROM TANKS_STATES ORDER BY id')
            rows = cursor.fetchall()
            tank_states_db = ast.literal_eval(rows[-1]["quantities"])
            self.assertTrue(tank_states_db[Tanks.WET_FOOD] == initial_tank_level - feeding_value)

            # remove test from database
            database.execute('DELETE FROM TANKS_STATES WHERE id = (SELECT MAX(id) FROM TANKS_STATES)')
            database.commit()

    # testing if refill works as expected after feeding the pet
    def test_feed_and_refill(self):
        # initialize object to custom values
        init_water = 200
        init_wet_food = 500
        app.petFeeder = PetFeederClass(feeding_hours=[(10, 00)], feeding_limit=200, inactivity_period=450,
                                   heating_temperature=15, tanks=[200, 500, 400], pet=PetTypes.DOG)

        # first, give the pet some food and water
        give_wet_food = 200
        initial_tank_level = app.petFeeder.tanks[Tanks.WET_FOOD]
        _ = self.app.get('/action/give_wet_food/?q=' + str(give_wet_food))
        self.assertTrue(app.petFeeder.tanks[Tanks.WET_FOOD] == initial_tank_level - give_wet_food)

        with app.app.app_context():
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute('SELECT quantities FROM TANKS_STATES ORDER BY id')
            rows = cursor.fetchall()
            tank_states_db = ast.literal_eval(rows[-1]["quantities"])
            self.assertTrue(tank_states_db[Tanks.WET_FOOD] == initial_tank_level - give_wet_food)

            # remove test from database
            database.execute('DELETE FROM TANKS_STATES WHERE id = (SELECT MAX(id) FROM TANKS_STATES)')
            database.commit()

        give_water = 150
        initial_tank_level = app.petFeeder.tanks[Tanks.WATER]
        _ = self.app.get('/action/give_water/?q=' + str(give_water))
        self.assertTrue(app.petFeeder.tanks[Tanks.WATER] == initial_tank_level - give_water)

        with app.app.app_context():
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute('SELECT quantities FROM TANKS_STATES ORDER BY id')
            rows = cursor.fetchall()
            tank_states_db = ast.literal_eval(rows[-1]["quantities"])
            self.assertTrue(tank_states_db[Tanks.WATER] == initial_tank_level - give_water)

            # remove test from database
            database.execute('DELETE FROM TANKS_STATES WHERE id = (SELECT MAX(id) FROM TANKS_STATES)')
            database.commit()

        _ = self.app.get('/action/fill_tanks/')
        self.assertTrue(app.petFeeder.tanks[Tanks.WATER] == Tanks.WATER_REFILL)
        self.assertTrue(app.petFeeder.tanks[Tanks.WET_FOOD] == Tanks.WET_FOOD_REFILL)
        self.assertTrue(app.petFeeder.tanks[Tanks.DRY_FOOD] == Tanks.DRY_FOOD_REFILL)

    # send some bad values to feeding hours and feeding limit and check if they are handled accordingly
    def test_bad_input_feeding_limit_and_hours(self):
        app.petFeeder = PetFeederClass(feeding_hours=[(10, 00)], feeding_limit=200, inactivity_period=450,
                                   heating_temperature=15, tanks=[200, 500, 400], pet=PetTypes.DOG)

        # send a non numeric string and check it doesn't do anything
        feeding_limit = "mancare"
        f_data = {'feeding_limit': str(feeding_limit)}
        f_response = self.app.post('/set/feeding_limit/', headers=f_data)
        self.assertFalse(app.petFeeder.feeding_limit == feeding_limit)

        with app.app.app_context():
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute('SELECT val FROM FEEDING_LIMITS ORDER BY id')
            rows = cursor.fetchall()
            feeding_db = rows[-1]["val"]
            self.assertFalse(feeding_db == feeding_limit)

        # send some bad values to the feeding hours function
        feeding_hours = "12:30:15, 10:11"
        fh_data = {'feeding_hours': feeding_hours}
        fh_response = self.app.post('/set/feeding_hours/', headers=fh_data)
        if len(app.petFeeder.feeding_hours) >= 2:
            # database.execute('DELETE FROM FEEDING_HOURS WHERE id = (SELECT MAX(id) FROM FEEDING_HOURS)')
            # database.commit()
            self.assertFalse(app.petFeeder.feeding_hours[1] == (10, 11))


        with app.app.app_context():
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute('SELECT hours FROM FEEDING_HOURS ORDER BY id')
            rows = cursor.fetchall()
            feeding_h_db = rows[-1]["hours"]
            self.assertFalse(feeding_h_db == "12:30:15, 10:11")

    # send negative value to temperature and negative value to feeding_hours
    def test_negative_temp_negative_feeding_hours(self):
        app.petFeeder = PetFeederClass(feeding_hours=[(10, 00)], feeding_limit=200, inactivity_period=450,
                                   heating_temperature=15, tanks=[200, 500, 400], pet=PetTypes.DOG)

        # send a negative value
        temperature_value = -20
        t_data = {'heating_temperature': str(temperature_value)}
        t_response = self.app.post('/set/heating_temperature/', headers=t_data)
        self.assertFalse(app.petFeeder.heating_temperature == temperature_value)

        with app.app.app_context():
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute('SELECT temperature FROM HEATING_TEMPERATURES ORDER BY id')
            rows = cursor.fetchall()
            temperature_db = rows[-1]["temperature"]
            self.assertFalse(temperature_db == temperature_value)

            # remove test from database, delete this code after fixing the bug
            database.execute('DELETE FROM HEATING_TEMPERATURES WHERE id = (SELECT MAX(id) FROM HEATING_TEMPERATURES)')
            database.commit()

        # send some bad values to the feeding hours function
        feeding_hours = "-12:30, 10:-11"
        fh_data = {'feeding_hours': feeding_hours}
        fh_response = self.app.post('/set/feeding_hours/', headers=fh_data)
        if len(app.petFeeder.feeding_hours) >= 2:
            # database.execute('DELETE FROM FEEDING_HOURS WHERE id = (SELECT MAX(id) FROM FEEDING_HOURS)')
            # database.commit()
            self.assertFalse(app.petFeeder.feeding_hours[1] == (10, -11))


        with app.app.app_context():
            database = db.get_db()
            cursor = database.cursor()
            cursor.execute('SELECT hours FROM FEEDING_HOURS ORDER BY id')
            rows = cursor.fetchall()
            feeding_h_db = rows[-1]["hours"]
            self.assertFalse(feeding_h_db == "-12:30, 10:-11")




