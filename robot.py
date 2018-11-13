import time
import numpy as np
import tensorforce.environments
#from tensorforce.agents import PPOAgent
import logging

logging.basicConfig(format='%(relativeCreated)6d %(threadName)s %(message)s', level=logging.INFO) # #TODO should I have a header type file for stuff like this?

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

        logging.info("Starting (well, not really)")
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

class Actor:
    def __init__(self):
        actions = {}
        actionsExploration = {}
        for i in range(12): #why 12?
            actions[str(i)] = {"type": "float"}

        layerSize = 300 #how big should this be?

        networkSpec = [
            dict(type='dense', size=layerSize, activation='selu'), #what is selu?
            dict(type='dense', size=layerSize, activation='selu'),
            dict(type='dense', size=layerSize, activation='selu')
        ]

        preprocessingConfig = None #what is this

        #self.agent = PPOAgent(
        #    states=dict(type='float', shape=(12+9,)), #why define the shape?
        #    actions=actions,
        #    batching_capacity=1000,
        #    network=networkSpec,
        #    states_preprocessing=preprocessingConfig,
        #    actions_exploration=actionsExploration,
        #    step_optimizer=dict(
        #        type="adam",
        #        learning_rate=1e-5 #alpha
        #    ),
        #)

    def act(self, state): #TODO
        jp = np.expand_dims( np.nan_to_num( np.array(state["JointPosition"] ) ),axis=0)
        #jv = np.expand_dims(np.array(state["JointVelocity"]), axis=0)
        orient = np.expand_dims( np.array(state["bodyRot"]), axis=0 )
        actiondict = self.agent.act( np.nan_to_num( np.concatenate([jp,orient],axis=1) ) / 5.0 )
        #actiondict = self.agent.act(jp)

        action = np.zeros(12)
        for i in range(12):
            action[i] = actiondict[str(i)][0]
        action = np.nan_to_num(action)
        #print(action)
        return np.clip(action,-1.0,1.0)

    def observe(self, reward, terminal):
        self.agent.observe(reward=reward,terminal=terminal)

    def save(self,directory):
        self.agent.save_model(directory=directory)

    def restore(self,directory):
        self.agent.restore_model(directory=directory)