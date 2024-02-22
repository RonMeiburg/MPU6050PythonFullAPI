from machine import Pin, I2C


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

class bus(I2C):
    
    def __init__(self, i2cbus, sda=Pin(16), scl=Pin(17), freq=400000):
        pass
   
    def read_bit(self, dev_addr, reg_addr, bit_start) -> int:
        return self.read_bits(dev_addr, reg_addr, bit_start, 1)

    def read_bits(self, dev_addr, reg_addr, bit_start, length) -> int:
        b = self.readfrom_mem(dev_addr, reg_addr, 1)
        bi = to_int(b)
        mask = ((1 << length) - 1) << (bit_start - length + 1)
        bi &= mask
        bi >>= (bit_start - length + 1)
        return bi

    def read_word(self, dev_addr, dev_reg) -> int:  
        high = self.readfrom_mem(dev_addr, dev_reg, 1)
        low = self.readfrom_mem(dev_addr, dev_reg+1, 1)
        return two_bytes_to_int(high, low)
        
    def read_bytes(self, dev_addr, dev_reg, length):
        print("called read_bytes, replace with self.readfrom_mem() call")
        return(self.readfrom_mem(dev_addr, dev_reg, length))
 
   
    def write_bit(self, dev_addr, reg_addr, bit_num, value) -> bool:
        b = self.readfrom_mem(dev_addr, reg_addr, 1) 
        bi = to_int(b)                                # convert to integer. Python does not support bitwise ops on bytes
        bi = (bi | (1 << bit_num)) if value != 0 else (bi & ~(1 << bit_num))     # Update the bit value
        b = to_byte(bi)                               # convert back to byte
        self.writeto_mem(dev_addr, reg_addr, b)      # Write the updated value back to the register
        return True                                  # Seems rather pointless for Python


    def write_bits(self, dev_addr, reg_addr, bit_start, length, data) -> None:
        b = self.readfrom_mem(dev_addr, reg_addr, 1)
        bi = to_int(b)                       
        mask = ((1 << length) - 1) << (bit_start - length + 1)
        data <<= (bit_start - length + 1)       # shift data into correct position
        data &= mask                            # zero all non-important bits in data
        bi &= ~(mask)                           # zero all important bits in existing byte
        bi |= data                              # combine data with existing byte
        b = to_byte(bi)            
        self.writeto_mem(dev_addr, reg_addr, b)
        return True 

    def write_word(self, dev_addr, reg_addr, word) -> None:
        buffer = two_bytes(word)
        self.writeto_mem(dev_addr, reg_addr, buffer)
           
