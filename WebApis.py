from flask import Flask, jsonify
from flask import request

from Job import *


app = Flask(__name__)

'''
REST APIs
'''


'''
Image uploading REST POST API
It accepts URL list from requests and start assigning the asynchronous jobs to Celery Workers. 
'''
@app.route('/v1/createJob', methods=['POST'])
def create_job():
    
    # check if request contain data
    if not request.json or not 'urls' in request.json:
        	return jsonify({"error":"param 'urls' not found in json or json has not been prepared properly"}), 400

    pass















if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)