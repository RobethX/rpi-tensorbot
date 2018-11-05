# import modules
#try:
#    import RPi.GPIO as GPIO
#except RuntimeError:
#    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
from EmulatorGUI import GPIO

import time
import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

tf.enable_eager_execution() #immediate mode for tf

from flask import Flask, render_template, request, Response, send_file

#learning parameters
alpha = 1e-3 #learning rate
gamma = 0.9 #discount factor

#setup pins
inChannels = []
outChannels = []
GPIO.setmode(GPIO.BOARD)
GPIO.setup(inChannels, GPIO.IN)
GPIO.setup(outChannels, GPIO.OUT)

#defining the robot
numLegs = 4
numJointsPerLeg = 2

class Joint:
    def __init__(self,m=0.0)
        self.m = m

class Leg:
    def __init__(self):
        self.joints = [joints() for _ in range(numJointsPerLeg)]

class Robot:
    def __init__(self):
        self.legs = [Leg() for _ in range(numLegs)]

def discount(r, gamma, normal):
    discount = 0; #placeholder
    return discount

#initialize tf session
r = Robot()
sess = tf.Session()
init = tf.global_variables_initializer()
sess.run(init)