# EE 250: Lab 6

import sys
import time
import grovepi as gp

# From GrovePi Git repository
if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)

# I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

# Set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# Send command to display (no need for external use)
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

# Set display text \n for second line (or auto wrap)
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

# Update the display without erasing the display
def setText_norefresh(text):
    textCommand(0x02) # return home
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    while len(text) < 32: #clears the rest of the screen
        text += ' '
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

if __name__ == '__main__':

    while True:

        # Connect ultrasonic ranger to digital port D4
        ultrasonic_ranger = 4

        # Connect rotary angle sensor to analog port A0
        potentiometer = 0

        while True:
            
            # Read sensor value from rotary angle sensor
            sensor_value = gp.analogRead(potentiometer)
            
            # Map rotary angle sensor values of [0, 1023] to ultrasonic range of [0, 517]
            mapped_rotary = int((float(sensor_value)/1023)*517)
            print("Threshold: " + str(mapped_rotary)) # Display mapped threshold value on terminal
        
            # Read distance value from ultrasonic ranger
            ultrasonic_distance = gp.ultrasonicRead(ultrasonic_ranger)
            print("Current: " + str(ultrasonic_distance)) # Display ultrasonic distance value on terminal

            # Check if object is closer than the set threshold
            objInRange = "         " # Empty string
            if ultrasonic_distance < mapped_rotary:
              objInRange = " OBJ PRES"
              setRGB(235, 10, 10) # Set background color of LCD to red
            else:
              setRGB(20, 245, 90) # Set background color of LCD to green

            # Set text on the LCD
            setText_norefresh(str(mapped_rotary) + "cm" + objInRange + "\n" + str(ultrasonic_distance) + "cm")
            
            time.sleep(0.1) # don't overload the i2c bus
