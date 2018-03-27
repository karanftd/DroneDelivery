#-- Application constant 
import enum
from random import *
from Job import *
import uuid
import pika
import pickle
import sys
import redis
import time


r = redis.Redis(host='localhost', port=6379, db=0)
#redis data structure
'''
{
	"drone_id": state,
}

'''


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='task',exchange_type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue




# creating enumerations using class
class DroneState(enum.Enum):
    
    Idle = 'Drone is idle, waiting for pickup'
    OutForDelivery = 'Drone on the way of package Delivery'
    AtDeliveryAddress = 'Drone reached at Delivery Address'
    DeliveredPackage = 'Drone has Delivered the package'
    OnTheWayToCC = 'Coming back to Command Center'
    BackToCC = 'Drone reached to Command Center ready for next delivery'


class Drone():
    
    # Members 
    _droneID = ''

    def __init__(self):
        pass
        
    #def spown(self, Job):

    def init(self):
        self.drone_id = uuid.uuid4().hex[:8]
        #self.drone_id = "Drone_"+str(self.drone_id)
        self.valocity = 0
        self.battery = randint(35, 100)
        self.is_armed = False
        self.mode = DroneState.Idle
        self.altitude = 0
        self.arm_and_ready()
        

    def __str__(self):
        
        return "'Mode' : {} ".format(repr(self.mode))

    def update_redis(self):
        
        time.sleep(randint(1,5))
        r.set(self.drone_id,self.mode.name)

    def get_drone_state(self):
        
        unpacked_object = pickle.loads(r.get(self.drone_id))
        self = unpacked_object
        return self

    def arm_and_ready(self):
        
        self.is_armed = True
        self.update_redis()
        print "Getting ready {}".format(self)

    def goto(self, job):
        #self = self.get_drone_state()
        if self.mode == DroneState.Idle:

            self.targetlat = job.base_lattitude
            self.targetlong = job.base_longitude
            self.valocity = job.valocity
            self.mode = DroneState.OutForDelivery
        
        elif self.mode == DroneState.DeliveredPackage:
            
            self.targetlat = job.lattitude
            self.targetlong = job.longitude
            self.valocity = job.valocity
            self.mode = DroneState.OnTheWayToCC
        
        #print "Current state {}".format(self)
        return self    
    
    def deliver_package_to_address(self, job):
        
        self = self.goto(job)
        self.update_redis()
        print "Out for delivery {}".format(self)

    def reached_delivery_address(self):
        
        #self = self.get_drone_state()
        self.mode = DroneState.AtDeliveryAddress
        self.altitude = 0
        self.valocity = 0
        self.is_armed = False
        self.update_redis()
        print "Reached delivery address {}".format(self)

    def delivered_package(self):
        
        #self = self.get_drone_state()
        self.mode = DroneState.DeliveredPackage
        #TODO : Log and update CC
        #self = self.goto(job)
        self.update_redis()
        print "Delivered package {}".format(self)
    
    def back_to_base(self,job):
        
        #self = self.get_drone_state()
        self.altitude = 0
        self.valocity = 0
        self.is_armed = False
        self.mode = DroneState.BackToCC

        self.update_redis()

        print "Back to Base {}".format(self)
    
    def back_to_idle_state(self):
        
        #self = self.get_drone_state()
        if self.mode == DroneState.BackToCC:
            self.mode = DroneState.Idle
        
        self.update_redis()
        print "Drone is Idle {}".format(self)



d = Drone()
d.init()
print d.drone_id

binding_key = d.drone_id

channel.queue_bind(exchange='task', queue=queue_name, routing_key=binding_key)


print(' [*] Waiting for task. To exit press CTRL+C')

def callback(ch, method, properties, body):
    
    print(' Delivery task recieved')
    job = Job()
    job = pickle.loads(body)
    #print job.longitude
    #print(" [x] %r" % job)

    d.arm_and_ready()

    d.deliver_package_to_address(job)

    d.reached_delivery_address()

    d.delivered_package()

    d.back_to_base(job)

    d.back_to_idle_state()

    # = d.get_drone_state()

    #print dd


channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()