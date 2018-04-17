
from htu21d import HTU21D
from ssd1306 import SSD1306_I2C
from machine import I2C,Pin
import time

i2c = I2C(scl=Pin(14),sda=Pin(2),freq=100000)
h = HTU21D()
s = SSD1306_I2C(126, 64, i2c)

s.init_display()

while True:
  temp='Temp:'+str(h.read_temperature())
  hum='Humi:'+str(h.read_humidity())
  print(temp,hum)
  s.fill(0)
  s.text(temp, 20, 20)
  s.text(hum, 20, 40, 4)
  s.show()
  time.sleep(1)