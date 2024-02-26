## Rotating Box using a PicoW and separate display server

### Set-up

Grab the files in the lib directory of RaspberryPico in this repository and copy them to the /lib directory on the Pi Pico.

Create a `secrets.py` file with two definitions:

```python
SSID       = "SSID of your access point"
PASSWD     = "Password of your access point"
```

Store this in the /lib directory on the Pico

From this point there are two options

### Using a second Pi running Thonny

Run MPU6050_quaternions.py file in Thonny on a Pi that is connected to the PicoW. This will create the appropriate MPU6050_DMP object, set up the network connection on the pico send the quaternion as a JSON packet to the server. Make sure the SERVERIP and SERVERPORT are those of the receiving display server. 

### Running a stand-alone Pico

After setting the correct SERVERIP in the code, copy the MPU6050_quaternions.py file to the root directory of the Pico and rename it to main.py. This step obviously requires a second Pi. Now disconnect the Pico and the host Pi and connected the Pico to a USB power supply (could be another Pi serving power only). After a few seconds the LED on the Pico will come on, and it should be sending quaternion as a JSON packet to the display server.

### Display server

On the display server run the rotating_box.py script from this directory. It will set up a receiving UDP socket for data coming from the PicoW. Make sure the server has the IP as specified in MPU6050_quaternions.py and initiate a socket on the correct port number. Here I have used port 5000.
