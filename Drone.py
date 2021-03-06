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

"drone_id": {
        "ID": "drone_id",
        "state": DroneState,
        "type": DronType,
        "capacity": DroneCapacity,
    }
'''

drone_redis = {}

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

    def init(self):
        self.drone_id = uuid.uuid4().hex[:8]
        self.valocity = 0
        self.battery = randint(35, 100)
        self.is_armed = False
        self.mode = DroneState.Idle
        self.altitude = 0
        self.drone_redis = {
            str(self.drone_id):{ 
                "state" : self.mode.name,
            }
        }
        self.arm_and_ready()
        

    def __str__(self):
        
        return "'Mode' : {} ".format(repr(self.mode))

    def update_redis(self):
        
        r.set("DroneID_"+self.drone_id,self.drone_redis)

    def arm_and_ready(self):
        
        self.is_armed = True
        self.update_redis()
        print "Drone is Idle {}".format(self)

    def goto(self, job):
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
        time.sleep(randint(1,5))
        return self    
    
    def deliver_package_to_address(self, job):
        
        self = self.goto(job)
        self.update_redis()
        time.sleep(randint(1,5))
        print "Out for delivery {}".format(self)

    def reached_delivery_address(self):
        
        self.mode = DroneState.AtDeliveryAddress
        self.altitude = 0
        self.valocity = 0
        self.is_armed = False
        self.update_redis()
        time.sleep(randint(1,5))
        print "Reached delivery address {}".format(self)

    def delivered_package(self):
        
        self.mode = DroneState.DeliveredPackage
        self.update_redis()
        time.sleep(randint(1,5))
        print "Delivered package {}".format(self)
    
    def back_to_base(self,job):
        
        self.altitude = 0
        self.valocity = 0
        self.is_armed = False
        self.mode = DroneState.BackToCC

        self.update_redis()
        time.sleep(randint(1,5))
        print "Back to Base {}".format(self)
    
    def back_to_idle_state(self):
        
        if self.mode == DroneState.BackToCC:
            self.mode = DroneState.Idle
        
        self.update_redis()
        time.sleep(randint(1,5))
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

    d.arm_and_ready()

    d.deliver_package_to_address(job)

    d.reached_delivery_address()

    d.delivered_package()

    d.back_to_base(job)

    d.back_to_idle_state()


channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()