ffmpeg -f image2 -pattern_type glob -framerate 10 -i '../FaceFollow/frames/full_*Apr*.jpg' -c:v libx264 RPiCam_April.avi
ffmpeg -f image2 -pattern_type glob -framerate 10 -i '../FaceFollow/frames/full_*May*.jpg' -c:v libx264 RPiCam_May.avi
ffmpeg -f image2 -pattern_type glob -framerate 10 -i '../FaceFollow/frames/full_*Jun*.jpg' -c:v libx264 RPiCam_June.avi
ffmpeg -f image2 -pattern_type glob -framerate 10 -i '../FaceFollow/frames/full_*Jul*.jpg' -c:v libx264 RPiCam_July.avi