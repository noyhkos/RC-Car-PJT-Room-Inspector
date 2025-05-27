import paho.mqtt.client as mqtt

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# OLED 설정
oled_reset = digitalio.DigitalInOut(board.D24)
WIDTH = 128
HEIGHT = 64
spi = board.SPI()
oled_cs = digitalio.DigitalInOut(board.D23)
oled_dc = digitalio.DigitalInOut(board.D25)
oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, oled_dc, oled_reset, oled_cs)

BROKER = "192.168.137.87"
PORT = 1883
TOPIC = "rcCar/info/object"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT 연결 성공(RC Manual Control)")
        client.subscribe(TOPIC)
    else:
        print(f"연결 실패, 코드: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(payload)
    oled.fill(0)
    oled.show()

    # 1. 더 큰 캔버스에 텍스트 그리기
    text = payload
    font = ImageFont.load_default()
    temp_width = 200
    temp_height = 64
    temp_image = Image.new("1", (temp_width, temp_height))  # 충분히 큰 공간
    draw = ImageDraw.Draw(temp_image)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    draw.text(((temp_width - text_w) // 2, (temp_height - text_h) // 2), text, font=font, fill=255)

    # 2. 회전 및 반전
    rotated = temp_image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)

    # 3. 중앙에서 128x64 크기로 crop
    rotated_w, rotated_h = rotated.size
    left = (rotated_w - WIDTH) // 2
    top = (rotated_h - HEIGHT) // 2
    cropped = rotated.crop((left, top, left + WIDTH, top + HEIGHT))

    # 4. OLED 출력
    oled.image(cropped)
    oled.show()



def INIT():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    try:
        client.loop_forever()
    finally:
        client.loop_stop()
        client.disconnect()

INIT()