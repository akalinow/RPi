import unittest
import numpy as np
import mediapipe as mp
from Detector import Detector

class TestDetector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model_path = './blaze_face_short_range.tflite'
        cls.detector = Detector(cls.model_path)
        cls.image_with_face = mp.Image.create_from_file('test_with_face.jpg').numpy_view()
        cls.image_without_face = mp.Image.create_from_file('test_without_face.jpg').numpy_view()

    def test_getModelResponse_with_face(self):
        result = self.detector.getVideoResponse(self.image_with_face)
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    def test_getModelResponse_without_face(self):
        result = self.detector.getVideoResponse(self.image_without_face)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()