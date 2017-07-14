
#encoding=utf-8
import serial  
import datetime
import time
from struct import *

# Serial input format:
# 0x42 0x4d CMD DATAH DATAL LRCH LRCL
# 0x42 0x4d 0xe3 0x00 0x00  ( 0x172 )
# LRCH*256+LRCL = sum(0x42 0x4d CMD DATAH DATAL LRCH)
# In fact, the DS-CO2-20 has only one command to input
# there fore, just keep the init_cmd 

#print("Opening Serial Port...\n)"
ser = serial.Serial("/dev/ttyAMA0", 9600)  

init_cmd =[ 0x42, 0x4d, 0xe3, 0x00, 0x00, 1, 114]
time.sleep(1)
for c in init_cmd:
    ser.write(chr(c))

time.sleep(2)
ser.flush()

def main(): 
    cnt = 0
    while True:  
        count = ser.inWaiting()  
        if count >= 12:  
            recv = ser.read(count)
            sh8 = recv[2]
            sl8 = recv[3]
            h8 = recv[4]
            l8 = recv[5]
            #print(str(ord(sh8)*256 + ord(sl8))+" size")
            print(str(ord(h8)*256 + ord(l8))+" PPM,"+ str(datetime.datetime.utcnow().isoformat()) )
            ser.flushInput()  
        time.sleep(0.1)  
        cnt = cnt + 1
        if cnt >= 2:
            break
if __name__ == '__main__':  
    try:  
        main()  
    except KeyboardInterrupt:  
        if ser != None:  
            ser.close()  
