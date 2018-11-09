from luma.core import render, cmdline, error
import serial
import psutil
import socket
import sys
import os
from PIL import Image, ImageFont
import logging
import time

# logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)-15s - %(message)s'
)
# ignore PIL debug messages
logging.getLogger('PIL').setLevel(logging.ERROR)

def getIP(): #should I use psutil instead of socket?
    return "IP: " + socket.gethostbyname(socket.gethostname())

def getMemoryUsage():
    return "Mem: %.1f%%" %psutil.virtual_memory().percent

def getProcessorUsage():
    return "CPU: %.1f%%, %d MHz" % (psutil.cpu_percent(), psutil.cpu_freq().current)

def displaySettings(args): #Display a short summary of the settings.
    iface = ''
    display_types = cmdline.get_display_types()
    if args.display not in display_types['emulator']:
        iface = 'Interface: {}\n'.format(args.interface)

    lib_name = cmdline.get_library_for_display_type(args.display)
    if lib_name is not None:
        lib_version = cmdline.get_library_version(lib_name)
    else:
        lib_name = lib_version = 'unknown'

    import luma.core
    version = 'luma.{} {} (luma.core {})'.format(
        lib_name, lib_version, luma.core.__version__)

    return 'Version: {}\nDisplay: {}\n{}Dimensions: {} x {}\n{}'.format(
        version, args.display, iface, args.width, args.height, '-' * 60)

def getDevice(actual_args=None): #Create device from command-line arguments and return it.
    if actual_args is None:
        actual_args = sys.argv[1:]
    parser = cmdline.create_parser(description='luma.examples arguments')
    args = parser.parse_args(actual_args)

    if args.config:
        # load config from file
        config = cmdline.load_config(args.config)
        args = parser.parse_args(config + actual_args)

    print(displaySettings(args))

    # create device
    try:
        device = cmdline.create_device(args)
    except error.Error as e:
        parser.error(e)

    return device

def draw():
    if os.name == 'posix': #dont run on windows
        imageFont = ImageFont.truetype(os.path.abspath(os.path.join(os.path.dirname(__file__), "font.ttf")))

        device = getDevice()
        with render.canvas(device) as draw:
            while True: #where should this be?
                draw.text((0, 0), getIP(), font=imageFont, fill="white")
                if device.height >= 32:
                    draw.text((0, 14), "Running: " + "PLACEHOLDER", font=imageFont, fill="white") #str(r.isRunning)
                if (device.height >= 64):
                    draw.text((0, 26), getMemoryUsage(), font=imageFont, fill="white")
                    draw.text((0, 38), getProcessorUsage(), font=imageFont, fill="white")
                time.sleep(5)

if __name__ == "__main__":
    try:
        draw()
    except KeyboardInterrupt:
        pass