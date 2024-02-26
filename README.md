# Full API for the MPU6050 in Python

### Introduction

The MPU6050 is an outdated 6-degrees (3 accelerometers, 3 gyro's) of freedom, that is still widely available from the likes of Joy-It and Adafruit. It is cheap and does the job for many simple hobby projects. It comes with an internal processor that can perform sensor fusion to produce  a quaternion representation of the orientation of the chip. It also has (zero-)motion detection.  

Most, if not all, Python projects are limited to direct access of the sensors, leaving the cpu-intensive calculations to the host processor.  Access to the advanced functions mentioned above has been made available through reverse engineering and a limited release of manufacturer documentation. The, now openly available API, is unfortunately in C++. For an effective use of the MPU6050 using Python access to the advanced functions is a necessity. Hence this translation into (micro)Python.



### Structure of the repo

This repo breaks up into two folders, one containing the PMU6050 using Python and the other using microPython. All is based on the C++ code in Jeff Rowberg's repository. https://github.com/jrowberg/i2cdevlib/tree/master/RP2040/MPU6050.  

The code exposes the functionality of the MPU6050, like (no-)motion detection, gravity free acceleraion, quaternion based orientation etc. At present the API calls to add additional sensors, in particular a magnetometer, have not (yet) been translated, as these are likely not going to be used and would only add size to the python source file. A recipe for translating these calls from C++ to (micro-)Python has been provided separately. 

Status

22 feb 2024 First example reading quaternions in microPython uploaded. The code for retrieving dmp packets is now stable even for low busfrequencies, down to 50kHz, and low packet retrieval frequencies
