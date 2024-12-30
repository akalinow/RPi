import unittest
import numpy as np
import mediapipe as mp
from Detector import Detector

class TestDetector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model_path = '/home/akalinow/scratch/FaceFollow/detector.tflite'
        cls.detector = Detector(cls.model_path)
        cls.image_with_face = mp.Image.create_from_file('test_with_face.jpg').numpy_view()
        cls.image_without_face = mp.Image.create_from_file('test_without_face.jpg').numpy_view()

    def test_getModelResponse_with_face(self):
        result = self.detector.getModelResponse(self.image_with_face)
        self.assertIsNotNone(result)
        self.assertGreater(len(result.detections), 0)

    def test_getModelResponse_without_face(self):
        result = self.detector.getModelResponse(self.image_without_face)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.detections), 0)

    def test_getFaces_with_face(self):
        faces = self.detector.getFaces(self.image_with_face)
        self.assertIsNotNone(faces)
        self.assertGreater(len(faces), 0)

    def test_getFaces_without_face(self):
        faces = self.detector.getFaces(self.image_without_face)
        self.assertIsNone(faces)

    def test_getFacePosition(self):
        result = self.detector.getModelResponse(self.image_with_face)
        detection = result.detections[0]
        face_pos = self.detector.getFacePosition(detection)
        self.assertIsNotNone(face_pos)
        self.assertEqual(len(face_pos), 2)

if __name__ == '__main__':
    unittest.main()