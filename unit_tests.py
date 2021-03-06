from email import header
from http.client import ResponseNotReady
import unittest
import requests
from urllib import response
import app
from PetFeeder import Tanks
from simulation import MyTime
import remote
from utils import publish


class PetFeederTests(unittest.TestCase):
    def setUp(self):
        app.init_app()
        self.app = app.app.test_client()
        self.mqtt = app.init_mqtt()

    def test_mqtt(self):
        publish(self.mqtt, '/SmartPetFeeder/heating_temperature', '30')
        publish(self.mqtt, '/SmartPetFeeder/water_temp', '10')
        publish(self.mqtt, '/SmartPetFeeder/wet_food_temp', '15')
        publish(self.mqtt, '/SmartPetFeeder/pet_detection_warning', '10')
        publish(self.mqtt, '/SmartPetFeeder/wet_food_mass', '10')
        publish(self.mqtt, '/SmartPetFeeder/dry_food_mass', '10')
        publish(self.mqtt, '/SmartPetFeeder/movement_detection', '10')
        self.assertTrue(app.covered)

    def test_set_heating_temperature_valid_value(self):
        value = 33.5
        data = {'heating_temperature': str(value)}
        response = self.app.post('/set/heating_temperature/', headers=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.petFeeder.heating_temperature, value)

    def test_set_heating_temperature_invalid_value(self):
        inital_value = app.petFeeder.heating_temperature
        value = 'qw'
        data = {'heating_temperature': str(value)}
        response = self.app.post('/set/heating_temperature/', headers=data)

        self.assertEqual(response.status_code, 406)
        self.assertEqual(app.petFeeder.heating_temperature, inital_value)

    def test_set_feeding_limit_valid_value(self):
        value = 500
        data = {'feeding_limit': str(value)}
        response = self.app.post('/set/feeding_limit/', headers=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.petFeeder.feeding_limit, value)

    def test_set_feeding_limit_invalid_value(self):
        inital_value = app.petFeeder.feeding_limit
        value = '13o1130'
        data = {'feeding_limit': str(value)}
        response = self.app.post('/set/feeding_limit/', headers=data)

        self.assertEqual(response.status_code, 406)
        self.assertEqual(app.petFeeder.feeding_limit, inital_value)

    def test_set_feeding_hours_valid_values(self):
        value = "9:30,12:00,13:59"
        data = {'feeding_hours': value}
        response = self.app.post('/set/feeding_hours/', headers=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.petFeeder.feeding_hours,
                         [(9, 30), (12, 0), (13, 59)])

    def test_set_feeding_hours_invalid_values_1(self):
        value = "9:30x,12:0,13:59"
        data = {'feeding_hours': value}
        feeding_hours_inital = app.petFeeder.feeding_hours
        response = self.app.post('/set/feeding_hours/', headers=data)

        self.assertEqual(response.status_code, 406)
        self.assertEqual(app.petFeeder.feeding_hours, feeding_hours_inital)

    def test_set_feeding_hours_invalid_values_2(self):
        value = "9:30, 12:0:9, 13:59"
        data = {'feeding_hours': value}
        feeding_hours_inital = app.petFeeder.feeding_hours
        response = self.app.post('/set/feeding_hours/', headers=data)

        self.assertEqual(response.status_code, 406)
        self.assertEqual(app.petFeeder.feeding_hours, feeding_hours_inital)

    def test_set_feeding_hours_invalid_values_3(self):
        value = "9:30,12:0,13:"
        data = {'feeding_hours': value}
        feeding_hours_inital = app.petFeeder.feeding_hours
        response = self.app.post('/set/feeding_hours/', headers=data)

        self.assertEqual(response.status_code, 406)
        self.assertEqual(app.petFeeder.feeding_hours, feeding_hours_inital)

    def test_set_inactivity_period(self):
        value = 54.64
        data = {'inactivity_period': str(value)}
        response = self.app.post('/set/inactivity_period/', headers=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.petFeeder.inactivity_period, value)

    def test_get_heating_temperature(self):
        value = app.petFeeder.heating_temperature
        response = self.app.get('/get/heating_temperature/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['heating_temperature'], str(value))

    def test_get_feeding_limit(self):
        value = app.petFeeder.feeding_limit
        response = self.app.get('/get/feeding_limit/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['feeding_limit'], str(value))

    def test_get_feeding_hours(self):
        value = app.petFeeder.feeding_hours
        response = self.app.get('/get/feeding_hours/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['feeding_hours'], str(value))

    def test_get_inactivity_period(self):
        value = app.petFeeder.inactivity_period
        response = self.app.get('/get/inactivity_period/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['inactivity_period'], str(value))

    def test_get_tanks_status(self):
        value = app.petFeeder.tanks
        response = self.app.get('/get/tanks_status/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['tanks_status'],  str(value))

    def test_give_water_valid_value(self):
        initial_tank_level = app.petFeeder.tanks[Tanks.WATER]
        value = initial_tank_level // 2
        response = self.app.get('/action/give_water/' + '?q= ' + str(value))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            app.petFeeder.tanks[Tanks.WATER] + value, initial_tank_level)

    def test_give_water_higher_value(self):
        initial_tank_level = app.petFeeder.tanks[Tanks.WATER]
        value = initial_tank_level + 500
        response = self.app.get('/action/give_water/' + '?q= ' + str(value))

        self.assertEqual(response.status_code, 406)
        self.assertEqual(app.petFeeder.tanks[Tanks.WATER], initial_tank_level)

    def test_give_dry_food(self):
        initial_tank_level = app.petFeeder.tanks[Tanks.DRY_FOOD]
        value = initial_tank_level + 500
        response = self.app.get('/action/give_dry_food/' + '?q= ' + str(value))

        self.assertEqual(response.status_code, 406)
        self.assertEqual(
            app.petFeeder.tanks[Tanks.DRY_FOOD], initial_tank_level)

    def test_fill_tanks(self):
        expected_value = [Tanks.WATER_REFILL,
                          Tanks.WET_FOOD_REFILL, Tanks.DRY_FOOD_REFILL]
        response = self.app.get('/action/fill_tanks/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.petFeeder.tanks, expected_value)

    def test_simultation_eq_true(self):
        time_1 = MyTime(10, 59, 5, 1, 2022)
        time_2 = MyTime(10, 59, 5, 1, 2022)
        self.assertTrue(time_1 == time_2)

    def test_simultation_eq_false(self):
        time_1 = MyTime(10, 59, 5, 1, 2022)
        time_2 = MyTime(10, 59, 7, 1, 2022)
        self.assertFalse(time_1 == time_2)

    def test_simultation_le_1(self):
        time_1 = MyTime(0, 0, 1, 1, 2023)
        time_2 = MyTime(23, 59, 31, 12, 2022)
        self.assertTrue(time_1 >= time_2)

    def test_simultation_le_2(self):
        time_1 = MyTime(23, 59, 31, 12, 2022)
        time_2 = MyTime(23, 58, 31, 12, 2022)
        self.assertTrue(time_1 >= time_2)

    def test_simulation_show(self):
        time = MyTime(23, 59, 30, 1, 2022)
        show_time = time.show()
        self.assertTrue(show_time == "23:59 , 30.01.2022")

    def test_simulation_increase_time_1(self):
        time = MyTime(23, 59, 11, 1, 2022)
        time.increase_time(2)
        self.assertTrue(time == MyTime(0, 1, 12, 1, 2022))

    def test_simulation_increase_time_2(self):
        time = MyTime(22, 30, 11, 1, 2022)
        time.increase_time(17)
        self.assertTrue(time == MyTime(22, 47, 11, 1, 2022))

    def test_remote_get_feeding_limit(self):
        remote.get_feeding_limit()
        req = requests.get('http://[::1]:5000/get/feeding_limit/')
        self.assertEqual(remote.petFeederCopy.feeding_limit, float(req.headers["feeding_limit"]))

    def test_remote_get_inactivity_period(self):
        remote.get_inactivity_period()
        req = requests.get('http://[::1]:5000/get/inactivity_period/')
        self.assertEqual(remote.petFeederCopy.inactivity_period,  float(req.headers["inactivity_period"]))

    def test_remote_get_heating_temperature(self):
        remote.get_heating_temperature()
        req = requests.get('http://[::1]:5000/get/heating_temperature/')
        self.assertEqual(remote.petFeederCopy.heating_temperature,  float(req.headers["heating_temperature"]))

    def test_remote_increase_feeding_limit(self):
        remote.increase_feeding_limit()
        req = requests.get('http://[::1]:5000/get/feeding_limit/')
        self.assertEqual(remote.petFeederCopy.feeding_limit, float(req.headers["feeding_limit"]))

    def test_remote_decrease_feeding_limit(self):
        remote.decrease_feeding_limit()
        req = requests.get('http://[::1]:5000/get/feeding_limit/')
        self.assertEqual(remote.petFeederCopy.feeding_limit, float(req.headers["feeding_limit"]))

    def test_remote_increase_inactivity_period(self):
        remote.increase_inactivity_period()
        req = requests.get('http://[::1]:5000/get/inactivity_period/')
        self.assertEqual(remote.petFeederCopy.inactivity_period, float(req.headers["inactivity_period"]))

    def test_remote_decrease_inactivity_period(self):
        remote.decrease_inactivity_period()
        req = requests.get('http://[::1]:5000/get/inactivity_period/')
        self.assertEqual(remote.petFeederCopy.inactivity_period,
                         float(req.headers["inactivity_period"]))

    def test_remote_increase_heating_temperature(self):
        remote.increase_heating_temperature()
        req = requests.get('http://[::1]:5000/get/heating_temperature/')
        self.assertEqual(remote.petFeederCopy.heating_temperature,
                         float(req.headers["heating_temperature"]))

    def test_remote_decrease_heating_temperature(self):
        remote.decrease_heating_temperature()
        req = requests.get('http://[::1]:5000/get/heating_temperature/')
        self.assertEqual(remote.petFeederCopy.heating_temperature, float(req.headers["heating_temperature"]))


if __name__ == "__main__":
    unittest.main()
