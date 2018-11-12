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
import tensorforce.environments
from tensorforce.agents import Agent
from tensorforce.execution import Runner
from tensorforce.contrib.openai_gym import OpenAIGym #DEBUG
import tensorforce.util
from gym.envs.mujoco import AntEnv
from flask import Flask, render_template, request, Response, send_file

os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')
from gpiozero import Motor, LED, PingServer, DistanceSensor
#import smbus2 #confgure i2c devices
#TODO use arduino instead of only raspi's GPIO pins (maybe)
if os.name == 'posix': #dont run on windows
    import screen
    from mpu6050 import mpu6050 #apt install python3-smbus

#logging
logging.basicConfig(format='%(relativeCreated)6d %(threadName)s %(message)s') #level=logging.DEBUG, 
#TODO

#learning hyperparameters
alpha = 0.01 #learning rate
gamma = 0.95 #discount factor - future reward rate
epsilonMax = 0.95 #e-greedy
epsilonMin = 0.0001
episodeDuration = 60 #seconds

#Tensorforce setup
class Environment(tensorforce.environments.Environment):
    def close(self):
        #TODO
        pass

    def seed(self, seed):
        #TODO
        return None

    def reset(self):
        logging.info("Not implemented") #TODO

    def execute(self, action):
        logging.info("Not implemented") #TODO

    @property
    def states(self):
        logging.info("Not implemented") #TODO

    @property
    def actions(self):
        logging.info("Not implemented") #TODO

    @staticmethod
    def from_spec(spec, kwargs):
        env = tensorforce.util.get_object(
            obj=spec,
            #predefined_objects=tensorforce.environments.environments, #TODO
            kwargs=kwargs
        )
        assert isinstance(env, Environment)
        return env

#env = Environment() #TODO finish custom environment
env = OpenAIGym(
    gym_id=AntEnv, #OpenAI Gym environment ID.
    monitor=False, #Output directory, False disables monitoring
    monitor_safe=False, #Prevents overwriting logs
    monitor_video=False, #save video every "monitor_video" steps
    visualize=True #visualize training environment - NOTE: slows down training
)

#load neural network config
with open("network.json", "r") as f:
    networkSpec = json.load(f)

#load agent config
with open("agent.json", "r") as f:
    agentConfig = json.load(f)

#agent = Agent.from_spec(
#    spec=agentConfig,
#    kwargs=dict(
#        states=env.states,
#        actions=env.actions,
#        network=networkSpec
#    )
#)

#runner = Runner(agent=agent, environment=env)

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
    def __init__(self, pin1, pin2):
        logging.info("Not implemented") #TODO
        #self.motor = Motor(pin1, pin2)

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

        #TODO work out velocity, rotation, and position from acceleration and rotational velocity
        #self.accelerometer = self.positionSensor.get_accel_data()
        #self.gyroscope = self.positionSensor.get_gyro_data()

        self.isRunning = False      
    #TODO seperate agent and environment functions from robot, do them seperately
    def episodeFinished(self, r):
        if r.episode % 100 == 0:
            sps = r.timestep / (time.time() - r.start_time)
            logging.info("Finished episode {ep} after {ts} timesteps. Steps Per Second {sps}".format(ep=r.episode, ts=r.timestep, sps=sps))
            logging.info("Episode reward: {}".format(r.episode_rewards[-1]))
            logging.info("Episode timesteps: {}".format(r.episode_timestep))
            logging.info("Average of last 500 rewards: {}".format(sum(r.episode_rewards[-500:]) / 500))
            logging.info("Average of last 100 rewards: {}".format(sum(r.episode_rewards[-100:]) / 100))
        return True

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

        #runner.run(
        #    timesteps=6000000, #TODO set timesteps
        #    episodes=episodes,
        #    max_episode_timesteps=10000,
        #    deterministic=False,
        #    episode_finished=self.episodeFinished
        #)

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
    def shutdown():
        if os.name == 'posix': #dont run on windows
            r.stop()
            logging.info("Shutting down...")
            os.system("sudo shutdown -h -t 5") #time does not seem to work - should I do shutdown now?
        else:
            logging.info("Not shutting down because the server is not running on a RaspberryPi!")
        return ('', 204)

    @app.route("/status")
    def status():
        return r.isRunning

    try:
        if os.name == 'posix': #dont run on windows
            pool.apply_async(screen.update) #TODO DOES NOT WORK ON WINDOWS!
        app.run(host='0.0.0.0') #temporary, use lighttpd
        #every x seconds check for connection to web server - if not found, stop and warn
    except KeyboardInterrupt:
        if os.name == 'posix': #dont run on windows
            screen.disp.clear() #clear screen so the info does not linger after the script is closed
        pass