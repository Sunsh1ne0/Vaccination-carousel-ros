#!/usr/bin/env python
# coding=utf-8

import rospy
from std_msgs.msg import Int32, Float32
import yaml
import psycopg2
from datetime import datetime

rospy.init_node('config_manager', anonymous=True)
rate = rospy.Rate(5)
config = '/home/ubuntu/web/carousel_backend/config.yaml'
fullDict = {}
fullDictOffset = {}
sessionPrev = None

def connect_to_db():
    global conn
    try:
    # пытаемся подключиться к базе данных
        conn = psycopg2.connect(dbname='carousel_db', user='postgres', password='Robot123', host="10.5.0.5", port="5432")
        print("Connecting to carousel")
        return 0
    except:
        # в случае сбоя подключения будет выведено сообщение
        print('Can`t establish connection to database')
        conn = None
        return 1

def init_tables():
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('CREATE TABLE IF NOT EXISTS carousel_stats (id Serial, timestamp TIMESTAMP, current_speed float8, dropsAmount INT, rotationAmount INT, vaccinationAmount1 INT, vaccinationAmount2 INT, startFlag boolean, sessionFlag boolean, sessionNum INT)')
                curs.execute('SELECT * FROM carousel_stats ORDER BY id DESC LIMIT 1')
                rows = curs.fetchall()
                if len(rows) == 0:
                    curs.execute('INSERT INTO carousel_stats (timestamp, current_speed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag, sessionNum) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (datetime.now(), 0, 0, 0, 0, 0, False, False, 0))
                    conn.commit()
        
                curs.execute('CREATE TABLE IF NOT EXISTS carousel_settings (id Serial, timestamp TIMESTAMP, rotDir text, targetSpeed float8, vacPos1 INT, vacPos2 INT, pusher text)')                
                curs.execute('SELECT * FROM carousel_settings ORDER BY id DESC LIMIT 1')
                rows = curs.fetchall()
                if len(rows) == 0:
                    curs.execute('INSERT INTO carousel_settings (timestamp, rotDir, targetSpeed, vacPos1, vacPos2, pusher) VALUES (%s, %s, %s, %s, %s, %s)', (datetime.now(), 'Counterclockwise', 1.8, 2, 3, 'Drop all'))
                    conn.commit()
            return 0
        return 'NO CONNECTION (INITIALIZE)'
    except:
        return 1

def update_settings(rotDir, targetSpeed, vacPos1, vacPos2, pusher):
    try:
        print(conn)
        if conn:
            with conn.cursor() as curs:
                curs.execute('UPDATE carousel_settings SET timestamp = %s, rotDir = %s, targetSpeed = %s, vacPos1 = %s, vacPos2 = %s, pusher = %s WHERE id = %s', (datetime.now(), rotDir, targetSpeed, vacPos1, vacPos2, pusher, 1))
                conn.commit()
                return 0
        return 'NO CONNECTION (UPDATE SETTINGS)'
    except:
        return 1
    
def update_stats(currentSpeed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag, sessionNum):
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('INSERT INTO carousel_stats (timestamp, current_speed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag, sessionNum) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (datetime.now(), currentSpeed, dropsAmount, rotationAmount, vaccinationAmount1, vaccinationAmount2, startFlag, sessionFlag, sessionNum))
                conn.commit()
                return 0
        return 'NO CONNECTION (UPDATE STATS)'
    except:
        return 1
    
def read_stats():
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('SELECT * FROM carousel_stats ORDER BY id DESC LIMIT 1')
                rows = curs.fetchall()
                return rows
        return 'NO CONNECTION (READ STATS)'
    except:
        return []

def read_settings():
    try:
        if conn:
            with conn.cursor() as curs:
                curs.execute('SELECT * FROM carousel_settings WHERE id = %s', (1,))
                rows = curs.fetchall()
                return rows
        return 'NO CONNECTION (READ SETTINGS)'
    except:
        return []

def loadConfig():
    global config, fullDict, sessionPrev
    
    tempList = read_settings()[0]
    fullDict['rotDir'] = tempList[2]
    fullDict['targetSpeed'] = tempList[3]
    fullDict['vacPos1'] = tempList[4]
    fullDict['vacPos2'] = tempList[5]
    fullDict['pusher'] = tempList[6]

    tempList = read_stats()
    print(tempList)
    if len(tempList) == 0:
        fullDict['dropsAmount'] = 0
        fullDict['rotationAmount'] = 0
        fullDict['vaccinationAmount1'] = 0
        fullDict['vaccinationAmount2'] = 0
        fullDict['startFlag'] = False
        fullDict['sessionFlag'] = False
        fullDict['sessionNum'] = 0
    else:
        tempList = tempList[0]
        fullDict['startFlag'] = tempList[7]
        fullDict['sessionFlag'] = tempList[8]
        fullDict['sessionNum'] = tempList[9]
    
    print(sessionPrev)
    if sessionPrev and not fullDict['sessionFlag']:
        fullDict['sessionNum'] = fullDict['sessionNum'] + 1
        fullDictOffset['dropsAmount'] = - fullDict['dropsAmount']
        fullDictOffset['vaccinationAmount1'] = - fullDict['vaccinationAmount1']
        fullDictOffset['vaccinationAmount2'] = - fullDict['vaccinationAmount2']
        fullDictOffset['rotationAmount'] = - fullDict['rotationAmount']

    sessionPrev = fullDict['sessionFlag']

if len(fullDict) == 0:
    connect_to_db()
    print(init_tables())
    tempList = read_settings()[0]
    fullDict['rotDir'] = tempList[2]
    fullDict['targetSpeed'] = tempList[3]
    fullDict['vacPos1'] = tempList[4]
    fullDict['vacPos2'] = tempList[5]
    fullDict['pusher'] = tempList[6]

    tempList = read_stats()
    if len(tempList) == 0:
        fullDict['currentSpeed'] = 0
        fullDict['dropsAmount'] = 0
        fullDict['rotationAmount'] = 0
        fullDict['vaccinationAmount1'] = 0
        fullDict['vaccinationAmount2'] = 0
        fullDict['startFlag'] = False
        fullDict['sessionFlag'] = False
        fullDict['sessionNum'] = 0
    else:
        tempList = tempList[0]
        fullDict['currentSpeed'] = 0
        fullDict['dropsAmount'] = tempList[3]
        fullDict['rotationAmount'] = tempList[4]
        fullDict['vaccinationAmount1'] = tempList[5]
        fullDict['vaccinationAmount2'] = tempList[6]
        fullDict['startFlag'] = False
        fullDict['sessionFlag'] = tempList[8]
        fullDict['sessionNum'] = tempList[9]
    
    update_stats(fullDict['currentSpeed'], fullDict['dropsAmount'], fullDict['rotationAmount'], fullDict['vaccinationAmount1'], fullDict['vaccinationAmount2'], fullDict['startFlag'], fullDict['sessionFlag'], fullDict['sessionNum'] )
    sessionPrev = fullDict['sessionFlag']


if (fullDict['sessionFlag']):
    fullDictOffset['dropsAmount'] = fullDict['dropsAmount']
    fullDictOffset['vaccinationAmount1'] = fullDict['vaccinationAmount1']
    fullDictOffset['vaccinationAmount2'] = fullDict['vaccinationAmount2']
    fullDictOffset['rotationAmount'] = fullDict['rotationAmount']
else:
    fullDictOffset['dropsAmount'] = 0
    fullDictOffset['vaccinationAmount1'] = 0
    fullDictOffset['vaccinationAmount2'] = 0
    fullDictOffset['rotationAmount'] = 0

fullDict['targetSpeed'] = 1.8
fullDict['currentSpeed'] = 0
fullDict['rotationAmount'] = 0
fullDict['dropsAmount'] = 0
fullDict['vaccinationAmount1'] = 0
fullDict['vaccinationAmount2'] = 0

#Stats
currentSpeed = fullDict['currentSpeed']
dropsAmount = fullDict['dropsAmount']
rotationAmount = fullDict['rotationAmount']
vaccinationAmount1 = fullDict['vaccinationAmount1']
vaccinationAmount2 = fullDict['vaccinationAmount2']

def callbackDrop(msg):
    global dropsAmount, fullDict
    dropsAmount = msg.data
    try:
        fullDict['dropsAmount'] = dropsAmount
    except:
        None


def callbackSpeed(msg):
    global currentSpeed, fullDict
    currentSpeed = msg.data
    try:
        fullDict['currentSpeed'] = round(abs(currentSpeed), 2)
    except:
        None

def callbackRot(msg):
    global rotationAmount, fullDict
    rotationAmount = msg.data
    try:
        fullDict['rotationAmount'] = rotationAmount
    except:
        None

def callbackVac1(msg):
    global vaccinationAmount1, fullDict
    vaccinationAmount1 = msg.data
    try:
        fullDict['vaccinationAmount1'] = vaccinationAmount1
    except:
        None

def callbackVac2(msg):
    global vaccinationAmount2, fullDict
    vaccinationAmount2 = msg.data
    try:
        fullDict['vaccinationAmount2'] = vaccinationAmount2
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
                if fullDict['rotDir'] == u'Counterclockwise':
                    target_speed = fullDict['targetSpeed']
                else:
                    target_speed = -fullDict['targetSpeed']
            else:
                target_speed = 0
            
            vac_pos_1 = fullDict['vacPos1']
            vac_pos_2 = fullDict['vacPos2']
            pusher = fullDict['pusher']

            pusher_options = {
                u'Drop none' : 0,
                u'Drop all' : 1,
                u'Two vaccines' : 2,
                u'One vaccine' :3
            }

            self.target_speed_pub.publish(target_speed)
            self.vac_pos_1_pub.publish(vac_pos_1)
            self.vac_pos_2_pub.publish(vac_pos_2)
            self.pusher_pub.publish(pusher_options[pusher])
            # print('out')

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
            update_stats(fullDict['currentSpeed'], fullDict['dropsAmount'] + fullDictOffset['dropsAmount'], fullDict['rotationAmount'] + fullDictOffset['rotationAmount'], fullDict['vaccinationAmount1'] + fullDictOffset['vaccinationAmount1'], fullDict['vaccinationAmount2'] + fullDictOffset['vaccinationAmount2'], fullDict['startFlag'], fullDict['sessionFlag'], fullDict['sessionNum'] )

            rate.sleep()
        except:
            pass
