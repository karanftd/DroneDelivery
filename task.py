#!/usr/bin/env python
import pika
import sys
import pickle
from Job import *

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='task',
                         exchange_type='topic')



job = Job()
job.lattitude = 100
job.longitude = 100
job.base_lattitude = 0
job.base_longitude = 0
job.valocity = 20

pickled_object = pickle.dumps(job)

message = pickled_object

channel.basic_publish(exchange='task',
                      routing_key='b878de25',
                      body=message)
print(" [x] Sent %r" % message)

connection.close()

