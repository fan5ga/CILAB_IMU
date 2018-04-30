# CILAB IMU sensor
The Cilab IMU was designed with multi-sensor fusion which works underwater.     
It includes a typical Inertial Measurement Unit (IMU), Barometer unit and thermometer. it could be incorporated into underwater systems which utilize the IMU raw data to determine current poses and navigate underwater, and use pressure and temperature sensor to determine underwater depth and water temperature. Communication is enabled via I2C to various devices.    
Arduino based program is provided to read raw data from sensors and send out the IMU, pressure, temperature information through serial port.     
The Cilab IMU GUI allows user to visualize the real time IMU sensor data and view the virtual IMU sensor through a Arduino board. Arduino communicate with IMU sensor via I2C and transfer real time data to PC through serial commination.

 
 
 
 **Multiple sensors fusion:** 
- BNO055: BOSCH IMU
- MS5837: Air/Water Preesure, water depth estimation
- TSY01: Temperature

### IMU Sensor board(Arduino Code)
IIC to Serial communication.


### IMU GUI linux Source code 
A simple GUI to visualize IMU data.
*** Dependency: ***
- OpenGL
- pygame
- tkinter

**Useage**
- $ python imu.py

### IMU GUI Windows 
Windows GUI

***More information please refer to Pdf Mannual.**
