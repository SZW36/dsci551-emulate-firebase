from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_socketio import send, emit
import json
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# sio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True, logger=True)
sio = SocketIO(app, cors_allowed_origins="*")

# for mongodb
client = MongoClient('localhost', 27017)
db = client.dsci551_db
main = db.main

# @app.route("/", methods = ['GET', 'POST'])
# def hello_world():
#     sio.send('xyz', 'zewei')
#     response = jsonify("abc")
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response

def process_path(myPath):
    """
    input: a string that represent a path, with .json as the end
           e.g. "a/b/c.json"
    output: a list that represent a path
           e.g. ["a", "b", "c"]
    """

    # remove the .json from the end
    myPath = myPath[:len(myPath)-5]

    path_list = myPath.split("/")

    return path_list

def find(path_list):
    """
    input: a list of string that represents path
    output: The outcome that we want to find. 
            If it does not exist, return -1 for no root, None for does not exist
    """

    resp = main.find_one({"_id": "root"}, {"_id": 0})
    if not resp:
        return -1
    resp = resp.get("root")

    for i in range(0, len(path_list)):
        target = path_list[i]
        if target == "":
            continue
        if not resp:
            break
        resp = resp.get(target)
    
    return resp

def insert(key, value):
    """
    insert an entry into mongodb

    input: can be a dict or list or 

    """
    data = {}
    if type(value) is dict: # multilevel
        data["_id"] = key
        data[key] = value
    else:
        data = {key: value} # make it into a dict
        data["_id"] = key
    main.insert_one(data)

@app.route('/', defaults={'myPath': ''}, methods=['GET'])
@app.route('/<path:myPath>', methods=['GET'])
def catch_all_get(myPath):

    path_list = process_path(myPath)

    resp = find(path_list)

    

    # send response back
    response = jsonify(resp)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

### PUT requests will delete old data on current level and insert new data
@app.route('/', defaults={'myPath': ''}, methods=['PUT'])
@app.route('/<path:myPath>', methods=['PUT'])
def catch_all_put(myPath):

    path_list = process_path(myPath)
    data = json.loads(request.get_data().decode('utf-8'))
    data_type = type(data)

    first_item = path_list[0]  

    if first_item == "":
        # delete everything in root
        main.delete_many({})
        # if data_type is dict:
        data = {"root" : data}
        data["_id"] = "root"
        main.insert_one(data)
    else:
        query_path = ".".join(path_list)
        query_path = "root." + query_path
        main.update_one({"_id": "root"}, {"$set": {query_path: data}}, upsert = True)

    # # send message to front end
    # sio.send(myPath, json=True)

    return "success"


### PATCH will: if key exists, update. else insert
@app.route('/', defaults={'myPath': ''}, methods=['PATCH'])
@app.route('/<path:myPath>', methods=['PATCH'])
def catch_all_patch(myPath):

    path_list = process_path(myPath)
    new_data = json.loads(request.get_data().decode('utf-8'))

    print("new data = " + str(new_data))

    data = find(path_list)

    print("data is " + str(data))

    if data == -1: # no root
        data = {"root" : new_data}
        data["_id"] = "root"
        main.insert_one(data)
        return "success"
    
    if not data: # data does not exist
        data = {}

    for key in new_data:
        data[key] = new_data[key]

    query_path = ".".join(path_list)
    if query_path == "":
        query_path = "root"
    else:
        query_path = "root." + query_path
    main.update_one({"_id": "root"}, {"$set": {query_path: data}}, upsert = True)

    return "success"

### POST will: if key exists, update. else insert
@app.route('/', defaults={'myPath': ''}, methods=['POST'])
@app.route('/<path:myPath>', methods=['POST'])
def catch_all_post(myPath):
    print("myPath = " + myPath)
    resp = {"url": request.url_root,
        "path": request.path,
        # "full path": request.full_path,
        "data": request.get_data().decode('utf-8')}

    print(resp)
    response = jsonify(resp)
    response.headers.add('Access-Control-Allow-Origin', '*')

    # send message to front end
    sio.send(resp, json=True)

    return response

### DELETE will delete data
@app.route('/', defaults={'myPath': ''}, methods=['DELETE'])
@app.route('/<path:myPath>', methods=['DELETE'])
def catch_all_delete(myPath):

    path_list = process_path(myPath)

    query_path = ".".join(path_list)
    main.update_one({"_id": "root"}, {"$unset": {query_path: data}}, upsert = True)

    print(resp)
    response = jsonify(resp)
    response.headers.add('Access-Control-Allow-Origin', '*')

    # send message to front end
    sio.send(resp, json=True)

    return response

### For backend to accept websocket messages from frontend
# @sio.on('my_event')
# def handler():
#     print('received my event')

sio.run(app, debug=True)




### Documentations

# 1. socketio
# https://flask-socketio.readthedocs.io/en/latest/getting_started.html#rooms

# 2. PyMongo
# https://www.digitalocean.com/community/tutorials/how-to-use-mongodb-in-a-flask-application

# 3. install mongodb on mac
# https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/