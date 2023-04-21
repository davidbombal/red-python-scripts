# Make sure you install yeelight
# pip3 install yeelight

# Documentation here: https://yeelight.readthedocs.io/en/latest/

from yeelight import discover_bulbs
discover_bulbs()

from yeelight import Bulb
bulb = Bulb("192.168.0.105")

bulb.turn_on()
bulb.get_properties()
bulb.set_brightness(50)
bulb.set_rgb(255, 0, 0)
bulb.set_rgb(1, 0, 0)

bulb.set_color_temp(200)
bulb.set_color_temp(4700)
