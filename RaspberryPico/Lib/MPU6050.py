from machine import Pin, I2C
import MPUregisters as MPUreg
from bus import bus
import utime
#
# Version 1.4 26-feb-2024
#


MPUADDR = MPUreg.MPUADDRESS
BUFFER_LENGTH = 32     #This is likely a limitation left over from the Arduino library

def to_byte(integer) -> bytes:
    return int.to_bytes(integer, 1, "big")

def two_bytes(integer) -> bytes:
    return int.to_bytes(integer, 2, "big")

def to_int(byte)-> int:
    return int.from_bytes(byte, "big")

def two_bytes_to_int(d1,d2) -> int:
    d = ord(d1)*256 + ord(d2)
    if d > 32767:
        d -= 65536
    return d

 

class MPU6050():
   
    def __init__(self, bus):
        
        self.bus = bus
#
        self.start_time_us = utime.ticks_us()
        self.start_time_ms = utime.ticks_ms()
        self.bus.writeto_mem(MPUADDR, MPUreg.RESET, b'\0')  # initialize MPU
        self.set_full_scale_gyro_range(MPUreg.GYRO_FS_250)
        self.set_full_scale_accel_range(MPUreg.ACCEL_FS_2)
        self.set_clock_source(MPUreg.CLOCK_PLL_XGYRO)    # This is doubled up in the MPU6050dmp class
        self.set_sleep_enabled(False)
#
# I2C bus related routines
#
    def reset_i2c_master(self): 
        self.bus.write_bit(MPUADDR, MPUreg.USER_CTRL, MPUreg.USERCTRL_I2C_MST_RESET_BIT, True)
        
    def set_i2c_master_mode_enabled(self, enabled):
        self.bus.write_bit(MPUADDR, MPUreg.USER_CTRL, MPUreg.USERCTRL_I2C_MST_EN_BIT,enabled)
        
    def set_slave_address(self, num, address):
        if (num > 3): return
        register = MPUreg.I2C_SLV0_ADDR + num*3
        print(address, type(address))
        self.bus.writeto_mem(MPUADDR, register, address)
#
# MPU control routines
#
    def set_clock_source(self, source):
        self.bus.write_bits(MPUADDR, MPUreg.PWR_MGMT_1, MPUreg.PWR1_CLKSEL_BIT, MPUreg.PWR1_CLKSEL_LENGTH, source)
    
    def set_sleep_enabled(self, enabled):
        self.bus.write_bit(MPUADDR, MPUreg.PWR_MGMT_1, MPUreg.PWR1_SLEEP_BIT, enabled)
         
    def set_wake_cycle_enabled(self, enabled):
        self.bus.write_bit(MPUADDR, MPUreg.PWR_MGMT_1, MPUreg.PWR1_CYCLE_BIT, enabled)

    def get_device_id(self) -> int:
        buffer = self.bus.read_bits(MPUADDR, MPUreg.WHO_AM_I, MPUreg.WHO_AM_I_BIT, MPUreg.WHO_AM_I_LENGTH)
        return buffer    
            
    def who_am_i(self) -> int:
        return to_int(self.bus.readfrom_mem(MPUADDR, 0x75, 1))

    def get_OTP_bank_valid(self):
        buffer = self.bus.read_bit(MPUADDR, MPUreg.XG_OFFS_TC, MPUreg.TC_OTP_BNK_VLD_BIT) #CHECK return type
        return buffer
    
    def set_OTP_bank_valid(self, enabled):
        self.bus.write_bit(MPUADDR, MPUreg.XG_OFFS_TC, MPUreg.OTP_BNK_VLD_BIT, enabled)

    def set_rate(self, rate):
        self.bus.writeto_mem(MPUADDR, MPUreg.SMPLRT_DIV, rate)
        
    def set_external_frame_sync(self, sync):
        self.bus.write_bits(MPUADDR, MPUreg.CONFIG, MPUreg.CFG_EXT_SYNC_SET_BIT, MPUreg.CFG_EXT_SYNC_SET_LENGTH, sync)

    def set_int_enabled(self, enabled):
        b = to_byte(int(enabled))
        self.bus.writeto_mem(MPUADDR, MPUreg.INT_ENABLE, b)
        
    def reset_dmp(self):
        self.bus.write_bit(MPUADDR, MPUreg.USER_CTRL, MPUreg.USERCTRL_DMP_RESET_BIT, True)
        
    def reset_fifo(self):
        self.bus.write_bit(MPUADDR, MPUreg.USER_CTRL, MPUreg.USERCTRL_FIFO_RESET_BIT, True)
        
    def set_int_data_ready_enabled(self):
        self.bus.write_bit(MPUADDR, MPUreg.INT_ENABLE, MPUreg.INTERRUPT_DATA_RDY_BIT, True)
        
    def get_int_data_ready_enabled(self):
        return self.bus.read_bit(MPUADDR, MPUreg.INT_ENABLE, MPUreg.INTERRUPT_DATA_RDY_BIT)
    
    def get_int_data_ready_status(self):
        return self.bus.read_bit(MPUADDR, MPUreg.INT_STATUS, MPUreg.INTERRUPT_DATA_RDY_BIT)
#
# Data processing and motion detection
#        
    def get_motion_detection_threshold(self) -> bytes:
        return self.bus.readfrom_mem(MPUADDR, MPUreg.MOT_THR, 1)
    
    def set_motion_detection_threshold(self, threshold):
        self.bus.writeto_mem(MPUADDR, MPUreg.MOT_THR, threshold)
        
    def get_motion_detection_duration(self) -> bytes:
        return self.bus.readfrom_mem(MPUADDR, MPUreg.MOT_DUR, 1)

    def set_motion_detection_duration(self, time):
        self.bus.writeto_mem(MPUADDR, MPUreg.MOT_DUR, time)
        
    def get_zero_motion_detection_threshold(self) -> bytes:
        return self.bus.readfrom_mem(MPUADDR, MPUreg.ZRMOT_THR, 1)
        
    def set_zero_motion_detection_threshold(self, threshold):
        self.bus.writeto_mem(MPUADDR, MPUreg.ZRMOT_THR, threshold)
        
    def get_zero_motion_detection_duration(self) -> bytes:
        return self.bus.readfrom_mem(MPUADDR, MPUreg.ZRMOT_DUR, 1)
        
    def set_zero_motion_detection_duration(self, time):
        self.bus.writeto_mem(MPUADDR, MPUreg.ZRMOT_DUR, time)
        
    def get_int_zero_motion_enabled(self) -> int:
        b = self.bus.read_bit(MPUADDR, MPUreg.INT_ENABLE, MPUreg.INTERRUPT_ZMOT_BIT)
        return b
    
    def set_int_zero_motion_enabled(self, enabled):
        self.bus.write_bit(MPUADDR, MPUreg.INT_ENABLE, MPUreg.INTERRUPT_ZMOT_BIT,enabled)
        
    def get_int_motion_enabled(self) -> int:
        b = self.bus.read_bit(MPUADDR, MPUreg.INT_ENABLE, MPUreg.INTERRUPT_MOT_BIT)
        return b
    
    def set_int_motion_enabled(self, enabled):
        self.bus.write_bit(MPUADDR, MPUreg.INT_ENABLE, MPUreg.INTERRUPT_MOT_BIT,enabled)
        
    def set_motion_detection_counter_decrement(self, decrement):
        self.bus.write_bits(MPUADDR, MPUreg.MOT_DETECT_CTRL, MPUreg.DETECT_MOT_COUNT_BIT, MPUreg.DETECT_MOT_COUNT_LENTH,decrement)
        
    def get_motion_detection_counter_decrement(self) -> int:
        return self.bus.read_bits(MPUADDR, MPUreg.MOT_DETECT_CTRL, MPUreg.DETECT_MOT_COUNT_BIT, MPUreg.DETECT_MOT_COUNT_LENTH)

    def get_DLPF_mode(self) -> int:
        return self.bus.read_bits(MPUADDR, MPUreg.MOT_DETECT_CTRL, MPUreg.CONFIG, MPUreg.CFG_DLPF_CFG_BIT, MPUreg.CFG_DLPF_CFG_LENGTH) 
    
    def set_DLPF_mode(self,mode):
        self.bus.write_bits(MPUADDR, MPUreg.CONFIG, MPUreg.CFG_DLPF_CFG_BIT, MPUreg.CFG_DLPF_CFG_LENGTH, mode)
        
    def set_DHPF_mode(self, mode):
        self.bus.write_bits(MPUADDR, MPUreg.ACCEL_CONFIG, MPUreg.ACONFIG_ACCEL_HPF_BIT, MPUreg.ACONFIG_ACCEL_HPF_LENGTH, mode)
        
    def get_DHPF_mode(self) -> int:
        return self.bus.read_bits(MPUADDR, MPUreg.ACCEL_CONFIG, MPUreg.ACONFIG_ACCEL_HPF_BIT, MPUreg.ACONFIG_ACCEL_HPF_LENGTH)
    
    
    def set_rate(self, rate):
        self.bus.writeto_mem(MPUADDR, MPUreg.SMPLRT_DIV, rate)

#
# Sensor related functions
#
    def get_full_scale_gyro_range(self) -> int:
        return(self.bus.read_bits(MPUADDR,
                                  MPUreg.GYRO_CONFIG,
                                  MPUreg.GCONFIG_FS_SEL_BIT,
                                  MPUreg.GCONFIG_FS_SEL_LENGTH))
    
    def set_full_scale_gyro_range(self, range):
        self.bus.write_bits(MPUADDR,
                            MPUreg.GYRO_CONFIG,
                            MPUreg.GCONFIG_FS_SEL_BIT,
                            MPUreg.GCONFIG_FS_SEL_LENGTH, range);
        
    def set_full_scale_accel_range(self, range):
        self.bus.write_bits(MPUADDR,
                            MPUreg.ACCEL_CONFIG,
                            MPUreg.ACONFIG_AFS_SEL_BIT,
                            MPUreg.ACONFIG_AFS_SEL_LENGTH, range);
          
    def get_acceleration(self):
        b = self.bus.readfrom_mem(MPUADDR, MPUreg.ACCEL_XOUT_H, 6)
        return(two_bytes_to_int(b[0:1], b[1:2]), two_bytes_to_int(b[2:3], b[3:4]),two_bytes_to_int(b[4:5], b[5:6]))    

    def get_rotation(self):
        b = self.bus.readfrom_mem(MPUADDR, MPUreg.GYRO_XOUT_H, 6)
        return(two_bytes_to_int(b[0:1], b[1:2]), two_bytes_to_int(b[2:3], b[3:4]),two_bytes_to_int(b[4:5], b[5:6]))
        
    def get_temperature(self) -> float:
        buffer = self.bus.readfrom_mem(MPUADDR, MPU6050_RA_TEMP_OUT_H, 2)
        return (two_bytes_to_int(buffer[0:1], buffer[1:2]))/340 + 36.53
    
#
# Sensor offsets
#

    def get_xaccel_offset(self):
        save_address = MPUreg.XA_OFFS_H if self.get_device_id() < 0x38 else 0x77   # why are we checking getDevice. According to docs w should get 0x34
        buffer = self.bus.readfrom_mem(MPUADDR, save_address, 2)
        return two_bytes_to_int(buffer[0:1], buffer[1:2])  #This is awkward python way to addres bytes in bytearray

    def set_xaccel_offset(self, offset):
        save_address = MPUreg.XA_OFFS_H if self.get_device_id() < 0x38 else 0x77
        self.bus.writeto_mem(MPUADDR, save_address, offset)
        
    def get_yaccel_offset(self):
        save_address = MPUreg.YA_OFFS_H if self.get_device_id() < 0x38 else 0x77   # why are we checking getDevice. According to docs w should get 0x34
        buffer = self.bus.readfrom_mem(MPUADDR, save_address, 2)
        return two_bytes_to_int(buffer[0:1], buffer[1:2])  #This is awkward python way to addres bytes in bytearray

    def set_yaccel_offset(self, offset):
        save_address = MPUreg.YA_OFFS_H if self.get_device_id() < 0x38 else 0x77
        self.bus.writeto_mem(MPUADDR, save_address, offset)
        
    def get_zaccel_offset(self):
        save_address = MPUreg.ZA_OFFS_H if self.get_device_id() < 0x38 else 0x77   # why are we checking getDevice. According to docs w should get 0x34
        buffer = self.bus.readfrom_mem(MPUADDR, save_address, 2)
        return two_bytes_to_int(buffer[0:1], buffer[1:2])  #This is awkward python way to addres bytes in bytearray

    def set_zaccel_offset(self, offset):
        save_address = MPUreg.ZA_OFFS_H if self.get_device_id() < 0x38 else 0x77
        self.bus.writeto_mem(MPUADDR, save_address, offset)      

    def get_xgyro_offset(self):
        return self.bus.read_word(MPUADDR, MPUreg.XG_OFFS_USRH)
    
    def set_xgyro_offset(self, offset):
        self.bus.write_word(MPUADDR, MPUreg.XG_OFFS_USRH, offset)   # translate write word to write buffer
  
    def get_ygyro_offset(self):
        return self.bus.read_word(MPUADDR, MPUreg.YG_OFFS_USRH)
    
    def set_ygyro_offset(self, offset):
        self.bus.write_word(MPUADDR, MPUreg.YG_OFFS_USRH, offset)   # translate write word to write buffer
    
    def get_zgyro_offset(self):
        return self.bus.read_word(MPUADDR, MPUreg.ZG_OFFS_USRH)
    
    def set_zgyro_offset(self, offset):
        self.bus.write_word(MPUADDR, MPUreg.ZG_OFFS_USRH, offset)   # translate write word to write buffer
        
        
    def get_accelerometer_power_on_delay(self) -> int:
        return self.bus.read_bits(MPUADDR, MPUreg.MOT_DETECT_CTRL, MPUreg.DETECT_ACCEL_ON_DELAY_BIT, MPUreg.DETECT_ACCEL_ON_DELAY_LENGTH)
    
    def set_accelerometer_power_on_delay(self, delay):
        self.bus.write_bits(MPUADDR, MPUreg.MOT_DETECT_CTRL, MPUreg.DETECT_ACCEL_ON_DELAY_BIT, MPUreg.DETECT_ACCEL_ON_DELAY_LENGTH, delay)

       
    # Memory related routines

    def set_memory_bank(self, bank, prefetchEnabled=False, userBank=False) -> None:
        bank_i = to_int(bank)   
        bank_i &= 0x1F;
        if (userBank):
            bank_i |= 0x20
        if (prefetchEnabled):
            bank_i |= 0x40
        bank = to_byte(bank_i)
        self.bus.writeto_mem(MPUADDR, MPUreg.BANK_SEL, bank);

    #MEM_START_ADDR register
    
    def set_memory_start_address(self, address):
        self.bus.writeto_mem(MPUADDR, MPUreg.MEM_START_ADDR, address);
        
    def writeProgMemoryBlock(self,data, data_size, bank, address, verify):
        
        return self.writeMemoryBlock(data, data_size, bank, address, verify, False);


    def writeMemoryBlock(self, data, data_size, bank, address, verify, useProgMem):
        self.set_memory_bank(bank, False, False)
        self.set_memory_start_address(address)

        data_pointer = 0
        address_i = to_int(address) 
        bank_i    = to_int(bank)
        counter = 0
        while data_pointer < data_size:
            counter += 1
            chunk_size = MPUreg.DMP_MEMORY_CHUNK_SIZE;
            chunk_size = min(chunk_size, len(data) - data_pointer)
            chunk_size = min(chunk_size, 256-address_i)
            if (useProgMem):
                pass  # the following was commented out in the c++ source code
            else:
                prog_buffer = data[data_pointer:data_pointer+chunk_size]
                bank = to_byte(bank_i)
                self.set_memory_bank(bank)                    
                address = to_byte(address_i) 
                self.set_memory_start_address(address)
                self.bus.writeto_mem(MPUADDR, MPUreg.MEM_R_W, prog_buffer);

            verify = True # DEBUG DEBUG
            if verify:
                bank    = to_byte(bank_i)       
                address = to_byte(address_i)
                self.set_memory_bank(bank);                 # set bank and start address again even though
                self.set_memory_start_address(address);     # these have just been set to write data to the MPU
                verify_buffer = self.bus.readfrom_mem(MPUADDR, MPUreg.MEM_R_W, chunk_size)

                for i in range(chunk_size):
                    if (prog_buffer[i] != verify_buffer[i]):  #translate
                        print(f"Block write verification error, {bank} , address {address} !");
                        print("Expected:")
                        for j in range(chunk_size):
                            print(f" 0x{prog_buffer[j]:02X}", end='')
                        print("\nReceived:")
                        for j in range(chunk_size):
                            print(f" 0x{verify_buffer[j]:02X}", end='')
                        print("\n")
                        return False # // uh oh.

            data_pointer += chunk_size
            address_i += chunk_size
            address_i %= 256       # wrap around at 256, c++ progs use uint8_t variables for that
            address = to_byte(address_i)
 
            if (i < data_size):
                if (address_i == 0):
                    bank_i += 1 
                    bank = to_byte(bank_i)                     
        return True
    
#
# FIFO related routines
#

    def get_fifo_count(self):
        buffer = self.bus.readfrom_mem(MPUADDR, MPUreg.FIFO_COUNTH, 2)
        return (buffer[0] << 8 | buffer[1])

    def get_fifo_byte(self):
        buffer = self.bus.readfrom_mem(MPUADDR, MPUreg.FIFO_R_W, 1)
        return buffer

    def get_fifo_bytes(self,length):
        if(length > 0):
            data = self.bus.readfrom_mem(MPUADDR, MPUreg.FIFO_R_W, length);
        else:
            data = bytearray()
        return data

    def reset_fifo(self):
       self.bus.write_bit(MPUADDR, MPUreg.USER_CTRL, MPUreg.USERCTRL_FIFO_RESET_BIT, True)

    def get_current_fifo_packet(self, length):   # length = packetsize. There is no check!!!
        ''' Overflow-proof function to retrieve a FIFO packet. Modified from Rowberg's C++
            routine as this was creating fragmented packets. The current approach is robust against
            busfrequencies as low as 50kHz and packetretrieval rates of 10Hz
        '''
        break_timer = utime.ticks_ms()
        fifo_c = self.get_fifo_count()
        while True:    
            if fifo_c == length:                          # Nice, we have only 1 packet
                return self.get_fifo_bytes(length) 
            elif fifo_c > length:                         # There is more than 1 packet in the fifo buffer 
                remove = (int(fifo_c/length) - 1)*length
                while remove > 5*length:                  # Limit #bytes received to avoid timouts at low busfrequencies
                    self.get_fifo_bytes(5*length)         # trash these
                    remove -= 5* length
                self.get_fifo_bytes(remove)
                return self.get_fifo_bytes(length)        # and return the remaining packet
            elif fifo_c == 0:
                if utime.ticks_diff(utime.ticks_ms(), break_timer) <= 50: # Need some more intelligence for timeout
                    utime.sleep_us(500)
                else:
                    raise Exception('Timeout waiting for next packet')
            else:
                pass    # This can occur when length does not match the actual package size 
                        # It occurs also when fifo has less than 'length' bytes, which occasionally happens,
                        # at least when using the dmp. So it is not per se an error to end up here.
                        # Should have a handler to separate both cases and raise an excpetion when necessary


            fifo_c = self.get_fifo_count() 

class MPU6050_DMP(MPU6050):
    
    MPU6050_DMP_FIFO_RATE_DIVISOR  = 0x01 # The New instance of the Firmware has this as the default

    def __init__(self, bus):
        super().__init__(bus)
        # we are reading DMP image from file. Make sure this is in /lib in the pico memory
        int_values =  []
        with open('/lib/DMP_image.txt') as DMP_image_source:
            a = DMP_image_source.readlines()
            for line in a:
                hex_values = line.strip().rstrip(', ').split(', ')
                int_values += [int(value, 16) for value in hex_values]
        self.DMP_image = bytes(int_values)
        self.len_DMP_image = 3062
        if len(self.DMP_image) != self.len_DMP_image:
            raise Exception("DMP image file has incorrect length")
        
        self.dmp_packet_size = 28
        
    def set_dmp_enabled(self, enabled):
        self.bus.write_bit(MPUADDR, MPUreg.USER_CTRL, MPUreg.USERCTRL_DMP_EN_BIT, enabled)
        
    def get_dmp_enabled(self):
        return self.bus.read_bit(MPUADDR, MPUreg.USER_CTRL, MPUreg.USERCTRL_DMP_EN_BIT)

    def dmp_initialize(self):
        self.bus.write_bit(MPUADDR,0x6B, 7, 1)                #PWR_MGMT_1: reset with 100ms delay
        utime.sleep_ms(100)
       
        self.bus.write_bits(MPUADDR,0x6A, 2, 3, 0b111)        # full SIGNAL_PATH_RESET: with another 100ms delay
        utime.sleep_ms(100);

        self.bus.writeto_mem(MPUADDR, 0x6B, b'\x01')   # 1000 0001 PWR_MGMT_1:Clock Source Select PLL_X_gyro CHECK!! comment not in line with data

        self.bus.writeto_mem(MPUADDR, 0x38, b'\x00')   # 0000 0000 INT_ENABLE: no Interrupt
        self.bus.writeto_mem(MPUADDR, 0x23, b'\x00')   # 0000 0000 MPU FIFO_EN: (all off) Using DMP's FIFO instead
        self.bus.writeto_mem(MPUADDR, 0x1C, b'\x00')   # 0000 0000 ACCEL_CONFIG: 0 =  Accel Full Scale Select: 2g
        self.bus.writeto_mem(MPUADDR, 0x37, b'\x80')   # 1001 0000 INT_PIN_CFG: ACTL The logic level for int pin is active low. and interrupt status bits are cleared on any read
        self.bus.writeto_mem(MPUADDR, 0x6B, b'\x01')   # 0000 0001 PWR_MGMT_1: Clock Source Select PLL_X_gyro
        self.bus.writeto_mem(MPUADDR, 0x19, b'\x04')   # 0000 0100 SMPLRT_DIV: Divides the internal sample rate 400Hz ( Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV))
        self.bus.writeto_mem(MPUADDR, 0x1A, b'\x01')   # 0000 0001 CONFIG: Digital Low Pass Filter (DLPF) Configuration 188HZ  //Im betting this will be the beat
        if (not self.writeProgMemoryBlock(self.DMP_image, self.len_DMP_image, b'\x00', b'\x00', True)):
             return 1     # Loads the DMP image into the MPU6050 Memory // Should Never Fail
        self.bus.writeto_mem(MPUADDR, 0x70, b'\x04\x00')# DMP Program Start Address!!
        self.bus.writeto_mem(MPUADDR, 0x1B, b'\x18')   # 0001 1000 GYRO_CONFIG: 3 = +2000 Deg/sec
        self.bus.writeto_mem(MPUADDR, 0x6A, b'\xC0')   # 1100 1100 USER_CTRL: Enable Fifo and Reset Fifo
        self.bus.writeto_mem(MPUADDR, 0x38, b'\x02')   # 0000 0010 INT_ENABLE: RAW_DMP_INT_EN on
        self.bus.write_bit(MPUADDR,0x6A, 2, 1)        # Reset FIFO one last time just for kicks. (MPUi2cWrite reads 0x6A first and only alters 1 bit and then saves the byte)
# 
        self.set_dmp_enabled(False)# disable DMP for compatibility with the MPU6050 library. Switch this on once all is initialised
        rate = b'\x04' 
        self.set_rate(rate) # slow down the pace of output to 1khz/(1+rate)


        return 0

    def dmp_packet_available(self):
        return self.get_fifo_count() >= self.dmp_get_fifo_packet_size();  #superflous call. Replace later

    def dmp_get_fifo_packet_size(self):
        return self.dmp_packet_size   

