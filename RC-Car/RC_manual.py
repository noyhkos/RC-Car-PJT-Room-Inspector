from RC_Control import run_command
import paho.mqtt.client as mqtt
from time import sleep
 
# mqtt-motor-rc control ---------------------------------------
BROKER = "192.168.137.87"
PORT = 1883
TOPIC = "rcCar/control/manual"

cmd_buf = []
 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT 연결 성공(RC Manual Control)")
        client.subscribe(TOPIC)
    else:
        print(f"연결 실패, 코드: {rc}")

def on_message(client, userdata, msg):
    global cmd_buf
    payload = msg.payload.decode()
    print(f"[MQTT] {msg.topic} → {payload}")
    dirc_str, acc_str, brk_str, mode_str = payload.split()
    dirc = int(dirc_str)
    acc = int(acc_str)
    brk = int(brk_str)
    mode = int(mode_str)

    run_command(1, dirc, acc, brk, mode)

# def on_nothing():
#     # while True:
#     #     run_command(1)
#     #     sleep(0.2)

def INIT():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)

    try:
        client.loop_forever()
    finally:
        run_command(0,0,0,0)