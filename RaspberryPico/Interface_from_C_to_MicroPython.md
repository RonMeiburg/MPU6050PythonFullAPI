# 

## Converting the C++ routines from the I2C-API to micropython for Pi Pico

The routines in the I2Cdev.cpp all call low-level c++ primitives from its I2C API. Micropython simplifies the access, as it already has a number of high level routines that deal with the nitty gritty. The C++ code has a number 'write-bit'  type routines for which the I2C driver requires a few more methods, as the smallest unit of transfer on the i2c bus is a byte. Below are some translations of C++ routines to micropython that can serve as a template.

### Reading data from the MPU6050

The readBytes routine in the C++ I2C-API is:

```cpp
int8_t I2Cdev::readBytes(uint8_t devAddr, uint8_t regAddr, uint8_t length, uint8_t *data, uint32_t timeout) {
    uint8_t count = 0;
    i2c_write_blocking(i2c_default, devAddr, &regAddr, 1, true);
    count = i2c_read_timeout_us(i2c_default, devAddr, data, length, false, timeout * 1000);    
    return count;
```

What this does is write two bytes onto the bus, first the address of the MPU (dev Addr - 0x68) in a write request and then a byte designating the register (regAddr). The low level routine `i2c-write-blocking` holds the bus while writing these two bytes, and then closes with a NACK. In the subsequent step `i2c_read_timeout_us` it puts a read request on the bus and subsequently pulls in 'length' number of bytes. In the end 'count' will hold the number of bytes received. 

But in Micropython all this is wrapped up in a single call:

```python
count = i2cbus.readfrom_mem(dev_address, reg_address, length):
```

This does require a one time initialisation of i2cbus, which is an I2C object. Check the GPIO pin assignment for the Pico and make a choice. The numbers below will work.

```python
from machine import Pin, I2C
busnum  = 0         # bus number. Can only be 0, 1
sdaPIN  = Pin(16)   # GPIO data pin for i2c bus
sclPIN  = Pin(17)   # GPIO clock pin for i2c bus
i2cbus = I2C(busnum, sda=sdaPIN, scl=sclPin)
```



The <u>readByte</u> routine in the C++ API calls the ReadBytes routine with length=1.

```cpp
int8_t I2Cdev::readByte(uint8_t devAddr, uint8_t regAddr, uint8_t *data, uint32_t timeout) {
    return readBytes(devAddr, regAddr, 1, data, timeout);
```

The equivalent Micropython call is:

```python
count = i2c.readfrom_mem(dev_address, reg_address, 1):
```





### Writing data to the MPU

etc etc TBD

In the same vein, we can deal with:

writeBytes in c++:

```cpp
bool I2Cdev::writeBytes(uint8_t devAddr, uint8_t regAddr, uint8_t length, uint8_t* data) {
    uint8_t status = 0;
    uint8_t data_buf[length + 1];
    data_buf[0] = regAddr;
    for(int i=0; i<length; i++){
        data_buf[i+1] = data[i];
    }
    status = i2c_write_blocking(i2c_default, devAddr, data_buf, length + 1, false);
    return status;
```

This puts the register address of the MPU as the first byte of a buffer (data_buf) and have it followed by 'length' number of bytes. 

In the python case this simplifies to:

```python
i2c.writeto_mem(dev_address, reg_address, buffer)
```

As writing to the MPU minimally involves 2 bytes, namely the regAddress and a least a single message byte the c++ route writeByte has to fall back to a writeBytes routine.

From the header file:

```cpp
    // GYRO_CONFIG register
    uint8_t getFullScaleGyroRange();
    void setFullScaleGyroRange(uint8_t range);
```

```cpp
#define MPU6050_GYRO_FS_250         0x00
#define MPU6050_GYRO_FS_500         0x01
#define MPU6050_GYRO_FS_1000        0x02
#define MPU6050_GYRO_FS_2000        0x03
```

From the source code:

```cpp
void MPU6050::initialize() {
    setClockSource(MPU6050_CLOCK_PLL_XGYRO);
    setFullScaleGyroRange(MPU6050_GYRO_FS_250);
    setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
    setSleepEnabled(false); // thanks to Jack Elston for pointing this one out!
}
```

```cpp
/** Set full-scale gyroscope range.

* @param range New full-scale gyroscope range value
* @see getFullScaleRange()
* @see MPU6050_GYRO_FS_250
* @see MPU6050_RA_GYRO_CONFIG
* @see MPU6050_GCONFIG_FS_SEL_BIT
* @see MPU6050_GCONFIG_FS_SEL_LENGTH
  */
  void MPU6050::setFullScaleGyroRange(uint8_t range) {
   I2Cdev::writeBits(devAddr, MPU6050_RA_GYRO_CONFIG,
                     MPU6050_GCONFIG_FS_SEL_BIT,
                     MPU6050_GCONFIG_FS_SEL_LENGTH, range);
}
```

```cpp
#define MPU6050_RA_GYRO_CONFIG      0x1B
#define MPU6050_GCONFIG_FS_SEL_BIT      4
#define MPU6050_GCONFIG_FS_SEL_LENGTH   2
```

```cpp
/** Write multiple bits in an 8-bit device register.
 * @param devAddr I2C slave device address
 * @param regAddr Register regAddr to write to
 * @param bitStart First bit position to write (0-7)
 * @param length Number of bits to write (not more than 8)
 * @param data Right-aligned value to write
 * @return Status of operation (true = success)
 */
bool I2Cdev::writeBits(uint8_t devAddr, uint8_t regAddr, uint8_t bitStart,
                       uint8_t length, uint8_t data) {
    //      010 value to write
    // 76543210 bit numbers
    //    xxx   args: bitStart=4, length=3
    // 00011100 mask byte
    // 10101111 original value (sample)
    // 10100011 original & ~mask
    // 10101011 masked | value
    uint8_t b;
    if (readByte(devAddr, regAddr, &b) != 0) {
        uint8_t mask = ((1 << length) - 1) << (bitStart - length + 1);
        data <<= (bitStart - length + 1); // shift data into correct position
        data &= mask; // zero all non-important bits in data
        b &= ~(mask); // zero all important bits in existing byte
        b |= data; // combine data with existing byte
        return writeByte(devAddr, regAddr, b);
    } else {
        return false;
    }
}
```

```python
def readByte(devAddr, regAddr, data, timeout):
    return readBytes(devAddr, regAddr, 1, data, timeout)

def writeBits(devAddr, regAddr, bitStart, length, data):
    b = 0
    if readByte(devAddr, regAddr, b) != 0:
        mask = ((1 << length) - 1) << (bitStart - length + 1)
        data <<= (bitStart - length + 1)
        data &= mask
        b &= ~(mask)
        b |= data
        return writeByte(devAddr, regAddr, b)
    else:
        return False
```

```cpp
/** Read single byte from an 8-bit device register.

* @param devAddr I2C slave device address
* @param regAddr Register regAddr to read from
* @param data Container for byte value read from device
* @param timeout Optional read timeout in milliseconds (0 to disable, leave off to use default class value in I2Cdev::readTimeout)
* @return Status of read operation (true = success)
  */
  int8_t I2Cdev::readByte(uint8_t devAddr, uint8_t regAddr, uint8_t *data, uint32_t timeout) {
   return readBytes(devAddr, regAddr, 1, data, timeout);
  }
```

```cpp
int8_t I2Cdev::readBytes(uint8_t devAddr, uint8_t regAddr, uint8_t length,
                         uint8_t *data, uint32_t timeout) {
    uint8_t count = 0;

    i2c_write_blocking(i2c_default, devAddr, &regAddr, 1, true);
    count = i2c_read_timeout_us(i2c_default, devAddr, data, length,
            false, timeout * 1000);

    return count;

}
```
