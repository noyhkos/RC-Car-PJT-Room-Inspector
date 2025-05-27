import board
import adafruit_dht

dht = adafruit_dht.DHT11(board.D22)

def get_temperature():
    return dht.temperature

def get_humidity():
    return dht.humidity

def close_dht():
    dht.exit()

print(get_temperature())
