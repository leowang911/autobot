import RPi.GPIO as IO
import time
import smbus
import time
import math
from math import pi

IO.setwarnings(False)
IO.setmode(IO.BCM)

#IR sensor
IO.setup(5,IO.IN) 
IO.setup(6,IO.IN) 
IO.setup(13,IO.IN) 
IO.setup(19,IO.IN) 
IO.setup(26,IO.IN) 

#IR target finder
IO.setup(21,IO.IN) 
IO.setup(16,IO.IN) 
IO.setup(20,IO.IN) 

#shooting
IO.setup(9,IO.IN) 

#motor 1
IO.setup(14,IO.OUT) 
IO.setup(15,IO.OUT)

#motor 2
IO.setup(23,IO.OUT)
IO.setup(24,IO.OUT)

IO.setup(9,IO.OUT)

#pwm pin setup
IO.setup(18,IO.OUT)
pwm=IO.PWM(18,100)
pwm.start(30)

#physical property
RPM=140
D=3.1*2.54
C=pi*D
d=(4.5+0.75)*2.54

#setting up the compass
bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x1e
REGISTER_CRA_REG_M = 0x00
REGISTER_MR_REG_M = 0x02
REGISTER_OUT_X_H_M = 0x03
REGISTER_OUT_X_LH_M = 0x04
REGISTER_OUT_Z_H_M = 0x05
REGISTER_OUT_Z_L_M = 0x06
REGISTER_OUT_Y_L_M = 0X08
REGISTER_OUT_Y_H_M = 0X07

def getX():
        xl = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_OUT_X_LH_M)
        xh = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_OUT_X_H_M)
        x =  (xh << 8) | xl
        if x >= 32768:
            x = x ^ 65535
            x += 1
            return -x
        return x

def getZ():
        zl = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_OUT_Z_L_M)
        zh = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_OUT_Z_H_M)
        z = (zh << 8) | zl
        if z >= 32768:
            z = z ^ 65535
            z += 1
            return -z
        return z

def getY():
        yl = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_OUT_Y_L_M)
        yh = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_OUT_Y_H_M)
        y = (yh << 8) | yl
        if y >= 32768:
            y = y ^ 65535
            y += 1
            return -y
        return y

bus.write_byte_data(DEVICE_ADDRESS, REGISTER_CRA_REG_M, 0x90)
bus.write_byte_data(DEVICE_ADDRESS, REGISTER_MR_REG_M, 0)


def compass_read():
        x = getX()
        y = getY()
        z = getZ()
        dir=math.degrees(math.atan2(y, x))
        print(dir)
        time.sleep(0.3)
		return dir

def inrange(range_mid,direction):
		
        inran=1
		if (0<=range_mid<90):
			if(range_mid-90<=direction<range_mid+90):
				inran=1
			else:
				inran=0
		if (90<=range_mid<=180):
			if(range_mid-90<=direction<=180 | -180<direction<=range_mid+90-360):
				inran=1
			else:
				inran=0
		if (-90<=range_mid<0):
			if (range_mid-90<=direction<range_mid+90):
				inran=1
			else:
				inran=0
		if (-180<=range_mid<-90):
			if (-180<=direction<range_mid+90 | 360+range_mid-90<=direction<180):
				inran=1
			else:
				inran=0

		return inran

def dis_time(distance):
        t=distance/C*1/RPM*60
        return t

def ang_time(angle):
        angl=angle/180*pi
        t=angl*d/2/C*1/RPM*60
        return t

def forward():
        print('forward')
        IO.output(14,True) 
        IO.output(15,False) 
        IO.output(23,True) 
        IO.output(24,False)
        return

def left(angle):
        print('left',angle,'degree')
        IO.output(15,True) 
        IO.output(14,False) 
        IO.output(24,False) 
        IO.output(23,True) 
        t=ang_time(angle)
        time.sleep(t)
        return

def right(angle):
        print('right',angle,'degree')
        IO.output(15,False)
        IO.output(14,True)
        IO.output(24,True)
        IO.output(23,False)
        t=ang_time(angle)
        time.sleep(t)
        return

def back(distance):
        print('back',distance,'cm')
        t=dis_time(distance)
        IO.output(14,False) 
        IO.output(15,True) 
        IO.output(23,False) 
        IO.output(24,True)
        time.sleep(t) 
        return

def stop(tim):
        print('stop',tim,'s')
        IO.output(14,True) 
        IO.output(15,True) 
        IO.output(23,True) 
        IO.output(24,True)
        time.sleep(tim) 
        return


def obstacle_avoid(sensor1,sensor2,sensor3,sensor4,sensor5):
        if (sensor1==True):
                if (sensor2==True):
                        if (sensor3==True):
                                if (sensor4==True):
                                        if(sensor5==True):
                                                forward()
                                                time.sleep(0.1)
                                        else:
                                                right(30)
                                                time.sleep(0.1)
                                else:
                                        back(5)
                                        time.sleep(0.3)
                                        right(30)
                                        time.sleep(0.1)

                        else:
                                back(5)
                                time.sleep(0.3)
                                right(60)
                                time.sleep(0.3)
            	else:
                        back(5)
                        time.sleep(0.3)
                        left(60)
                        time.sleep(0.3)
        else:
                left(30)
                time.sleep(0.1)
        return

def shoot():
        IO.output(9,True)


inti_dir = compass_read()   #setup inital direction
shootcount = 0


while 1:
        
        IO.output(9,False)      #load shooting mechanism

        sensor2=IO.input(5)		#ir avoidance sensors
        sensor5=IO.input(6)
        sensor3=IO.input(13)
        sensor4=IO.input(19)
        sensor1=IO.input(26)
        
        target1=IO.input(21)	#ir tracking sensors
        target2=IO.input(16)
        target3=IO.input(20)

        direction = compass_read()

        if(target3==False):
                if(target2==False):
                        if(target1==False):
                                if (inrange(inti_dir,direction)=True): #see if the bot is facing forward
                                		obstacle_avoid(sensor1,sensor2,sensor3,sensor4,sensor5)
                                else:
                                		right(1)
                                		time.sleep(0.1)
                                		print('change direction to forward') 
                        else:
                                if (shootcount==0):
                                        print('target lock')
                                        stop(1)
                                        shoot()
                                        shootcount=1
                                        if (inti_dir<=0):               #switch direction 180 degrees to go homebase
                                        	inti_dir=inti_dir+180
                                        else:
                                        	inti_dir=inti_dir-180
                                else:
                                        print('homebase lock')
                                        forward()

                else:
                        print('target on left')
                        left(90)
                        time.sleep(0.3)
        else:
                print('target on right')
                right(90)
                time.sleep(0.3)




