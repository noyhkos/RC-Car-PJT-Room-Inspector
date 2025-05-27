from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
from time import sleep

lst = [242.32, 352.34, 810.2]
lst2 = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 466.16, 493.88, 1046.5]

b = TonalBuzzer(17)

def beep_start(val):
    b.play(lst2[val])
    return

def beep_stop():
    b.stop()
    return
