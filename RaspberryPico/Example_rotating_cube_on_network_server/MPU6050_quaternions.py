# Micropython version
# Create a MPU object with running dmp, extract quaternion data from dmp
# packets and send this to a remote host over the network for display
# This requires a Pico W to send data over Wifi.
# Ron Meiburg feb 2024

from machine import Pin, I2C
import MPUregisters as MPUreg
from bus import bus
from MPU6050 import MPU6050_DMP
from secrets import *
import network
import usocket
import json
import utime

def two_bytes_to_int(d1,d2) -> int:
    value = d1*256 + d2    
    if value >= 0x8000:
        value -= 65536
    return value


led         = Pin("LED", Pin.OUT)
led.off()
#
# Set up network connection
#
print("set up network")
wlan = network.WLAN(network.STA_IF)
SERVERIP    = "192.168.10.130"  # When using another device for display
SERVERPORT  =  5000             # Choose your network port
#SSID      Define this in secrets file
#PASSWD    Define this in secrets file

status = wlan.ifconfig()
print( 'Connected to ' + SSID + '. ' + 'Device IP: ' + status[0] )
print('creating socket')
sockaddr = usocket.getaddrinfo(SERVERIP, SERVERPORT)[0][-1]
# Now you can use that address
print("Network details: ",sockaddr)
# Create DGRAM UDP socket
sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
sock.connect(sockaddr)

# Define i2c specifics for the Pico
busnum  = 0         # bus number. Can only be 0, 1
sdaPIN  = Pin(16)   # data pin for i2c bus
sclPIN  = Pin(17)   # clock pin for i2c bus

# create bus object
i2cbus = bus(busnum,sda=sdaPIN, scl=sclPIN, freq=50000)  # use 50kHz so we can track with analyzer
print(i2cbus)
# create mpu object with full dmp functionality
mpu = MPU6050_DMP(i2cbus)
print(f"mpu available on i2c bus address: 0x{int(mpu.who_am_i()):x}")

# load the dmp image and switch it on
mpu.dmp_initialize()
mpu.set_dmp_enabled(True)

if mpu.get_dmp_enabled():
    print("digital motion processor enabled")
    led.on()  #flag all is working
else:
    print("digital motion processor not enabled")

dmp_packet_length = mpu.dmp_get_fifo_packet_size()


scale = 16384.0


while True:
#for _ in range(100):
    utime.sleep_ms(30)   # delay so not to overload the network
    data = mpu.get_current_fifo_packet(dmp_packet_length)
    b = [j for j in data]

# Pull the quaternion components out of the dmp output
# NB the components of b are actually already integers

    q1 = (two_bytes_to_int(b[0], b[1]))/scale
    q2 = (two_bytes_to_int(b[4], b[5]))/scale
    q3 = (two_bytes_to_int(b[8], b[9]))/scale
    q4 = (two_bytes_to_int(b[12], b[13]))/scale
    data = {"q1" : q1,
            "q2" : q2,
            "q3" : q3,
            "q4" : q4,
        }
    # pack up the data and send to server for display
    json_data = json.dumps(data)
    sock.write(json_data.encode('utf-8'))

