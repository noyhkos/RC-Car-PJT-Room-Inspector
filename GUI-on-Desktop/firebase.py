import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import paho.mqtt.client as mqtt
import threading

# MQTT 세팅
BROKER = "192.168.137.87"
PORT = 1883
TOPIC_SENSOR = "rcCar/info/sensor"
TOPIC_OBJ = "rcCar/info/object"

def update_sensor(temp, humid):
    data_temp_humid = {
        'temperature': temp,
        'humidity': humid,
    }
    # 데이터를 컬렉션에 추가합니다.
    db.collection('sensor_data').add(data_temp_humid)
    print('temp/humid data successfully added.')

def update_object(obj):
    data_object = {
        'object': obj
    }
    db.collection('objects').add(data_object)
    print('object data successfully added.')

def on_connect_sense(client, userdata, flags, rc):
    if rc == 0:
        print("SENSOR MQTT connected successfully")
        client.subscribe(TOPIC_SENSOR)
    else:
        print(f"SENSOR connection failure, code: {rc}")

def on_connect_object(client, userdata, flags, rc):
    if rc == 0:
        print("OBJECT MQTT connected successfully")
        client.subscribe(TOPIC_OBJ)
    else:
        print(f"OBJECT connection failure, code: {rc}")

def on_message_sense(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[MQTT] {msg.topic} → {payload}")
    temp_str, humid_str = payload.split()
    
    # 수정된 부분: float으로 변환
    temp = float(temp_str)
    humid = float(humid_str)
    
    print(f"temp: {temp}, humidity: {humid}%")
    update_sensor(temp, humid)

    
def on_message_object(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[MQTT] {msg.topic} → {payload}")
    obj = payload
    print(f"object : {obj}")
    update_object(obj)

def commun_sensor():
    client_sense = mqtt.Client()
    client_sense.on_connect = on_connect_sense
    client_sense.on_message = on_message_sense
    client_sense.connect(BROKER, PORT)
    client_sense.loop_forever()

def commun_object():
    client_obj = mqtt.Client()
    client_obj.on_connect = on_connect_object
    client_obj.on_message = on_message_object
    client_obj.connect(BROKER, PORT)
    client_obj.loop_forever()

def clear_collection(collection_name):
    docs = db.collection(collection_name).stream()
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    print(f"At '{collection_name}' collection, {deleted}cnt data deleted.")


# Firebase 인증 정보를 제공하는 서비스 계정 키 파일을 다운로드하고 경로를 설정합니다.
cred = credentials.Certificate('./pjt-rccar-firebase-adminsdk-fbsvc-cf671f02ea.json')
# Firebase 앱 초기화
try:
    # Firestore 데이터베이스를 가져옵니다.
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    clear_collection('sensor_data')
    clear_collection('objects')
    
    # MQTT 통신을 위한 스레드 생성 및 시작
    thread_sensor = threading.Thread(target=commun_sensor)
    thread_sensor.start()
    thread_object = threading.Thread(target=commun_object)
    thread_object.start()
    
    # 메인 스레드가 끝나지 않게 무한 대기
    thread_sensor.join()
    thread_object.join()
    
except ValueError:
    # 이미 초기화된 경우 예외 무시
    print("Firebase app is already initialized.")
    pass
