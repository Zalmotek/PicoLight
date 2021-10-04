import time
import board
import neopixel
import storage
from rotaryio import IncrementalEncoder
from digitalio import DigitalInOut, Direction, Pull

storage.remount("/", readonly=False)

# NeoPixels
num_pixels = 16
pixels = neopixel.NeoPixel(board.GP0, num_pixels)
pixels.brightness = 0.8

# Rotary Encoder
encoder = IncrementalEncoder(board.GP16, board.GP17)
button = DigitalInOut(board.GP18)
button.direction = Direction.INPUT
button.pull = Pull.UP

lastPos = 0 #None
mode = 1

redVal = 100
bluVal = 100
grnVal = 0

maxIntensity = 100
maxColourVal = 255

file = open("data.txt", "r")
data = file.read()
[colourVal, intensity] = data.split(",")
colourVal = int(colourVal)
intensity = int(intensity)
file.close()

lastPos = encoder.position

def colorwheel(color_value):
    """
    A colorwheel. ``0`` and ``255`` are red, ``85`` is green, and ``170`` is blue, with the values
    between being the rest of the rainbow.
    :param int color_value: 0-255 of color value to return
    :return: tuple of RGB values
    """
    if color_value < 0 or color_value > 255:
        return 0, 0, 0
    if color_value < 85:
        return 255 - color_value * 3, color_value * 3, 0
    if color_value < 170:
        color_value -= 85
        return 0, 255 - color_value * 3, color_value * 3
    color_value -= 170
    return color_value * 3, 0, 255 - color_value * 3

def color_chase(color, wait):
    for i in range(num_pixels):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.1)

def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = colorwheel(rc_index & 255)
            if button.value == 0:
                return None
        pixels.show()
        time.sleep(wait)
        
while True:
    if mode == 2:
        rainbow_cycle(0)
    # poll encoder position
    pos = encoder.position
    if pos != lastPos:
        if lastPos < pos:
            if mode == 1:
                if colourVal < maxColourVal:
                    colourVal = colourVal + 1
            elif mode == 0:
                if intensity < maxIntensity:
                    intensity = intensity + 1
        else:
            if mode == 1:
                if colourVal > 0:
                    colourVal = colourVal - 1
            elif mode == 0:
                if intensity > 0:
                    intensity = intensity - 1
        lastPos = pos
    
    # poll encoder button
    if button.value == 0:
        file = open("data.txt", "w")
        file.write(str(colourVal) + ",")
        file.write(str(intensity))
        file.close()
        mode = (mode + 1) % 3
        pixels.brightness = 0.2
        pixels.fill((100,100,100))
        time.sleep(0.3)
        
    if colourVal < 86:
        RGBVal = colourVal * 3
        redVal = RGBVal
        grnVal = 255 - RGBVal
        bluVal = 0
    elif colourVal < 171:
        RGBVal = (colourVal - 86) * 3
        redVal = RGBVal
        grnVal = 0
        bluVal = 255 - RGBVal
    elif colourVal < 256:
        RGBVal = (colourVal - 171) * 3
        redVal = 0
        grnVal = RGBVal
        bluVal = 255 - RGBVal
    else:
        RGBVal = (colourVal - 256) * 3
        redVal = RGBVal
        grnVal = RGBVal
        bluVal = RGBVal
        
    pixels.brightness = intensity * 0.01
    pixels.fill((redVal,grnVal,bluVal))
