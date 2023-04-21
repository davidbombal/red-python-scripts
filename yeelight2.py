# Make sure you install yeelight
# pip3 install yeelight

# Documentation here: https://yeelight.readthedocs.io/en/latest/

import time
from yeelight import Bulb
bulb1 = Bulb("192.168.0.105")
bulb2 = Bulb("192.168.0.117")
bulb1.turn_on()
bulb2.turn_on()
time.sleep(1)

bulb1.set_rgb(255,0,0)
bulb2.set_rgb(255,0,0)
time.sleep(1)

bulb1.set_rgb(164,168,50)
time.sleep(1)

bulb2.set_rgb(50,90,168)
time.sleep(1)

bulb1.set_rgb(168,50,50)
time.sleep(1)

bulb2.set_rgb(50,168,54)
time.sleep(1)

bulb1.set_rgb(255,0,0)
time.sleep(1)

rgb1 = 50
rgb2 = 10
rgb3 = 50
for i in range(10):
    bulb1.set_rgb(rgb1,rgb2,rgb3)
    bulb2.set_rgb(rgb1-10,rgb2-10,rgb3-10)
    time.sleep(1)
    i = i + 1
    rgb1 = (i*10.5)
    rgb2 = (i*5.5)
    rgb3 = (i*9.5)
    print(rgb1, rgb2, rgb3)
    bulb1.set_rgb(rgb1,rgb2,rgb3)

bulb1.set_rgb(50,64,168)
bulb2.set_rgb(50,64,168)
