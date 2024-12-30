import unittest
from Servos import Servos

class TestServos(unittest.TestCase):

    def setUp(self):
        self.servos = Servos()

    def test_initial_position(self):
        self.assertEqual(self.servos.currAngle, self.servos.restPos)

    def test_reset_position(self):
        self.servos.setPosition((90, 85))
        self.servos.resetPosition()
        self.assertEqual(self.servos.currAngle, self.servos.restPos)

    def test_set_axis_position_within_range(self):
        self.servos.setAxisPosition("h", 90)
        self.assertEqual(self.servos.currAngle["h"], 90)
        self.servos.setAxisPosition("v", 50)
        self.assertEqual(self.servos.currAngle["v"], 50)

    def test_set_axis_position_out_of_range(self):
        self.servos.setAxisPosition("h", 200)
        self.assertNotEqual(self.servos.currAngle["h"], 200)
        self.servos.setAxisPosition("v", 100)
        self.assertNotEqual(self.servos.currAngle["v"], 100)

    def test_set_position(self):
        self.servos.setPosition((90, 85))
        self.assertEqual(self.servos.currAngle["h"], 90)
        self.assertEqual(self.servos.currAngle["v"], 85)

    def test_str(self):
        self.servos.setPosition((90, 85))
        self.assertEqual(str(self.servos), "\x1b[34mH:\x1b[0m90 \x1b[34mV:\x1b[0m85")

if __name__ == '__main__':
    unittest.main()