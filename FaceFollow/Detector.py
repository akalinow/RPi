#System imports
import time

#Nice printout imports
from termcolor import colored

#Model imports and variables
import mediapipe as mp # type: ignore
from mediapipe.tasks import python # type: ignore
from mediapipe.tasks.python import vision # type: ignore

class Detector:

    def __init__(self, model_path, type='still', result_callback=None):

        FaceDetector = mp.tasks.vision.FaceDetector
        BaseOptions = mp.tasks.BaseOptions
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options_still = FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
        )

        options_live = FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=result_callback,
        )
        options = options_still if type == 'still' else options_live

        self.detector = FaceDetector.create_from_options(options)
        self.score_threshold = 0.8
        self.image_size = np.array((640, 480))

    #############################################
    def getVideoResponse(self, rgb_image):
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        self.image_size = rgb_image.shape[1], rgb_image.shape[0]
        result = self.detector.detect_for_video(mp_image, time.monotonic_ns())
        faces = self.getFaces(result, mp_image, timestamp_ms=0)
        return faces
    #############################################
    def getLiveResponse(self, rgb_image):
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        self.image_size = rgb_image.shape[1], rgb_image.shape[0]
        self.detector.detect_async(mp_image, time.monotonic_ns())
    #############################################
    def getFaces(self, result, output_image=None, timestamp_ms=None):
        
        detections = result.detections
        if len(detections) == 0:
            return np.array([])
        
        detections = sorted(detections, key=lambda detection: detection.bounding_box.width*detection.bounding_box.height, 
                            reverse=True) 
        
        faces = []
        for aDetection in detections:
            face = self.getFacePosition(aDetection)
            if face[4]!=0: ##bbox width
                faces.append(face)

        faces = np.array(faces)
        return faces    
    #############################################
    def getFacePosition(self, detection):

        face = np.zeros(6) #face_pos, bbox

        # Ignore detections with score lower than threshold
        score = detection.categories[0].score
        if score < self.score_threshold:
            return face
        
        # Get face position from bounding box
        bbox = detection.bounding_box
        left_eye = np.array((detection.keypoints[0].x, detection.keypoints[0].y)) 
        right_eye = np.array((detection.keypoints[1].x, detection.keypoints[1].y)) 
        face_pos = (left_eye + right_eye)/2.0
        face = np.array([face_pos[0], face_pos[1], 
                         bbox.origin_x, bbox.origin_y,
                         bbox.width, bbox.height])

        return face
#############################################
#############################################
from image_functions import *
#############################################
def test_module():            
            
    if __name__ == '__main__':  
        model_path = '/home/akalinow/scratch/FaceFollow/blaze_face_short_range.tflite'
        
        detectorObj = Detector(model_path, type='still')

        image = mp.Image.create_from_file('test_with_face.jpg').numpy_view()
        faces = detectorObj.getVideoResponse(image)
        print(faces)

        image = mp.Image.create_from_file('test_without_face.jpg').numpy_view()
        faces = detectorObj.getVideoResponse(image)
        print(faces)
        
        def result_callback(result, output_image=None, timestamp_ms=None):
            print(result)

        detectorObj = Detector(model_path, type='live', result_callback=result_callback)
        image = mp.Image.create_from_file('test_with_face.jpg').numpy_view()
        detectorObj.getLiveResponse(image)
                      
#############################################
test_module()


