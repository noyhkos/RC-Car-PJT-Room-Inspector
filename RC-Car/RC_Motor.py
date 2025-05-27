from Raspi_MotorHAT import Raspi_MotorHAT

LEFT_ITR = 100
MID_ITR = 250
RIGHT_ITR = 350

mh = Raspi_MotorHAT(addr=0x6f, freq=60)

dc = mh.getMotor(2)
servo = mh._pwm

dc.setSpeed(0)
# servo.setPWMFreq(60)

def drv(val):
    if(val>255):
        dc.setSpeed(250)
        dc.run(Raspi_MotorHAT.FORWARD)
    if(val>0):
        dc.setSpeed(val)
        dc.run(Raspi_MotorHAT.FORWARD)
    elif(val<-255):
        dc.setSpeed(250)
        dc.run(Raspi_MotorHAT.BACKWARD)
    elif(val<0):
        dc.setSpeed(-1*val)
        dc.run(Raspi_MotorHAT.BACKWARD)
    else:
        dc.setSpeed(0)
        dc.run(Raspi_MotorHAT.RELEASE)

def turn(val):
    # global LEFT_ITR, MID_ITR, RIGHT_ITR
    if(val<-100):
        servo.setPWM(0,0,LEFT_ITR)
    elif(val<0):
        temp  = val * ((MID_ITR-LEFT_ITR)/100)
        temp = MID_ITR + temp
        print("left, ", temp)
        servo.setPWM(0,0,int(temp))
    elif(val==0):
        servo.setPWM(0,0,MID_ITR)
    elif(val<100):
        temp  = val * ((RIGHT_ITR - MID_ITR)/100)
        temp = MID_ITR + temp
        print("right, ", temp)
        servo.setPWM(0,0,int(temp))
    else:
        servo.setPWM(0,0,RIGHT_ITR)


