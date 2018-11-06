# import modules
#try:
#    import RPi.GPIO as GPIO
#except RuntimeError:
#    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

import time
import os
import sys
import threading
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import logging

tf.enable_eager_execution() #immediate mode for tf

from flask import Flask, render_template, request, Response, send_file

os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')
from gpiozero import Motor, LED, PingServer, DistanceSensor
#from mpu6050 import mpu6050 #apt install python3-smbus

#logging
#TODO

#learning hyperparameters
alpha = 0.01 #learning rate
gamma = 0.9 #discount factor - future reward rate
epsilonMax = 0.9 #e-greedy

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

        self.Q = tf.zeros((3,3))

        #self.accelerometer = positionSensor.get_accel_data()
        #self.gyroscope = positionSensor.get_gyro_data()

    def reset(self):
        logging.info("Resetting...")
        self.stop() #if running
        #reset motors
        #warn if pitch or roll too far extreme (upside down?)
        self.calibrate()
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
        logging.info("Starting... Will run " + episodes + " times")
        return True

    def stop(self):
        logging.info("Stopping gracefully...")
        return True

    def kill(self): #force stop
        logging.info("Stopping forcefully...")
        return True

    def setAlpha(self, t = 0.0):
        logging.info("setAlpha") #TODO

    def timeflow(self, t = 0.0):
        self.setAlpha(t)

        for i in range(len(self.legs)):
            Qs = [tf.matmul(self.Q, self.legs[i].joints[0].Q)]
            for ii in range(1, len(self.legs[i].joints)):
                Qs.append(tf.matmul(Qs[ii-1], self.legs[i].joints[ii].Q))

r = Robot()
#r.timeflow()

def discount(r, gamma, normal):
    discount = 0; #placeholder
    return discount

#control panel website
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = b'secret'

@app.route("/")
def webIndex():
    return render_template('index.html', title='Control Panel')

@app.route("/reset", methods=['GET', 'POST'])
def webReset():
    r.reset()
    return ('', 204)

@app.route("/calibrate", methods=['GET', 'POST'])
def webCalibrate():
    r.calibrate()
    return ('', 204)

@app.route("/start", methods=['GET', 'POST'])
def webStart():
    r.start(request.form['episodes'])
    return ('', 204)

@app.route("/stop", methods=['GET', 'POST'])
def webStop():
    r.stop()
    return ('', 204)

@app.route("/kill", methods=['GET', 'POST'])
def webKill():
    r.kill()
    return ('', 204)

#Deep Q Network off-policy learning
class DeepQNetwork:
    def __init__(self, actions, features, learningRate, rewardDecay, eGreedy, replaceTargetIterator = 300, memorySize = 500, batchSize = 32, eGreedyIncriment = None, outputGraph = False):
        self.actions = actions
        self.features = features
        self.alpha = learningRate
        self.gamma = rewardDecay
        self.epsilonMax = eGreedy
        self.replaceTargetIterator = replaceTargetIterator
        self.memorySize = memorySize
        self.batchSize = batchSize
        self.epsilonIncriment = eGreedyIncriment
        self.epsilon = 0 if eGreedyIncriment is not None else self.epsilonMax

        self.learnStepCounter = 0

        self.memory = np.zeros((self.memorySize, features * 2 + 2))

#initialize tf session
sess = tf.Session()
init = tf.global_variables_initializer()

globalStep = tf.train.get_or_create_global_step()
summaryWriter = tf.contrib.summary.create_file_writer('./logs', flush_millis=10000)

#sess.run(init)

if __name__ == "__main__":
#    with summaryWriter.as_default(), tf.contrib.summary.always_record_summaries():
#        tf.contrib.summary.scalar("loss", loss)
#        train_op = ....

    app.run(host='0.0.0.0') #temporary, use lighttpd
    #every x seconds check for connection to web server - if not found, stop and warn

#    with tf.Session(...) as sess:
#       tf.global_variables_initializer().run()
#       tf.contrib.summary.initialize(graph=tf.get_default_graph())
    # ...
#       while not_done_training:
#            sess.run([train_op, tf.contrib.summary.all_summary_ops()])
