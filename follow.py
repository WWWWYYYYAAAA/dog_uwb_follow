import mc_sdk_py
import serial
import time
from ctypes import c_int32
import math
app=mc_sdk_py.HighLevel()
print("Initializing...")
app.initRobot("192.168.168.99",43988, "192.168.168.168") #local_ip, local_port, dog_ip
time.sleep(7)
print("Initialization completed")
ser = serial.Serial(port="/dev/ttyACM0", baudrate=921600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

if ser.isOpen():
    print("串口已打开")
else:
    print("串口打开失败")

kpx = 1.0
kdx = 0.8
kpa = 1.0
kda = 0.8

dist_target = 1.4
v_limit = 1.0
a_limit = 0.8
def main():
    app.standUp()
    time.sleep(4)
    Vx = 0
    Va = 0
    dist_raw = 0
    angle_raw = 0
    last_dist_raw = 0
    last_angle_raw = 0
    while 1:
        data = ser.read(150)
        if (len(ser)>140):
            for i in range(len(data)-35):
                if data[i] == 0x55 and data[i+1]==0x07 and data[i+int(data[i+2])]==0x55 and data[i+int(data[i+2])+1]==0x07:
                    dist_raw = c_int32((65536*data[i+25] + 256*data[i+24] + data[i+23])<<8).value/256/1000
                    angle_raw = c_int32((256*data[i+27] + data[i+26])<<16).value/256/256/100
        # print("\r", dist_raw/1000, angle_raw/100, end="")
        if(abs(angle_raw)>7.5):
            Va = kpa*(angle_raw/180*math.pi-0)+kda*(last_angle_raw-angle_raw)/180*math.pi
        else:
            Va = 0
        if dist_raw>1.75 or dist_raw<1.0:
            Vx = kpx*(dist_raw-dist_target)+kdx*(last_dist_raw-dist_raw)
        else:
            Vx = 0
            
        if Vx < -v_limit:
            Vx = -v_limit
        elif Vx > v_limit:
            Vx = v_limit
            
        if Va < -a_limit:
            Va = -a_limit
        elif Va > a_limit:
            Va = a_limit
        
        if(abs(Vx)<0.2):
            Vx = 0
        if(abs(Va)<0.1):
            Va = 0
        
        if Va < 0 and Va > -0.2:
            Va = -0.2
        if Va > 0 and Va < 0.2:
            Va = 0.2
            
        if Vx < 0 and Vx > -0.4:
            Vx = -0.4
        if Va > 0 and Vx < 0.4:
            Vx = 0.4
            
        print("\r", dist_raw, angle_raw, "|", Vx, Va, end="")
        last_dist_raw = dist_raw
        last_angle_raw = angle_raw
        app.move(Vx, 0, Va)
        time.sleep(0.04)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        app.passive()
        time.sleep(2)

   