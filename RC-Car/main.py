from RC_Buzzer import beep_start, beep_stop
from RC_Ultrasound import get_distance
from time import sleep

from RC_Control import run_command, set_cmdmode

import RC_manual
# import RC_voice

from object_detection.object_detect_mqtt import detection_on

# import RC_dht

import threading

warning_on = 0

# THREADINGs ---------------------------------------------------
def warning():
    global warning_on
    while True:
        fwd_dist = get_distance()
        # print(fwd_dist)
        if(fwd_dist<10):
            set_cmdmode(2)
            if(warning_on==0):
                print("[[[[ CRASH WARNING!!!! ]]]]")
                beep_start(0)
                sleep(1)
            warning_on=1
        else: 
            set_cmdmode(0)
            beep_stop()
            warning_on=0
        sleep(0.2)

t1 = threading.Thread(target=RC_manual.INIT)
# t2 = threading.Thread(target=RC_voice.INIT)
t3 = threading.Thread(target=warning)
t4 = threading.Thread(target=detection_on)
# t5 = threading.Thread(target=RC_dht.INIT)

t1.start()
# t2.start()
t3.start()
t4.start()
# t5.start()

t1.join()
# t2.join()
t3.join()
t4.join()
# t5.join()


