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
sudo apt install portaudio19-dev bluez-alsa-utils vsftpd
sudo dpkg-reconfigure locales
sudo systemctl disable bluealsa
pactl list #find name of the BT speaker
sudo pactl set-card-profile bluez_card.00_A4_1C_B0_CE_E6 headset-head-unit
cd RPi
sudo cp config/pulse/default.pa /etc/pulse
sudo cp config/boot/config.txt /boot/firmware/config.txt
sudo cp config/systemd/* /lib/systemd/system/
sudo cp config/crontab/akalinow /var/spool/cron/crontabs
sudo systemctl enable jupyter.service
sudo systemctl enable vsftpd.service
sudo systemctl enable face_monitor.service
python3 -m venv --system-site-packages ./venv
source venv/bin/activate
pip install -r python/requirements.txt
pip3 install git+https://github.com/pimoroni/VL53L0X-python.git
cp python/TSL2591.py venv/lib/python3.11/site-packages
python3 -m ipykernel install --user --name=venv
```

The venv has to use system packages as there are issue witn installing picamera2 from pip.

### Run instructions
```Bash
cd RPi
source venv/bin/activate
cd FaceFollow
python face_follow.py
```
