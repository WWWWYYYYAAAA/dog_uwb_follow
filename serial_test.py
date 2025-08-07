import serial
import time
from ctypes import c_int32
# 打开 COM17，将波特率配置为115200，数据位为8，无校验位，停止位为1，读超时时间为1秒
ser = serial.Serial(port="/dev/ttyACM0", baudrate=921600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

if ser.isOpen():
    print("串口已打开")
else:
    print("串口打开失败")
    
while 1:
    data = ser.read(100)
    dist_raw = 0
    angle_raw = 0
    for i in range(len(data)-35):
        if data[i] == 0x55 and data[i+1]==0x07 and data[i+int(data[i+2])]==0x55 and data[i+int(data[i+2])+1]==0x07:
            dist_raw = c_int32((65536*data[i+25] + 256*data[i+24] + data[i+23])<<8).value/256
            angle_raw = c_int32((256*data[i+27] + data[i+26])<<16).value/256/256
    print("\r", dist_raw/1000, angle_raw/100, end="")
    time.sleep(0.1)