# RC카 - Room Inspector 프로젝트
    
## 개요
### AI를 활용한 공간 분석 원격 이동체
1. 원격 조종으로 공간을 탐사
2. 획득한 정보를 데이터 베이스에 저장
3. 업로드 된 정보를 바탕으로 AI 공간 분석 제공

## 하드웨어 스펙
1. RC Car
- *Raspberry Pi 5*
- UGEEK Stepper Motor HAT v0.2
- Pi CAM
- Ultrasound Module(HC-SR04)
- Buzzer Module
- 16V/50V Poser Supplier
 
- *Raspberry Pi Zero*
- dht11
    
2. Joystick
- ESP32(Nodemce32s)
- Joystick Module
    
3. OLED-Glass
- Raspberry Pi Zero
- OLED Module

## 시스템 아키텍쳐
사진 첨부

## 주요 기능
1. RC Car - Joystick
- Sport/Echo 모드로 상황에 맞는 주행 질감
- 코너주행 가속 Differectial Matching

2. OpenCV Object Detection
- Tensor Flow - Lite 활용한 Object Detection

3. MQTT 통신
- RcCar, OLED-Glass, Joystick, GUI 단말 간의 유연한 통신
- MQTT Topics
1) rcCar/control/manual -> Joiystick 컨트롤 커맨드 전송
2) rcCar/info/sensor -> RP Zero 온습도 전송
3) rcCar/info/object -> RC 카 에서 새롭게 인식한 사물 전송
4) rcCar/detection/reset -> DB 및 GUI 초기화
5) rcCar/detection/clear -> rcCar Object List clear cmd

4. AI 데이터 분석
-  Gemini API를 활용하여 획득한 정보를 바탕으로 공간 정보 분석

