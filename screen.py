from luma.core import render, cmdline, error
import serial
import psutil
import socket
import sys
import os
from PIL import Image, ImageFont
import logging
import time

#OLED display
def getIP(): #should I use psutil instead of socket?
    return "IP: " + socket.gethostbyname(socket.gethostname())

def getMemoryUsage():
    return "Mem: %.1f%%" %psutil.virtual_memory().percent

def getProcessorUsage():
    return "CPU: %.1f%%, %d MHz" % (psutil.cpu_percent(), psutil.cpu_freq().current)

def getDevice():
    parser = cmdline.create_parser(description="luma args")
    args = parser.parse_args(sys.argv[1:])

    if args.config: # load config from file
        config = cmdline.load_config(args.config)
        args = parser.parse_args(config + args)

        #display_types = cmdline.get_display_types()
    
        #lib_name = cmdline.get_library_for_display_type(args.display)
        #if lib_name is not None:
        #lib_version = cmdline.get_library_version(lib_name)
    #else:
        #lib_name = lib_version = "unknown"

    try:
        device = cmdline.create_device(args)
    except error.Error as e:
        parser.error(e)
        logging.error("Could not setup display!")
    
    return device

def draw():
    imageFont = ImageFont.truetype(os.path.abspath(os.path.join(os.path.dirname(__file__), "font.ttf")))

    device = getDevice()
    with render.canvas(device) as draw:
        while True: #where should this be?
            #draw.text((0, 14), "Running: " + str(r.isRunning), font=imageFont, fill="white")
            draw.text((0, 0), getIP(), font=imageFont, fill="white")
            if (device.height >= 64):
                draw.text((0, 26), getMemoryUsage(), font=imageFont, fill="white")
                draw.text((0, 38), getProcessorUsage(), font=imageFont, fill="white")
            time.sleep(5)

if __name__ == "__main__":
    try:
        draw()
    except KeyboardInterrupt:
        pass