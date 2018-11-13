#TODO divide the program into multiple files for readability

# import modules
#try:
#    import RPi.GPIO as GPIO
#except RuntimeError:
#    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

import time
import os
import sys
from multiprocessing import Process, Pool, Manager, Value
import logging
import json
import numpy as np
#import tensorflow as tf
import gc
from flask import Flask, render_template, request, Response, send_file
import robot

os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')
from gpiozero import Motor, LED, PingServer, DistanceSensor
#import smbus2 #confgure i2c devices
#TODO use arduino instead of only raspi's GPIO pins (maybe)
if os.name == 'posix': #dont run on windows
    import screen
    from mpu6050 import mpu6050 #apt install python3-smbus
#else: #only run on windows
    #os.environ["PATH"] = "C:\\Users\\rmchi\\.mujoco\\mjpro150\\bin"

#from gym.envs.mujoco import AntEnv
#logging
logging.basicConfig(format='%(relativeCreated)6d %(threadName)s %(message)s') #level=logging.DEBUG, 
#TODO

env = robot.Environment() #TODO finish custom environment
agent = robot.Actor()

def runEpisode(): #use runner? #TODO this is a placeholder
    ob = env.reset() #why ob?
    totreward = 0 #what does this mean?
    while True:
        action = agent.act(ob)
        #ob, reward, done, _ = env.step(action) #what is _? 
        totreward = totreward + reward
        agent.observe(reward=np.nan_to_num(reward), terminal=done)
        time.sleep(0.1) #pause
        if done:
            gc.collect()
            return totreward #return last reward

#Main
if __name__ == "__main__":
    try: #try loading previous session data
        agent.restore("./data/") #what should I call this?
    except:
        logging.info("No previous data found. Starting fresh.")

    pool = Pool() #how many processes?
    
    r = robot.Robot()

    #control panel website
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = b'secret'

    @app.route("/")
    def webIndex():
        return render_template('index.html', title='Control Panel')

    @app.route("/reset", methods=['GET', 'POST'])
    def webReset():
        #pool.apply_async(r.reset())
        r.reset()
        return ('', 204)

    @app.route("/calibrate", methods=['GET', 'POST'])
    def webCalibrate():
        #pool.apply_async(r.calibrate())
        r.calibrate()
        return ('', 204)

    @app.route("/start", methods=['GET', 'POST'])
    def webStart():
        #pool.apply_async(r.start(request.form['episodes']))
        r.start(request.form['episodes'])
        return ('', 204)

    @app.route("/stop", methods=['GET', 'POST'])
    def webStop():
        #pool.apply_async(r.stop())
        r.stop()
        return ('', 204)

    @app.route("/kill", methods=['GET', 'POST'])
    def webKill():
        #pool.apply_async(r.kill())
        r.kill()
        return ('', 204)

    @app.route("/shutdown", methods=['GET', 'POST'])
    def webShutdown():
        if os.name == 'posix': #dont run on windows
            r.stop()
            logging.info("Shutting down...")
            os.system("sudo shutdown -h -t 5") #time does not seem to work - should I do shutdown now?
        else:
            logging.info("Not shutting down because the server is not running on a RaspberryPi!")
        return ('', 204)

    @app.route("/status")
    def webStatus():
        return r.isRunning

    try:
        if os.name == 'posix': #dont run on windows
            pool.apply_async(screen.update)
        app.run(host='0.0.0.0') #TODO temporary, use lighttpd
        #every x seconds check for connection to web server - if not found, stop and warn
    except KeyboardInterrupt:
        pass

    if os.name == 'posix': #dont run on windows
        screen.disp.clear() #clear screen so the info does not linger after the script is closed