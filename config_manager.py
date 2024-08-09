#!/usr/bin/env python
# coding=utf-8

import rospy
from std_msgs.msg import Int32, Float32
import yaml

rospy.init_node('config_manager', anonymous=True)
rate = rospy.Rate(5)
config = '/home/ubuntu/web/carousel_backend/config.yaml'
fullDict = {}

def loadConfig():
    global config, fullDict
    with open(config, "r") as file:
        fullDict = yaml.safe_load(file)
        # print(fullDict)

if len(fullDict) == 0:
    loadConfig()

#Stats
currentSpeed = fullDict['currentSpeed']
dropsAmount = fullDict['dropsAmount']
rotationAmount = fullDict['rotationAmount']
vaccinationAmount1 = fullDict['vaccinationAmount1']
vaccinationAmount2 = fullDict['vaccinationAmount2']

def callbackDrop(msg):
    global dropsAmount, config
    # rospy.loginfo(f"Drop is {msg}")
    dropsAmount = msg.data
    try:
        fullDict['dropsAmount'] = dropsAmount
        # with open(config, 'w') as file:
        #     yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
    except:
        None


def callbackSpeed(msg):
    global currentSpeed, config
    # rospy.loginfo(f"Speed is {msg}")
    currentSpeed = msg.data
    try:
        fullDict['currentSpeed'] = round(abs(currentSpeed), 2)
        # with open(config, 'w') as file:
        #     yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
    except:
        None

def callbackRot(msg):
    global rotationAmount, config
    # rospy.loginfo(f"Rot is {msg}")
    rotationAmount = msg.data
    try:
        fullDict['rotationAmount'] = rotationAmount
        # with open(config, 'w') as file:
        #     yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
    except:
        None

def callbackVac1(msg):
    global vaccinationAmount1, config
    # rospy.loginfo(f"vaccinationAmount1 is {msg}")
    vaccinationAmount1 = msg.data
    try:
        fullDict['vaccinationAmount1'] = vaccinationAmount1
        # with open(config, 'w') as file:
        #     yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
    except:
        None

def callbackVac2(msg):
    global vaccinationAmount2, config
    # rospy.loginfo(f"vaccinationAmount2 is {msg}")
    vaccinationAmount2 = msg.data
    try:
        fullDict['vaccinationAmount2'] = vaccinationAmount2
        # with open(config, 'w') as file:
        #     yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
    except:
        None

subDrop = rospy.Subscriber("/drop_counter", Int32, callbackDrop)
subSpeed = rospy.Subscriber("/current_speed_rotating_hangers_machine", Float32, callbackSpeed)
subRot = rospy.Subscriber("/number_of_turns", Int32, callbackRot)
subVac1 = rospy.Subscriber("/injection_counter_vet1", Int32, callbackVac1)
subVac2 = rospy.Subscriber("/injection_counter_vet2", Int32, callbackVac2)



class ConfigManager:
    def __init__(self):
        loadConfig()
        self.target_speed_pub = rospy.Publisher('/target_speed_rotating_hangers_machine', Float32, queue_size = 1)
        self.vac_pos_1_pub = rospy.Publisher('/position_vet1', Int32, queue_size = 1)
        self.vac_pos_2_pub = rospy.Publisher('/position_vet2', Int32, queue_size = 1)
        self.pusher_pub = rospy.Publisher('/tappet_mode', Int32, queue_size = 1)

    def sendConfig(self):
        try:
            loadConfig()
            if fullDict['startFlag']:
                if fullDict['rotDir'] == u'Против часовой':
                    target_speed = fullDict['targetSpeed']
                else:
                    target_speed = -fullDict['targetSpeed']
            else:
                target_speed = 0
            
            vac_pos_1 = fullDict['vacPos1']
            vac_pos_2 = fullDict['vacPos2']
            pusher = fullDict['pusher']

            pusher_options = {
                u'Без сброса' : 0,
                u'Сброс всех' : 1,
                u'Две вакцины' : 2,
                u'Одна вакцина' :3
            }

            self.target_speed_pub.publish(target_speed)
            self.vac_pos_1_pub.publish(vac_pos_1)
            self.vac_pos_2_pub.publish(vac_pos_2)
            self.pusher_pub.publish(pusher_options[pusher])
            print('out')

            rospy.loginfo("Configuration sent successfully")
        
        except IOError:
            rospy.logger("Configuration file not found")
        except yaml.YAMLError:
            rospy.logger("Error parsing config file")
        except Exception as e:
            rospy.logger("Unexpected error: {}".format(e))

if __name__ == '__main__':
    node = ConfigManager()
    while not rospy.is_shutdown():
        try:
            node.sendConfig()
            with open(config, 'w') as file:
                yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
            rate.sleep()
        except:
            pass
