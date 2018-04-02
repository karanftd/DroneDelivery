#!/usr/bin/env python
import pika
import sys
import pickle
from Job import *
import redis
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='task',
                         exchange_type='topic')

r = redis.Redis(host='localhost', port=6379, db=0)

assign_drone = ''

def get_free_drone():

    keys = r.keys(pattern="DroneID_*")
    '''
    "{
        '697b7fc5': {
            'state': 'Idle'
        }
    }"
    '''
    print keys
    for key in keys:
        
        # parse string to dictionary
        strVal = r.get(key)
        json_acceptable_string = strVal.replace("'", "\"")
        dictVal = json.loads(json_acceptable_string)

        # split to get Unique DroneID
        droneID = key.split('_')
        
        if dictVal[droneID[1]]['state'] == 'Idle':
            
            global assign_drone
            assign_drone = droneID[1]
            break
        else:
            continue
    else:
        print "no Drone is free " 


job = Job()
job.lattitude = 100
job.longitude = 100
job.base_lattitude = 0
job.base_longitude = 0
job.valocity = 20

pickled_object = pickle.dumps(job)

message = pickled_object

get_free_drone()

if assign_drone:
    
    channel.basic_publish(exchange='task',
                          routing_key=assign_drone,
                          body=message)
#print(" [x] Sent %r" % message)

connection.close()

