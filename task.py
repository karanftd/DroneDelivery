#!/usr/bin/env python
import pika
import sys
import pickle
from Job import *
import redis

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='task',
                         exchange_type='topic')

r = redis.Redis(host='localhost', port=6379, db=0)

assign_drone = ''

def get_free_drone():

    keys = r.keys()

    for key in keys:
        
        if r.get(key) == 'Idle':
            
            global assign_drone
            assign_drone = key
            break
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

print assign_drone

get_free_drone()

print assign_drone

if assign_drone:
    
    channel.basic_publish(exchange='task',
                          routing_key=assign_drone,
                          body=message)
#print(" [x] Sent %r" % message)

connection.close()

