from DHT11 import get_temperature, get_humidity, close_dht
import paho.mqtt.client as mqtt
from time import sleep
BROKER = "192.168.137.87"
PORT = 1883
TOPIC = "rcCar/info/sensor"
 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT 연결 성공(dht11)")
        client.subscribe(TOPIC)
    else:
        print(f"연결 실패, 코드: {rc}")

def INIT():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(BROKER, PORT, 60)

    client.loop_start()

    try:
        while True:
            temp = get_temperature()
            humd = get_humidity()
            msg = str(temp) + " " + str(humd)
            try:
                client.publish(TOPIC, msg)
                print("temp, humd: ", msg)
            except:
                print("ERROR: dht")
            sleep(5)

    finally:
        print("dht fail")
        close_dht()
        client.loop_stop()
        client.disconnect()
# INIT()