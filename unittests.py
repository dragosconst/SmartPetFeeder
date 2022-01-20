import unittest
import app

class PetFeederTests(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_heating_temperature(self):
        value = 33
        data = {'heating_temperature' : str(value)}
        response = self.app.post('/set/heating_temperature/', headers=data)
        self.assertTrue(app.myObj.heating_temperature == value)

    def test_feeding_limit(self):
        value = 500
        data = {'feeding_limit' : str(value)}
        response = self.app.post('/set/feeding_limit/', headers=data)
        self.assertTrue(app.myObj.feeding_limit == value)


if __name__ == "__main__":
    unittest.main()