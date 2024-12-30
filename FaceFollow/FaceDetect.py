#System imports
import time

#Nice printout imports
from termcolor import colored

#Model imports and variables
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class FaceFollow:

    def __init__(self, model_path):

        FaceDetector = mp.tasks.vision.FaceDetector
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            #running_mode=VisionRunningMode.LIVE_STREAM,
            #result_callback=result_callback
        )

        self.detector = FaceDetector.create_from_options(options)
        self.score_threshold = 0.5

    #############################################
    def getModelResponse(self, rgb_image):
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        result = self.detector.detect(mp_image)
        return result
    #############################################
    def getFacePosition(self, result):

        if not len(result.detections):
            return

        detection = result.detections[0]
        score = detection.categories[0].score

        # Ignore detections with score lower than threshold
        if score < self.score_threshold:
            return
        
        # Get left and right eye positions
        if len(detection.keypoints) < 2:
            return

        left_eye = np.array((detection.keypoints[0].x, detection.keypoints[0].y)) 
        right_eye = np.array((detection.keypoints[1].x, detection.keypoints[1].y)) 
        print(colored("Score:","blue"),score)
        print(colored("Left/right eye:","blue"), left_eye,right_eye)
    #############################################
    def detect(self, mp_image):

        result = self.detector.detect(mp_image)
        return self.getFacePosition(result)    
    #############################################

#############################################
from image_functions import *
#############################################
def test_module():            
            
    if __name__ == '__main__':  
        model_path = '/home/akalinow/scratch/FaceFollow/detector.tflite'
        model = FaceFollow(model_path)

        mp_image = mp.Image.create_from_file('test.jpg')
        result = model.detect(mp_image)
        print(result)

        '''
        image_copy = np.copy(mp_image.numpy_view())
        annotated_image = visualize(image_copy, result)
        rgb_annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        cv2.imwrite("test_annotated.jpg", rgb_annotated_image)

        follow_eyes(result, mp.Image,0)
        '''
              
#############################################
test_module()


