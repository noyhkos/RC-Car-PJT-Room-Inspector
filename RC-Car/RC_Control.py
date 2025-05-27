from RC_Motor import drv, turn

velocity = 0
cmd_mode = 0 # 1:voice, 2:crashAvoid

def set_velc(acc, brk, mode):
    global velocity
    if(acc==1 and brk==1):
        velocity=0
    elif(brk==0):
        velocity -= 50
        if(mode==-1 and velocity<-50):
            velocity = -50
        if(velocity<-200):
            velocity=-200
    elif(acc==0):
        velocity += 50
        if(mode==-1 and velocity>50):
            velocity = 50
        if(velocity>200):
            velocity=200

def set_cmdmode(val):
    global cmd_mode 
    cmd_mode = val

# mode => 0:stop, 1:manual, 2:voice
def run_command(mode, arg1=0, arg2=1, arg3=1, arg4=1):
    global velocity
    if(mode == 0):
        drv(0)
        turn(0)
    elif(mode == 1):
        if(cmd_mode==1): return
        # arg1 = dirc, arg2 = acc, arg3 = brk, arg4 = mode(sports/echo)
        turn(arg1)
        set_velc(arg2, arg3, arg4)
        diff_match = int( (abs(arg1/100.0)**15) * 60 )
        if(velocity>0):
            velocity += diff_match
        elif(velocity<0):
            velocity -= diff_match
        drv(velocity)
        if(cmd_mode==2 and velocity>0): 
            velocity = 0
            drv(0)
        print("Velocity: ", velocity)
    # elif(mode == 2):
    #     # if(cmd==1):
    #     # elif(cmd==2):
    #     # elif(cmd==3):
    #     # elif(cmd==4):
    #     # elif(cmd==5):
    #     # elif(cmd==6):
    #     # elif(cmd==7):
    # else:

    running = 0