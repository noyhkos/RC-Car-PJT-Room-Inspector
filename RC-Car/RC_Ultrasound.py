from gpiozero import DistanceSensor

sensor = DistanceSensor(echo=24, trigger=23, max_distance=2.0)

def get_distance():
    return sensor.distance * 100
