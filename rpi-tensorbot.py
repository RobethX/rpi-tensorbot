# import modules
#try:
#    import RPi.GPIO as GPIO
#except RuntimeError:
#    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

import time
import os
import sys
import psutil
import socket
from multiprocessing import Process, Pool, Manager, Value
import logging
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from keras import backend
from keras.models import Model
#from keras.

tf.enable_eager_execution() #immediate mode for tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = "3"

from flask import Flask, render_template, request, Response, send_file

os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')
from gpiozero import Motor, LED, PingServer, DistanceSensor
#from mpu6050 import mpu6050 #apt install python3-smbus
from luma.core import render, cmdline, error
import serial
#TODO use arduino instead of only raspi's GPIO pins

from PIL import Image, ImageFont

#logging
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
#TODO

#learning hyperparameters
alpha = 0.01 #learning rate
gamma = 0.95 #discount factor - future reward rate
epsilonMax = 0.95 #e-greedy
epsilonMin = 0.0001
episodeDuration = 60 #seconds

#A Vector3 class for Python
class Vector3:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def zero(self):
        self.x = 0
        self.y = 0
        self.z = 0

#defining the robot
numLegs = 4
numJointsPerLeg = 2

class Joint:
    def __init__(self, a, b, m = 0.0, Q=tf.zeros((3,3))):
        self.m = m
        self.Q = Q
        #self.motor = Motor(a, b)

class Leg:
    def __init__(self):
        self.joints = [Joint(1, 2) for _ in range(numJointsPerLeg)] #fix pins -- assign joins' pins manually?

class Robot: #agent
    def __init__(self):
        self.legs = [Leg(), Leg(), Leg(), Leg()]
        #self.distanceSensors = [DistanceSensor(3, 4)]
        #self.positionSensor = mpu6050(0x68) #not sure how to tell address/how it converts to pin num
        #self.positionSensor.set_accel_range(1)
        #self.positionSensor.set_gyro_range(1)
        self.distanceFromGround = 0 #set to actual value
        self.position = Vector3()
        self.velocity = Vector3()
        self.acceleration = Vector3()
        self.rotation = Vector3() #x = roll, y = pitch, z = yaw

        self.isRunning = False

        self.Q = tf.zeros((3,3))
        self.epsilon = epsilonMax
        self.model = None
        self.modelTarget = None

        #self.accelerometer = positionSensor.get_accel_data()
        #self.gyroscope = positionSensor.get_gyro_data()

    def isReady(self): #TODO
        return True #TODO if upright, etc.

    def reset(self):
        logging.info("Resetting...")
        self.stop() #if running
        #reset motors
        #warn if pitch or roll too far extreme (upside down?)
        self.calibrate()
        #homing system with auxilary motion (wheels)?
        #rotate 180 degrees before starting again?
        return True

    def calibrate(self):
        logging.info("Calibrating...")
        self.position.zero()
        self.velocity.zero()
        #zero pitch and roll, leave yaw
        self.rotation.x = 0
        self.rotation.y = 0
        return True

    def start(self, episodes = 1):
        if (self.isRunning == True): #warn if already running
            logging.warn("Episode already running!")
            return False

        logging.info("Starting... Will run " + int(episodes) + " time(s)")
        self.isRunning = True
        for i in range(1, episodes):

            time.sleep(4) #rest for a few seconds before resetting
            self.reset() #move back to original position?
            time.sleep(1) #rest for a second before starting

            timeEpisodeStarted = time.time()
            while (time.time() - timeEpisodeStarted < episodeDuration):
                n = 10 #TODO figure out what n should be
                #a = np.argmax(Q[s,:] + np.random.randn(1, n) * (1. / (i + 1))) #choose action greedily TODO

            logging.info("Finished episode " + i + " with a success rate of ") #TODO print out success
            i += 1 #add one to i before starting loop over

        return True

    def stop(self):
        if (self.isRunning == False): #warn if not running
            logging.warn("Tried to stop but nothing is running!")
            return False

        logging.info("Stopping gracefully...")
        self.isRunning = False
        return True

    def kill(self): #force stop
        logging.info("Stopping forcefully...")
        self.isRunning = False
        return True

    def setAlpha(self, t = 0.0):
        logging.info("setAlpha") #TODO

    def timeflow(self, t = 0.0):
        self.setAlpha(t)

        for i in range(len(self.legs)):
            Qs = [tf.matmul(self.Q, self.legs[i].joints[0].Q)]
            for ii in range(1, len(self.legs[i].joints)):
                Qs.append(tf.matmul(Qs[ii-1], self.legs[i].joints[ii].Q))

def discount(r, gamma, normal):
    discount = 0 #placeholder
    return discount

#Main
if __name__ == "__main__":
    pool = Pool() #how many processes?
    
    r = Robot()
    #r.timeflow()

    #control panel website
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = b'secret'

    @app.route("/")
    def webIndex():
        return render_template('index.html', title='Control Panel')

    @app.route("/reset", methods=['GET', 'POST'])
    def webReset():
        pool.apply_async(r.reset())
        return ('', 204)

    @app.route("/calibrate", methods=['GET', 'POST'])
    def webCalibrate():
        pool.apply_async(r.calibrate())
        return ('', 204)

    @app.route("/start", methods=['GET', 'POST'])
    def webStart():
        pool.apply_async(r.start(request.form['episodes']))
        return ('', 204)

    @app.route("/stop", methods=['GET', 'POST'])
    def webStop():
        pool.apply_async(r.stop())
        return ('', 204)

    @app.route("/kill", methods=['GET', 'POST'])
    def webKill():
        pool.apply_async(r.kill())
        return ('', 204)

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

    def drawDisplay():
        imageFont = ImageFont.truetype(os.path.abspath(os.path.join(os.path.dirname(__file__), "font.ttf")))

        with render.canvas(getDevice()) as draw:
            while True: #where should this be?
                draw.text((0, 0), getIP() + " Running: " + r.isRunning, font=imageFont, fill="white")
                draw.text((0, 14), getMemoryUsage() + " " + getProcessorUsage(), font=imageFont, fill="white")
                time.sleep(5)

    #initialize tf session
    sess = tf.Session()
    init = tf.global_variables_initializer()
    backend.set_session(sess) #Keras

    globalStep = tf.train.get_or_create_global_step()
    summaryWriter = tf.contrib.summary.create_file_writer('./logs', flush_millis=10000)

    #with Manager() as manager, summaryWriter.as_default(), tf.contrib.summary.always_record_summaries():
#        tf.contrib.summary.scalar("loss", loss)
#        train_op = ....

    #pool.apply_async(drawDisplay()) #TODO DOES NOT WORK ON WINDOWS!
    app.run(host='0.0.0.0') #temporary, use lighttpd
    #every x seconds check for connection to web server - if not found, stop and warn

#    with tf.Session(...) as sess:
#       tf.global_variables_initializer().run()
#       tf.contrib.summary.initialize(graph=tf.get_default_graph())
    # ...
#       while not_done_training:
#            sess.run([train_op, tf.contrib.summary.all_summary_ops()])
