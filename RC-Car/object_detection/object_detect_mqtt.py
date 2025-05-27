import os
import argparse
import time
import cv2
import numpy as np
from picamera2 import Picamera2
# from picamera2.encoders import H264Encoder
# from picamera2.outputs import FileOutput
# from picamera2 import Transform
import importlib.util
import paho.mqtt.client as mqtt

# MQTT settings
BROKER = "192.168.137.87"
PORT = 1883
TOPIC_pub = "rcCar/info/object"
TOPIC_sub = "rcCar/detection/clear"

detected = []

def on_connect_pub(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT PUB 연결 성공(O.D.)")
    else:
        print(f"PUB 연결 실패, 코드: {rc}")
def on_connect_sub(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT SUB 연결 성공(O.D.)")
        client.subscribe(TOPIC_sub)
    else:
        print(f"SUB 연결 실패, 코드: {rc}")

def on_message_sub(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[MQTT] {msg.topic} → {payload}")
    detected.clear()


class VideoStream:
    def __init__(self, resolution=(640, 480)):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": resolution}))
        # self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": resolution},
        #                         transform=Transform(hflip=True, vflip=True)))
        self.picam2.start()
        self.frame = self.picam2.capture_array()

    def read(self):
        self.frame = self.picam2.capture_array()
        return self.frame

    def stop(self):
        self.picam2.stop_()

parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', default='./model')
parser.add_argument('--graph', default='detect.tflite')
parser.add_argument('--labels', default='labelmap.txt')
parser.add_argument('--threshold', default=0.5)
parser.add_argument('--resolution', default='1280x720')
args = parser.parse_args()

MODEL_NAME = args.modeldir
# PATH_TO_CKPT = os.path.join(MODEL_NAME, args.graph)
# PATH_TO_LABELS = os.path.join(MODEL_NAME, args.labels)
PATH_TO_CKPT = os.path.abspath(os.path.join(os.path.dirname(__file__), MODEL_NAME, args.graph))
PATH_TO_LABELS = os.path.abspath(os.path.join(os.path.dirname(__file__), MODEL_NAME, args.labels))

with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]
if labels[0] == '???':
    del(labels[0])

pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

interpreter = Interpreter(model_path=PATH_TO_CKPT)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
floating_model = (input_details[0]['dtype'] == np.float32)
input_mean = 127.5
input_std = 127.5

boxes_idx, classes_idx, scores_idx = 0, 1, 2

resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)
videostream = VideoStream(resolution=(imW, imH))
time.sleep(1)

def detection_on():
    client_pub = mqtt.Client()
    client_sub = mqtt.Client()

    client_pub.on_connect = on_connect_pub

    client_sub.on_connect = on_connect_sub
    client_sub.on_message = on_message_sub

    client_pub.connect(BROKER, PORT, 60)
    client_sub.connect(BROKER, PORT, 60)

    client_pub.loop_start()
    client_sub.loop_start()
    try:
        while True:
            frame = videostream.read()
            frame = videostream.read()
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

            boxes = interpreter.get_tensor(output_details[boxes_idx]['index'])[0]
            classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0]
            scores = interpreter.get_tensor(output_details[scores_idx]['index'])[0]

            for i in range(len(scores)):
                if scores[i] > float(args.threshold):
                    object_name = labels[int(classes[i])]
                    if int(scores[i]*100) > 60:
                        if object_name not in detected:
                            detected.append(object_name)
                            client_pub.publish(TOPIC_pub, object_name)
                            print(f"{object_name} recognized and published")
            print(detected)
            time.sleep(2)

    except KeyboardInterrupt:
        pass
    finally:
        videostream.stop()
        client_pub.loop_stop()
        client_sub.loop_stop()

        client_pub.disconnect()
        client_sub.disconnect()

# detection_on()