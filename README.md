# RPi
RaspberryPi projects


## FaceFollow

A toy code for a raspberry pi camera usage:

- [x] following a face. [DONE]
- [] face is recognised unsing a [mobilenet_v3](https://www.kaggle.com/models/google/mobilenet-v3/tfLite/large-100-224-feature-vector-metadata) model features. [NOT YET]
- [] chat using [Google Gemini API ](https://ai.google.dev/gemini-api/docs/quickstart?lang=python) [NOT YET]
- [] voice synthesis using [Google Text-to-Speech](https://gtts.readthedocs.io/en/latest/index.html)

### Install instructions

```Bash
python3 -m venv --system-site-packages /home/akalinow/scratch/venv
source venv/bin/activate
pip install -r requirements.txt
```

The venv has to use system packages as there are issue witn installing picamera2 from pip.


### Run instructions
```Bash
source venv/bin/activate
python face_follow.py
```
