import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QListView
from PySide6.QtCore import QStringListModel, QTimer, QObject, Signal, Slot
from PySide6.QtGui import QPixmap
import pyqtgraph as pg
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from ui_form import Ui_MainWindow
import paho.mqtt.client as mqtt
import threading

objects = []
humidity = []
temp = []
response = ''
infer_log = ''
GOOGLE_API_KEY = "AIzaSyA0rW2LbTuF2vNHHl7EO0FUSNvKn4qaphY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
main_window_instance = None

# MQTT 세팅
BROKER = "192.168.137.87"
PORT = 1883
TOPIC_PUBLISH = "rcCar/detection/clear"  # 송신용
TOPIC_SUBSCRIBE = "rcCar/detection/reset"  # 수신용

# Firebase 설정
cred = credentials.Certificate('./pjt-rccar-firebase-adminsdk-fbsvc-cf671f02ea.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Qt 시그널을 위한 클래스
class MQTTSignals(QObject):
    reset_requested = Signal()

# Firebase 실시간 업데이트를 위한 시그널 클래스
class FirebaseSignals(QObject):
    objects_updated = Signal(list)  # 사물 목록이 업데이트되었을 때
    sensors_updated = Signal(list, list)  # 센서 데이터가 업데이트되었을 때 (temp, humidity)

mqtt_signals = MQTTSignals()
firebase_signals = FirebaseSignals()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT connected successfully")
        client.subscribe(TOPIC_SUBSCRIBE)
        print(f"Subscribed to topic: {TOPIC_SUBSCRIBE}")
    else:
        print(f"MQTT connection failure, code: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip()
    print(f"[MQTT] {msg.topic} → {payload}")
    
    if msg.topic == TOPIC_SUBSCRIBE and payload == "reset requested":
        print("Reset signal received, emitting Qt signal...")
        mqtt_signals.reset_requested.emit()

# MQTT 클라이언트 (deprecation warning 해결)
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    try:
        mqtt_client.connect(BROKER, PORT, 60)
        mqtt_client.loop_start()
        print("MQTT client started")
    except Exception as e:
        print(f"MQTT connection error: {e}")

# Firebase 실시간 리스너 함수들
def on_objects_snapshot(doc_snapshot, changes, read_time):
    """Objects 컬렉션 변경사항을 실시간으로 감지"""
    global objects
    print(f"[FIREBASE] Objects collection changed! Changes: {len(changes)}")
    
    # 변경사항 처리
    for change in changes:
        if change.type.name == 'ADDED':
            doc_data = change.document.to_dict()
            obj = doc_data.get('object')
            if obj and obj not in objects:
                objects.append(obj)
                print(f"[+] Added object: {obj}")
        elif change.type.name == 'REMOVED':
            doc_data = change.document.to_dict()
            obj = doc_data.get('object')
            if obj and obj in objects:
                objects.remove(obj)
                print(f"[-] Removed object: {obj}")
        elif change.type.name == 'MODIFIED':
            print(f"[*] Modified object document")
    
    # UI 업데이트 시그널 발생
    firebase_signals.objects_updated.emit(objects.copy())

def on_sensors_snapshot(doc_snapshot, changes, read_time):
    """Sensor_data 컬렉션 변경사항을 실시간으로 감지"""
    global temp, humidity
    print(f"[SENSOR] Sensor data collection changed! Changes: {len(changes)}")
    
    # 전체 데이터 다시 로드 (간단한 방법)
    temp.clear()
    humidity.clear()
    
    for doc in doc_snapshot:
        data = doc.to_dict()
        temp.append(data.get('temperature', 0))
        humidity.append(data.get('humidity', 0))
    
    print(f"[DATA] Updated sensor data - Temp: {len(temp)}, Humidity: {len(humidity)}")
    
    # UI 업데이트 시그널 발생
    firebase_signals.sensors_updated.emit(temp.copy(), humidity.copy())

def start_firebase_listeners():
    """Firebase 실시간 리스너 시작"""
    try:
        print("[FIREBASE] Starting Firebase real-time listeners...")
        
        # Objects 컬렉션 리스너
        objects_ref = db.collection('objects')
        objects_watch = objects_ref.on_snapshot(on_objects_snapshot)
        
        # Sensor_data 컬렉션 리스너
        sensors_ref = db.collection('sensor_data')
        sensors_watch = sensors_ref.on_snapshot(on_sensors_snapshot)
        
        print("[OK] Firebase listeners started successfully!")
        return objects_watch, sensors_watch
        
    except Exception as e:
        print(f"[ERROR] Firebase listeners start error: {e}")
        return None, None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.plot_widget = self.ui.Graph

        # 리스트뷰에 모델 연결
        self.model = QStringListModel()
        self.ui.listView.setModel(self.model)

        # 버튼 연결
        self.ui.pushButton.clicked.connect(self.run_infer)
        self.ui.pushButton_2.clicked.connect(self.reset_all)
        
        # MQTT 시그널 연결
        mqtt_signals.reset_requested.connect(self.reset_all)
        
        # Firebase 실시간 업데이트 시그널 연결
        firebase_signals.objects_updated.connect(self.on_objects_updated)
        firebase_signals.sensors_updated.connect(self.on_sensors_updated)

        self.plot_graph()
        self.update_object_list(["초기값: 없음"])
        self.update_location("장소 없음")
        
        print("[INFO] MainWindow initialized!")

    @Slot(list)
    def on_objects_updated(self, new_objects):
        """실시간으로 사물 목록이 업데이트되었을 때 호출"""
        print(f"[UI] Updating objects: {new_objects}")
        if new_objects:
            self.update_object_list(new_objects)
        else:
            self.update_object_list(["감지된 사물이 없습니다."])

    @Slot(list, list)
    def on_sensors_updated(self, new_temp, new_humidity):
        """실시간으로 센서 데이터가 업데이트되었을 때 호출"""
        print(f"[UI] Updating sensors - Temp: {len(new_temp)}, Humidity: {len(new_humidity)}")
        # 그래프 업데이트
        self.plot_graph()

    def plot_graph(self):
        x = list(range(len(temp)))

        self.plot_widget.clear()
        self.plot_widget.enableAutoRange(axis='xy', enable=True)

        if temp and humidity:
            self.plot_widget.plot(x, temp, pen=pg.mkPen(color='r', width=2), name="Temperature")
            self.plot_widget.plot(x, humidity, pen=pg.mkPen(color='b', width=2), name="Humidity")

        self.plot_widget.setTitle("온도 및 습도 추이")
        self.plot_widget.setLabel('left', '값')
        self.plot_widget.setLabel('bottom', '시간')
        self.plot_widget.addLegend()

    def run_infer(self):
        global objects, temp, humidity, response, infer_log

        print("[AI] Starting inference...")
        
        # 현재 데이터로 추론 (실시간으로 이미 업데이트된 상태)
        print(f"[DATA] Current data - Objects: {len(objects)}, Temp: {len(temp)}, Humidity: {len(humidity)}")

        # 장소 추론
        info = '이 방에 있는 물건으로는 '
        if objects:
            for i in range(len(objects)):
                info += objects[i]
                if i == len(objects) - 1:
                    info += '가 있습니다.'
                else:
                    info += ', '
        else:
            info += '아무것도 없습니다.'

        if not temp or not humidity:
            info += ' 현재 온도와 습도 정보가 없습니다.'
            self.update_location(info)
            return

        temp_avg = sum(temp) / len(temp)
        humid_avg = sum(humidity) / len(humidity)
        info += f' 온도는 {temp_avg:.1f}도, 습도는 {humid_avg:.1f}%입니다. 위 정보를 바탕으로 이 방이 어떤 방인지 논리적으로 한국말로 추론해주세요.'

        try:
            response = model.generate_content(info)
            self.update_location(response.text)
            print("[OK] AI inference completed")
        except Exception as e:
            print(f"[ERROR] AI infer error: {e}")
            self.update_location("추론 중 오류가 발생했습니다.")

    def update_object_list(self, items):
        self.model.setStringList(items)

    def update_location(self, location_str):
        self.ui.textBrowser_4.setText(location_str)
    
    @Slot()
    def reset_all(self):
        global objects, temp, humidity, response, infer_log
        print("[RESET] ===== RESET_ALL() EXECUTING =====")
        
        # 데이터 초기화
        objects.clear()
        temp.clear()
        humidity.clear()
        response = ''
        infer_log = ''
        print("[RESET] Global data cleared")

        # UI 초기화
        self.plot_widget.clear()
        self.update_object_list(["초기값: 없음"])
        self.update_location("장소 없음")
        print("[RESET] UI Initialized")

        # Firestore 데이터 삭제
        try:
            print("[RESET] Starting Firebase data deletion...")
            
            # sensor_data 컬렉션 삭제
            docs = db.collection('sensor_data').stream()
            sensor_count = 0
            for doc in docs:
                doc.reference.delete()
                sensor_count += 1

            # objects 컬렉션 삭제
            docs = db.collection('objects').stream()
            object_count = 0
            for doc in docs:
                doc.reference.delete()
                object_count += 1

            print(f"[OK] Firebase data cleared - Sensors: {sensor_count}, Objects: {object_count}")
        except Exception as e:
            print(f"[ERROR] Firebase data clear error: {e}")

        # MQTT 메시지 전송
        try:
            mqtt_client.publish(TOPIC_PUBLISH, "reset requested")
            print("[MQTT] MQTT reset message sent")
        except Exception as e:
            print(f"[ERROR] MQTT message sent failure: {e}")
            
        print("[RESET] ===== RESET_ALL() COMPLETED =====")

def main():
    global main_window_instance
    
    app = QApplication(sys.argv)
    
    # MQTT 시작
    start_mqtt()
    
    # 메인 윈도우 생성
    main_window_instance = MainWindow()
    main_window_instance.show()
    
    # Firebase 실시간 리스너 시작
    objects_watch, sensors_watch = start_firebase_listeners()
    
    print("[APP] Application started successfully!")
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("[EXIT] Program exited by user")
    finally:
        print("[CLEANUP] Cleaning up...")
        # Firebase 리스너 정리
        if objects_watch:
            objects_watch.unsubscribe()
        if sensors_watch:
            sensors_watch.unsubscribe()
        # MQTT 정리
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()