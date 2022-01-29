import app
import unittest
from PetFeeder import PetFeederClass, PetTypes, Tanks
import db
import ast

class PetFeederIntegrationTests(unittest.TestCase):
    def setUp(self):
        app.init_app()
        self.app = app.app.test_client()

    def test1(self):
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






