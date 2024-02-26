#
# Version 1.0 14feb2024
#
# Register addresses and constants for MPU6050
#
# MPU6050 bus address
MPUADDRESS = 0x68
# reset
RESET = 0x6b
#
# Sensor configuration
#
GYRO_CONFIG           = 0x1B
ACCEL_CONFIG          = 0x1C
GCONFIG_FS_SEL_BIT    = 4
GCONFIG_FS_SEL_LENGTH = 2
ACONFIG_AFS_SEL_BIT   = 4
ACONFIG_AFS_SEL_LENGTH = 2
#
# Constants
#
GYRO_FS_250  = 0x00
GYRO_FS_500  = 0x01
GYRO_FS_1000 = 0x02
GYRO_FS_2000 = 0x03
ACCEL_FS_2   = 0x00
ACCEL_FS_4   = 0x01
ACCEL_FS_8   = 0x02
ACCEL_FS_16  = 0x03
#
# Sensor R(ead) registers
#
ACCEL_XOUT_H   =  0x3B
ACCEL_XOUT_L   =  0x3C
ACCEL_YOUT_H   =  0x3D
ACCEL_YOUT_L   =  0x3E
ACCEL_ZOUT_H   =  0x3F
ACCEL_ZOUT_L   =  0x40
TEMP_OUT_H     =  0x41
TEMP_OUT_L     =  0x42
GYRO_XOUT_H    =  0x43
GYRO_XOUT_L    =  0x44
GYRO_YOUT_H    =  0x45
GYRO_YOUT_L    =  0x46
GYRO_ZOUT_H    =  0x47
GYRO_ZOUT_L    =  0x48
#
# Offset RW registers
#
XA_OFFS_H      =  0x06 #[15:0] XA_OFFS
XA_OFFS_L_TC   =  0x07
YA_OFFS_H      =  0x08 #[15:0] YA_OFFS
YA_OFFS_L_TC   =  0x09
ZA_OFFS_H      =  0x0A #[15:0] ZA_OFFS
ZA_OFFS_L_TC   =  0x0B
XG_OFFS_USRH   =  0x13   # X-Gyro offset [0:15]
XG_OFFS_USRL   =  0x14
YG_OFFS_USRH   =  0x15   # Y-Gyro offset [0:15]
YG_OFFS_USRL   =  0x16
ZG_OFFS_USRH   =  0x17   # Z-Gyro offset [0:15]    
ZG_OFFS_USRL   =  0x18
XG_OFFS_TC     =  0x00 #[7] PWR_MODE, [6:1] XG_OFFS_TC, [0] OTP_BNK_VLD
YG_OFFS_TC     =  0x01 #[7] PWR_MODE, [6:1] XG_OFFS_TC, [0] OTP_BNK_VLD
ZG_OFFS_TC     =  0x02 #[7] PWR_MODE, [6:1] XG_OFFS_TC, [0] OTP_BNK_VLD
#
#
TC_PWR_MODE_BIT    = 7
TC_OFFSET_BIT      = 6
TC_OFFSET_LENGTH   = 6
TC_OTP_BNK_VLD_BIT = 0
#
# Interrupt settings
#
INT_ENABLE                 = 0x38
INTERRUPT_FF_BIT           = 7
INTERRUPT_MOT_BIT          = 6
INTERRUPT_ZMOT_BIT         = 5
INTERRUPT_FIFO_OFLOW_BIT   = 4
INTERRUPT_I2C_MST_INT_BIT  = 3
INTERRUPT_PLL_RDY_INT_BIT  = 2
INTERRUPT_DMP_INT_BIT      = 1
INTERRUPT_DATA_RDY_BIT     = 0


USER_CTRL      =  0x6A  # Bit 7 enable DMP, bit 3 reset DMP
PWR_MGMT_1     =  0x6B  # Device defaults to sleep mode
PWR_MGMT_2     =  0x6C
BANK_SEL       =  0x6D  # Selects a specific bank
MEM_START_ADDR =  0x6E  # 
MEM_R_W        =  0x6F  # Register for reading of writing to DMP (check)


FIFO_COUNTH    =  0x72
FIFO_COUNTL    =  0x73
FIFO_R_W       =  0x74
WHO_AM_I       =  0x75  #Should return 0x68 (or 0x69 using Joy-it board)
WHO_AM_I_BIT   =    6
WHO_AM_I_LENGTH =   6
PWR1_DEVICE_RESET_BIT =  7
PWR1_SLEEP_BIT        =  6
PWR1_CYCLE_BIT        =  5
PWR1_TEMP_DIS_BIT     =  3
PWR1_CLKSEL_BIT       =  2
PWR1_CLKSEL_LENGTH    =  3

CLOCK_INTERNAL   = 0x00
CLOCK_PLL_XGYRO  = 0x01
CLOCK_PLL_YGYRO  = 0x02
CLOCK_PLL_ZGYRO  = 0x03
CLOCK_PLL_EXT32K = 0x04
CLOCK_PLL_EXT19M = 0x05
CLOCK_KEEP_RESET = 0x07
#
# Low pass filter settings
#
DLPF_BW_256 = 0x00
DLPF_BW_188 = 0x01
DLPF_BW_98  = 0x02
DLPF_BW_42  = 0x03
DLPF_BW_20  = 0x04
DLPF_BW_10  = 0x05
DLPF_BW_5   = 0x06
CFG_DLPF_CFG_BIT    = 2
CFG_DLPF_CFG_LENGTH = 3
#
# DMP related registers and parameters
#
DMP_MEMORY_BANKS       = 8
DMP_MEMORY_BANK_SIZE   = 256
DMP_MEMORY_CHUNK_SIZE  = 16
DMP_CFG_1              = 0x70
DMP_CFG_2              = 0x71
DMP_FIFO_RATE_DIVISOR  = 0x01


USERCTRL_DMP_EN_BIT          =   7
USERCTRL_FIFO_EN_BIT         =   6
USERCTRL_I2C_MST_EN_BIT      =   5
USERCTRL_I2C_IF_DIS_BIT      =   4
USERCTRL_DMP_RESET_BIT       =   3
USERCTRL_FIFO_RESET_BIT      =   2
USERCTRL_I2C_MST_RESET_BIT   =   1
USERCTRL_SIG_COND_RESET_BIT  =   0

# Motion detection registers
FF_THR    = 0x1D
FF_DUR    = 0x1E
MOT_THR   = 0x1F
MOT_DUR   = 0x20
ZRMOT_THR = 0x21
ZRMOT_DUR = 0x22

I2C_SLV0_ADDR = 0x25
OTP_BNK_VLD_BIT = 0
SMPLRT_DIV = 0x19
EXT_SYNC_TEMP_OUT_L = 0x1
CFG_EXT_SYNC_SET_BIT    = 5
CFG_EXT_SYNC_SET_LENGTH = 3
CONFIG = 0x1A