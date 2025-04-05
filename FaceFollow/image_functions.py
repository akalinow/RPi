from typing import Tuple, Union
import time

import math
import numpy as np
import cv2

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # red

##############################################################
def _normalized_to_pixel_coordinates(
    normalized_x: float, normalized_y: float, image_width: int,
    image_height: int) -> Union[None, Tuple[int, int]]:
  """Converts normalized value pair to pixel coordinates."""

  # Checks if the float value is between 0 and 1.
  def is_valid_normalized_value(value: float) -> bool:
    return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                      math.isclose(1, value))

  if not (is_valid_normalized_value(normalized_x) and
          is_valid_normalized_value(normalized_y)):
    # TODO: Draw coordinates even if it's outside of the image bounds.
    return None
  x_px = min(math.floor(normalized_x * image_width), image_width - 1)
  y_px = min(math.floor(normalized_y * image_height), image_height - 1)
  return x_px, y_px
####################################################################
def annotateImage(image, fps):
   
  # Show the FPS
  # Visualization parameters
  _ROW_SIZE = 15  # pixels
  _LEFT_MARGIN = 5  # pixels
  _TEXT_COLOR = (0, 0, 255)  # red
  _FONT_SIZE = 1
  _FONT_THICKNESS = 1
  fps_text = 'FPS = ' + str(int(fps))
  text_location = (_LEFT_MARGIN, _ROW_SIZE)

  timestamp_text = time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime()) 
    
  cv2.putText(image, timestamp_text, text_location, cv2.FONT_HERSHEY_PLAIN,
              _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)
  return image
####################################################################
def cropFace(image, focusPoints):
    width, height = image.shape[1], image.shape[0]
    new_res = (224, 224)
    
    keypoint_x, keypoint_y = focusPoints[0], focusPoints[1]
    keypoint_px = _normalized_to_pixel_coordinates(keypoint_x, keypoint_y,
                                                    width, height)
    
    bbox = focusPoints[2:6].astype(int)
    anchor = np.array((bbox[1], bbox[0]))
    size = np.array((bbox[3], bbox[2])).astype(int)
    anchor -= (size*0.2).astype(int)
    anchor -= (50, 0)
    size += (size*0.4).astype(int)
    anchor = np.where(anchor>0, anchor, 0)
    image_cropped = image[anchor[0]:anchor[0]+size[0], anchor[1]:anchor[1]+size[1]]
    image_resized = cv2.resize(image_cropped,dsize=new_res, interpolation = cv2.INTER_CUBIC)
    return image_resized
    
####################################################################
def drawFocusPoints(image, focusPoints):
    for point in focusPoints:
        width, height = image.shape[1], image.shape[0]
        keypoint_x, keypoint_y = focusPoints[0], focusPoints[1]
        keypoint_px = _normalized_to_pixel_coordinates(keypoint_x, keypoint_y,
                                                     width, height)
        
        cv2.circle(image, keypoint_px, 5, (0, 0, 255), -1)
        cv2.circle(image, point[2:4].astype(int)-50, 5, (255,0,0), -1)

    return image_resized
####################################################################
def visualize(
    image,
    detection_result
) -> np.ndarray:
  """Draws bounding boxes and keypoints on the input image and return it.
  Args:
    image: The input RGB image.
    detection_result: The list of all "Detection" entities to be visualize.
  Returns:
    Image with bounding boxes.
  """
  annotated_image = image.copy()
  height, width, _ = image.shape

  for detection in detection_result.detections:
    # Draw bounding_box
    bbox = detection.bounding_box
    start_point = bbox.origin_x, bbox.origin_y
    end_point = bbox.origin_x + 1.05*bbox.width, bbox.origin_y + 1.1*bbox.height
    cv2.rectangle(annotated_image, start_point, end_point, TEXT_COLOR, 3)

    # Draw keypoints
    for keypoint in detection.keypoints:
      keypoint_px = _normalized_to_pixel_coordinates(keypoint.x, keypoint.y,
                                                     width, height)
      color, thickness, radius = (0, 255, 0), 2, 2
      cv2.circle(annotated_image, keypoint_px, thickness, color, radius)

    # Draw label and score
    category = detection.categories[0]
    category_name = category.category_name
    category_name = '' if category_name is None else category_name
    probability = round(category.score, 2)
    result_text = category_name + ' (' + str(probability) + ')'
    text_location = (MARGIN + bbox.origin_x,
                     MARGIN + ROW_SIZE + bbox.origin_y)
    cv2.putText(annotated_image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

  return annotated_image
  ######################################################################