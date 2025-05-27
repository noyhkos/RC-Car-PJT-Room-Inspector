// <MQTT header> --------------------------------------
#include "EspMQTTClient.h"
EspMQTTClient client(
  "wifiID",    //wifi SSID
  "wifiPW",      //wifi password
  "192.168.137.87",    // MQTT Broker server ip
  "joystick",          // MQTT Username
  "",     // MQTT pw
  "controler1",     //device name, 장치를 구별하는 용도
  1883             
);
char *topic = "rcCar/control/manual";
char *topic2 = "rcCar/detection/reset";
String msg;
// -----------------------------------------------------

// <joystick header> -----------------------------------
int Xpin = 39;
int Ypin = 34;
int clkPin = 13;
int xin = 0;
int yin = 0;
// int velc = 0;
int dirc = 0;
int clk_prev = 0;
int clk_new = 0;
// -----------------------------------------------------

// <buttons header> -----------------------------------
int btn1_pin = 27;
int btn2_pin = 12;
int btn3_pin = 14;
int btn1_state = 0;
int btn2_state = 0;
int btn3_prev = 0;
int btn3_new = 0;
int mode = 1;
// -----------------------------------------------------

// <led header> -----------------------------------
int led1 = 32;
int led2 = 33;
// -----------------------------------------------------

void tx(){
  Serial.println("tx");
  client.publish(topic, msg);
}
void rx(){}
void tx2(){
  Serial.println("tx2");
  client.publish(topic2, "reset requested");
}

void setup() {
  Serial.begin(115200);

  // led
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  
  // buttons
  pinMode(btn1_pin, INPUT_PULLUP);
  pinMode(btn2_pin, INPUT_PULLUP);
  // pinMode(btn3_pin, INPUT_PULLUP);
  pinMode(clkPin, INPUT_PULLUP);

  // joystick
  analogReadResolution(9);

  //mqtt-----------------------
  client.enableDebuggingMessages(); 
  client.enableHTTPWebUpdater(); 
  client.enableOTA(); 
  client.enableLastWillMessage("TestClient/lastwill", "I am going offline");
  //mqtt-------------------------
}

void onConnectionEstablished(){
  //client.loop() 에 의해 호출되는 API
}

void loop() {
  xin = analogRead(Xpin);
  yin = analogRead(Ypin);
  // velc = ((-yin+255)/20)*20;
  dirc = (((xin*200/500)-100)/10)*10;

  btn1_state = digitalRead(btn1_pin);
  btn2_state = digitalRead(btn2_pin);
  btn3_new = digitalRead(btn3_pin);
  if(btn3_prev==0 && btn3_new==1)tx2();
  btn3_prev = btn3_new;

  clk_new = digitalRead(clkPin);
  if(clk_prev==0 && clk_new==1)mode*=-1;
  clk_prev = clk_new;

  if(mode==-1){
    digitalWrite(led1, HIGH);
    digitalWrite(led2, LOW);
  } else {
    digitalWrite(led1, LOW);
    digitalWrite(led2, HIGH);
  }

  Serial.println("=============================");
  Serial.print("btn1: ");
  Serial.print(btn1_state);
  Serial.print("  btn2: ");
  Serial.print(btn2_state);
  Serial.print("  btn3: ");
  Serial.print(btn3_new);
  Serial.print("  clk: ");
  Serial.print(clk_new);
  Serial.print("  mode: ");
  Serial.println(mode);

  msg = String(dirc) + " " + String(btn1_state) + " " + String(btn2_state) + " " + String(mode);
  Serial.println(msg);
  tx();
  client.loop();

  delay(100);
}
