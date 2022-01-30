from email import header
import unittest
from urllib import response
import app
from PetFeeder import Tanks


class PetFeederTests(unittest.TestCase):
    def setUp(self):
        app.init_app()
        self.app = app.app.test_client()

    def test_set_heating_temperature(self):
        value = 33
        data = {'heating_temperature': str(value)}
        response = self.app.post('/set/heating_temperature/', headers=data)
        self.assertTrue(app.petFeeder.heating_temperature == value)

    def test_set_feeding_limit(self):
        value = 500
        data = {'feeding_limit': str(value)}
        response = self.app.post('/set/feeding_limit/', headers=data)
        self.assertTrue(app.petFeeder.feeding_limit == value)

    def test_set_feeding_hours(self):
        value = "9:30, 12:0, 23:59"
        data = {'feeding_hours': value}
        response = self.app.post('/set/feeding_hours/', headers=data)
        self.assertTrue(app.petFeeder.feeding_hours == [
                        (9, 30), (12, 0), (23, 59)])

    def test_set_inactivity_period(self):
        value = 54.64
        data = {'inactivity_period': str(value)}
        _ = self.app.post('/set/inactivity_period/', headers=data)
        self.assertTrue(app.petFeeder.inactivity_period == value)

    def test_get_heating_temperature(self):
        value = app.petFeeder.heating_temperature
        response = self.app.get('/get/heating_temperature/')
        self.assertTrue(response.headers['heating_temperature'] == str(value))

    def test_get_feeding_limit(self):
        value = app.petFeeder.feeding_limit
        response = self.app.get('/get/feeding_limit/')
        self.assertTrue(response.headers['feeding_limit'] == str(value))

    def test_get_feeding_hours(self):
        value = app.petFeeder.feeding_hours
        response = self.app.get('/get/feeding_hours/')
        self.assertTrue(response.headers['feeding_hours'] == str(value))

    def test_get_inactivity_period(self):
        value = app.petFeeder.inactivity_period
        response = self.app.get('/get/inactivity_period/')
        self.assertTrue(response.headers['inactivity_period'] == str(value))
    
    def test_get_tanks_status(self):
        value = app.petFeeder.tanks
        response = self.app.get('/get/tanks_status/')
        self.assertTrue(response.headers['tanks_status'] == str(value))

    def test_give_water(self):
        initial_tank_level = app.petFeeder.tanks[Tanks.WATER]
        value = initial_tank_level // 2
        _ = self.app.get('/action/give_water/' + "?q= " + str(value))
        self.assertTrue(app.petFeeder.tanks[Tanks.WATER] + value  == initial_tank_level)

    def test_give_wet_food(self):
        initial_tank_level = app.petFeeder.tanks[Tanks.WET_FOOD]
        _ = self.app.get('/action/give_wet_food/')
        self.assertTrue(app.petFeeder.tanks[Tanks.WET_FOOD] + (Tanks.WET_FOOD_DEFAULT_PORTION if initial_tank_level >= Tanks.WET_FOOD_DEFAULT_PORTION \
                                                               else 0)  == initial_tank_level)

    def test_give_dry_food(self):
        initial_tank_level = app.petFeeder.tanks[Tanks.DRY_FOOD]
        value = initial_tank_level + 500
        _ = self.app.get('/action/give_dry_food/' + "?q= " + str(value))
        self.assertTrue(app.petFeeder.tanks[Tanks.DRY_FOOD] == initial_tank_level)

if __name__ == "__main__":
    unittest.main()
