import os, sys, json, datetime, copy, uuid, requests
import logging
from flask import Flask, request, jsonify 
from flask_cors import CORS
from pymongo import MongoClient
from io import BytesIO
import numpy as np
from maps import detour

application = Flask(__name__)
CORS(application)

logger = logging.getLogger("hack_api")

mongo_url = os.environ['MONGO_URL']
cli = MongoClient(mongo_url)
db = cli.test
db.test.insert_one({"test":"test"})

@application.route('/health')
def health_check():
    logger.debug('<health-check>')
    return "OK"

@application.route('/find_stops', methods=['POST'])
def api_new_trip():
    data = request.get_json(force=True)
    src = data.get('src')
    dst = data.get('dst')
    mid = data.get('mid')
    detour_data = detour(src, dst, mid)
    ret = detour_data
    return jsonify(ret)

@application.route('/place_order', methods=['POST'])
def api_place_order():
    ret = {}
    return jsonify(ret)

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8888)
