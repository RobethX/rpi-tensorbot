import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import serial
import psutil
import socket
import sys
import os
from PIL import Image, ImageFont, ImageDraw
import logging
import time

import subprocess

def getIP(): #should I use psutil instead of socket?
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True ).strip() #TODO can I do this a better way????
    return "IP: " + IP.decode('ascii') #socket.gethostbyname(socket.gethostname())

def getStatus():
    return "Status: " + str(True) #TODO #str(r.isRunning)

def getMemoryUsage():
    return "Mem: %.1f%%" %psutil.virtual_memory().percent

def getProcessorUsage():
    return "CPU: %.1f%%, %d MHz" % (psutil.cpu_percent(), psutil.cpu_freq().current)

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_address=0x3C) #128x32 display with set I2C address

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()
#font = ImageFont.truetype('font.ttf', 8)

def update():
    if os.name == 'posix': #dont run on windows
        while True:
            draw.rectangle((0,0,width,height), outline=0, fill=0) #clear screen

            draw.text((x, top), getIP(), font=font, fill="white")
            draw.text((x, top+8), getStatus(), font=font, fill="white") 
            draw.text((x, top+16), getMemoryUsage(), font=font, fill="white")
            draw.text((x, top+25), getProcessorUsage(), font=font, fill="white")

            #display image
            disp.image(image)
            disp.display()
            time.sleep(3)

if __name__ == "__main__":
    try:
        update()
    except KeyboardInterrupt:
        pass