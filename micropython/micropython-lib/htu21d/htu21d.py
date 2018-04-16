# The MIT License (MIT)
#
# Copyright (c) 2018 QinChi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
HTU21D is a python library for the ESP8266 HTU21D-F Humidity/Temperature
"""

from machine import I2C,Pin
import math
import time

# HTU21D default address
HTU21D_I2CADDR            = 0x40

# Operating Modes
HTU21D_HOLDMASTER         = 0x00
HTU21D_NOHOLDMASTER       = 0x10

# HTU21D Commands
HTU21D_TRIGGERTEMPCMD     = 0xE3  # Trigger Temperature Measurement
HTU21D_TRIGGERHUMIDITYCMD = 0xE5  # Trigger Humidity Measurement
HTU21D_WRITEUSERCMD       = 0xE6  # Write user register
HTU21D_READUSERCMD        = 0xE7  # Read user register
HTU21D_SOFTRESETCMD       = 0xFE  # Soft reset

HTU21D_MAX_MEASURING_TIME = 100   # mSec

# HTU21D Constants for Dew Point calculation
HTU21D_A = 8.1332
HTU21D_B = 1762.39
HTU21D_C = 235.66


class HTU21DException(Exception):
    print(Exception)

# HTU21D
class HTU21D():
    def __init__(self):
        """Initialize I2C device"""
        self.addr = HTU21D_I2CADDR
        self.i2c = I2C(scl=Pin(14),sda=Pin(2),freq=100000)

    def __del__(self):
        """Delete I2C device"""
        del(self.i2c)

    def reset(self):
        """Reboots the sensor switching the power off and on again."""
        dat = bytes((HTU21D_SOFTRESETCMD, ))
        self.i2c.writeto(self.addr, dat)
        time.sleep(1)

    def crc_check(self, msb, lsb, crc):
        """CRC check"""
        remainder = ((msb << 8) | lsb) << 8
        remainder |= crc
        divsor = 0x988000
        for i in range(0, 16):
            if remainder & 1 << (23 - i):
                remainder ^= divsor
            divsor >>= 1
        if remainder == 0:
            return True
        else:
            return False

    def read_raw_temp(self):
        """Reads the raw temperature from the sensor."""
        dat = bytes((HTU21D_TRIGGERTEMPCMD,))
        self.i2c.writeto(self.addr, dat)
        time.sleep(0.1)
        dat = self.i2c.readfrom(self.addr, 3)
        if self.crc_check(dat[0],dat[1], dat[2]) is False:
            raise HTU21DException("CRC Exception")
        raw = (dat[0] << 8) + dat[1]
        raw &= 0xFFFC
        return raw

    def read_raw_humidity(self):
        """Reads the raw relative humidity from the sensor."""
        dat = bytes((HTU21D_TRIGGERHUMIDITYCMD,))
        self.i2c.writeto(self.addr, dat)
        time.sleep(0.1)
        dat = self.i2c.readfrom(self.addr, 3)
        if self.crc_check(dat[0], dat[1], dat[2]) is False:
            raise HTU21DException("CRC Exception")
        raw = (dat[0] << 8) + dat[1]
        raw &= 0xFFFC
        return raw

    def read_temperature(self):
        """Gets the temperature in degrees celsius."""
        v_raw_temp = self.read_raw_temp()
        v_real_temp = float(v_raw_temp)/65536 * 175.72
        v_real_temp -= 46.85
        return v_real_temp

    def read_humidity(self):
        """Gets the relative humidity."""
        v_raw_hum = self.read_raw_humidity()
        v_real_hum = float(v_raw_hum)/65536 * 125
        v_real_hum -= 6
        return v_real_hum

    def read_dewpoint(self):
        """Calculates the dew point temperature."""
        # Calculation taken straight from datasheet.
        ppressure = self.read_partialpressure()
        humidity = self.read_humidity()
        den = math.log10(humidity * ppressure / 100) - HTU21D_A
        dew = -(HTU21D_B / den + HTU21D_C)
        return dew

    def read_partialpressure(self):
        """Calculate the partial pressure in mmHg at ambient temperature."""
        v_temp = self.read_temperature()
        v_exp = HTU21D_B / (v_temp + HTU21D_C)
        v_exp = HTU21D_A - v_exp
        v_part_press = 10 ** v_exp
        return v_part_press

