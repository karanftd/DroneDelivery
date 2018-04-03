from flask import Flask, jsonify
from flask import request
import uuid
import pickle
import redis

from Job import Job
from settings import *


app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)

'''
REST APIs
'''


'''
Image uploading REST POST API
It accepts Jobs from requests and start assigning the asynchronous jobs to Celery Workers. 
'''
@app.route('/v1/createJob', methods=['POST'])
def create_job():
    
    # check if request contain data
    if not request.json or not 'urls' in request.json:
        	return jsonify({"error":"param 'urls' not found in json or json has not been prepared properly"}), 400

    pass

    # create a Job
    deliveryJob = Job()

    deliveryJob.packageID = uuid.uuid4().hex[:8]
    if request.json["lat"]:
        deliveryJob.lattitude = request.json["lat"]
    else:
        return jsonify({"error":"param 'Latitude' not found in json or json has not been prepared properly"}), 501
    if request.json["lon"]:
        deliveryJob.longitude = request.json["lon"]
    else:
        return jsonify({"error":"param 'Longitude' not found in json or json has not been prepared properly"}), 501
    if request.json["valocity"]:
        deliveryJob.valocity = request.json["valocity"]
    else:
        return jsonify({"error":"param 'Longitude' not found in json or json has not been prepared properly"}), 501

    deliveryJob.base_lattitude = BASELAT
    deliveryJob.base_longitude = BASELON

    pickled_object = pickle.dumps(deliveryJob)

    r.set("JOB_"+deliveryJob.packageID, pickled_object)


    return jsonify({"message":"Job created successfully. JOB_ID : "+str(deliveryJob.packageID)}), 201


    











if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)