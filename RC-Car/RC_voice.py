from RC_Control import run_command, set_cmdmode
import paho.mqtt.client as mqtt
 
# mqtt-motor-rc control ---------------------------------------
BROKER = "192.168.137.87"
PORT = 1883
TOPIC = "rcCar/control/voice"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT 연결 성공")
        client.subscribe(TOPIC)
    else:
        print(f"연결 실패, 코드: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[MQTT] {msg.topic} → {payload}")
    cmd = int(payload)
    print("voice command: ", cmd)
    set_cmdmode(1)
    run_command(2, cmd)
    set_cmdmode(0)

def INIT():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)

    try:
        client.loop_forever()
    finally:
        run_command(0)
        
