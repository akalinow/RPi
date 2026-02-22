ls -1tr ../FaceFollow/frames/full_*.jpg | sed 's/^/file /' > frames.txt
ffmpeg -f image2 -pattern_type glob -framerate 10 -i frames.txt -c:v libx264 RPiCam.avi

#ffmpeg -f image2 -pattern_type glob -framerate 10 -i '../FaceFollow/frames/full_*May*.jpg' -c:v libx264 RPiCam_May.avi
#ffmpeg -f image2 -pattern_type glob -framerate 10 -i '../FaceFollow/frames/full_*Jun*.jpg' -c:v libx264 RPiCam_June.avi
#ffmpeg -f image2 -pattern_type glob -framerate 10 -i '../FaceFollow/frames/full_*Jul*.jpg' -c:v libx264 RPiCam_July.avi