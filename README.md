# RPi
RaspberryPi projects


## FaceFollow

A toy code for a raspberry pi camera usage:

- [x] following a face. 
- [x] face is recognised unsing a [mobilenet_v3](https://www.kaggle.com/models/google/mobilenet-v3/tfLite/large-100-224-feature-vector-metadata) model features. 
- [ ] chat using [Google Gemini API ](https://ai.google.dev/gemini-api/docs/quickstart?lang=python) 
- [ ] voice synthesis using [Google Gemini API](https://ai.google.dev/gemini-api/docs/quickstart?lang=python) 

### Install instructions

```Bash
sudo apt install portaudio19-dev
cd RPi
sudo cp config/pulse/default.pa /etc/pulse
sudo cp config/boot/config.txt /boot/firmware/config.txt
sudo cp config/systemd/* /lib/systemd/system/
sudo systemctl enable jupyter.service
python3 -m venv --system-site-packages ./venv
source venv/bin/activate
pip install -r python/requirements.txt
```

The venv has to use system packages as there are issue witn installing picamera2 from pip.


### Run instructions
```Bash
source venv/bin/activate
cd FaceFollow
python face_follow.py
```
