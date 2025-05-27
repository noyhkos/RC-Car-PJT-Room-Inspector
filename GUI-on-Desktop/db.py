import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import sys

GOOGLE_API_KEY = "your-google-api-key" 
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# Firebase 인증 정보를 제공하는 서비스 계정 키 파일을 다운로드하고 경로를 설정합니다.
cred = credentials.Certificate('./pjt-rccar-firebase-adminsdk-fbsvc-cf671f02ea.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

temp = []
humidity = []
objects = []

docs_sensor = db.collection('sensor_data').stream()
for doc in docs_sensor:
    data = doc.to_dict()
    temp.append(data.get('temperature', 0))
    humidity.append(data.get('humidity', 0))

# 객체 데이터 수집
docs_object = db.collection('objects').stream()
for doc in docs_object:
    data = doc.to_dict()
    obj = data.get('object')
    if obj and obj not in objects:
        objects.append(obj)


info = '이 방에 있는 물건으로는 '
for i in range(len(objects)):
    info += objects[i]
    if i == len(objects) - 1:
        info += '가 있습니다.'
    else:
        info += ', '

temp_avg = sum(temp) / len(temp)
humid_avg = sum(humidity) / len(humidity)
info += f' 온도는 {temp_avg:.1f}도, 습도는 {humid_avg:.1f}%입니다. 위 정보를 바탕으로 이 방이 어떤 방인지 논리적으로 한국말로 추론해주세요.'

response = model.generate_content(info)

sys.stdout.reconfigure(encoding='utf-8')
print(response.text)