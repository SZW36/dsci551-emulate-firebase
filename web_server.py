from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_socketio import send, emit
import json
from pymongo import MongoClient
from uuid import uuid4
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# sio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True, logger=True)
CORS(app)
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

def find_for_deletion(path_list):
    """
    input: a list of path
    return: -1 if not found
            an index pointing to the key to be deleted

            e.g. 
                path_list = ["a", "b"]
                resp = {"a": {"b": 2}} 
                if we want to delete "b", it will return 0 because we need to delete "a" too

    """
    resp = main.find_one({"_id": "root"}, {"_id": 0})
    res = find_for_deletion_helper(path_list, 0, resp.get("root"))
    print(res)
    if res == False: # we haven't found it
        return -1
    return res[0]

def find_for_deletion_helper(path_list, idx, resp):
    # if not found
    if resp == None:
        return False
    
    # base case
    if idx == len(path_list):
        return [idx, True if type(resp) is not dict or len(resp) == 1 else False]
    
    result = find_for_deletion_helper(path_list, idx+1, resp.get(path_list[idx]))
    
    # if deeper recursion tells us its not found, return False
    if result == False:
        return False

    if len(resp) == 1 and result[1]:
        result[0] = idx
        return result
    
    result[1] = False
    return result


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

def process_resp(resp):
    """
    input: dictionary or anything that can be jsonified
    output: jsonified response with added header that allows all origin to receive response "Access-Control-Allow-Origin"
    """
    response = jsonify(resp)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

def checkIfComparable(resp, cur_type, orderBy = None):
    """
    input: 
        resp: dictionary
        cur_type: the type that we want it to be
        orderBy: string that represent key name of the attribute in the subdictionary
        
        If orderBy is supplied, we want to check subdictionary for the value in key-value pair
        If not, we want to just check each value in key-value pair of current dictionary
    
    output:
        whether the values are comparable
    """

    initialType = ""
    # check if value is primitive or if value type are consistent
    for key in resp:
        if orderBy:
            if initialType == "":
                initialType = type(resp[key][orderBy])
            if initialType != type(resp[key][orderBy]):
                return False
            if type(resp[key][orderBy]) is dict:
                return False
        else:
            if initialType == "":
                initialType = type(resp[key])
            if initialType != type(resp[key]):
                return False
            if type(resp[key]) is dict:
                return False
        if initialType != cur_type:
            return False

    return True

def convert(s):
    """
    input: string
    output: convert into either int or string if possible. If not, return the original string
    """
    if not s:
        return s
    
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

def reinsert_root_elem(input = {}):
    # delete everything in root
    main.delete_many({})
    # if data_type is dict:
    data = {"root" : input}
    data["_id"] = "root"
    main.insert_one(data)

@app.route('/', defaults={'myPath': ''}, methods=['GET'])
@app.route('/<path:myPath>', methods=['GET'])
def catch_all_get(myPath):

    path_list = process_path(myPath)
    resp = find(path_list)
    args = request.args.to_dict()
    
    if len(args) == 0:
        return process_resp(resp)

    # remove single quotes or double quotes
    for key in args:
        if type(args[key]) is str:
            args[key] = args[key].strip("\'\"")

    orderBy = args.get("orderBy")
    limitToFirst = convert(args.get("limitToFirst"))
    limitToLast = convert(args.get("limitToLast"))
    equalTo = convert(args.get("equalTo"))
    startAt = convert(args.get("startAt"))
    endAt = convert(args.get("endAt"))

    # convert them so that the logic works for error checking
    limitToFirst = -1 if limitToFirst == 0 else limitToFirst
    limitToLast = -1 if limitToLast == 0 else limitToLast

    ### Error checking

    # 1. limitToFirst and limitToLast: only one of it can occur
    if limitToFirst and limitToLast:
        return "error: only one of limitToFirst and limitToLast can occur"
    # 2. limitToFirst and limitToLast cannot be less than 1
    if limitToFirst or limitToLast:
        if (limitToFirst != None and type(limitToFirst) is not int) or (limitToLast != None and type(limitToLast) is not int):
            return "error: limitToFirst or limitToLast must be integer"
        if (limitToFirst != None and limitToFirst < 1) or (limitToLast != None and limitToLast < 1):
            return "error: limitToFirst or limitToLast must be positive"
    # 3. equalTo cannot be specified with startAt or endAt
    if equalTo and (startAt or endAt):
        return "error: equalTo cannot be specified in addition to startAt or endAt"
    # 4. startAt > endAt or startAt cannot compare with endAt
    if startAt and endAt:
        if type(startAt) != type(endAt):
            return {}
        elif startAt > endAt:
            return {}
        elif startAt == endAt: # this reduces to equalTo problem
            equalTo = startAt
    # 5. every argument should have the same type:
    cur_type = ""
    my_list = [equalTo, startAt, endAt]
    for item in my_list:
        if item is None:
            continue
        if cur_type == "":
            cur_type = type(item)
        if cur_type != type(item):
            return "error: argument have different types"


    key_list = resp.keys()
    sorted_key_list = []
    output = []
    if orderBy == "$key":
        # key has to be string, so we convert equalTo into string
        if equalTo:
            equalTo = str(equalTo)
            val = resp.get(equalTo)
            return process_resp({equalTo: val} if val != None else None)
        else:
            # convert into string for comparison
            startAt = str(startAt) if startAt else None
            endAt = str(endAt) if endAt else None

            # sort it and then use two pointers
            sorted_key_list = sorted(key_list)
            left = 0
            right = len(sorted_key_list)-1
            if startAt:
                while left <= right and sorted_key_list[left] < startAt:
                    left += 1
            if endAt:
                while left <= right and sorted_key_list[right] > endAt:
                    right -= 1
            if limitToFirst:
                end = left + limitToFirst - 1
                right = end if end <= right else right
            if limitToLast:
                start = right - limitToLast + 1
                left = start if start >= left else left

            while left <= right:
                output.append(sorted_key_list[left])
                left += 1


    elif orderBy == "$value":

        # # check if single value and value are of same type
        # # if so, sort it by that value
        # # if not, return the original list without doing anything

        # comparable = checkIfComparable(resp, cur_type)
        # if not comparable:
        #     return process_resp(resp)
        
        key_list = []
        for key in resp:
            if type(resp[key]) == type(equalTo) or type(resp[key]) == type(startAt) or type(resp[key]) == type(endAt):
                key_list.append(key)
        
        sorted_key_list = sorted(key_list, key=lambda list_item: (resp[list_item]))
        
        # use two pointers to locate where to start getting output
        left = 0
        right = len(sorted_key_list)-1
        if equalTo:
            while left <= right and resp.get(sorted_key_list[left]) != equalTo:
                left += 1
            while left <= right and resp.get(sorted_key_list[right]) != equalTo:
                right -= 1
        if startAt:
            while left <= right and resp.get(sorted_key_list[left]) < startAt:
                left += 1
        if endAt:
            while left <= right and resp.get(sorted_key_list[right]) > endAt:
                right -= 1
        if limitToFirst:
            end = left + limitToFirst - 1
            right = end if end <= right else right
        if limitToLast:
            start = right - limitToLast + 1
            left = start if start >= left else left
        
        while left <= right:
            output.append(sorted_key_list[left])
            left += 1

    else:

        # comparable = checkIfComparable(resp, cur_type, orderBy)
        # if not comparable:
        #     return process_resp(resp)
        
        key_list = []
        for key in resp:
            cur_item = resp[key]
            if type(cur_item) is not dict:
                continue
            for key2 in cur_item:
                if  key2 == orderBy:
                    if (equalTo or startAt or endAt):
                        if (type(resp[key][key2]) == type(equalTo) or \
                            type(resp[key][key2]) == type(startAt) or \
                            type(resp[key][key2]) == type(endAt)):
                            key_list.append(key)
                    else:
                        key_list.append(key)
        
        sorted_key_list = sorted(key_list, key=lambda list_item: (resp[list_item][orderBy]))

        # use two pointers to locate where to start getting output
        left = 0
        right = len(sorted_key_list)-1
        print("right = " + str(right))
        if equalTo:
            while left <= right and resp.get(sorted_key_list[left]).get(orderBy) != equalTo:
                left += 1
            while left <= right and resp.get(sorted_key_list[right]).get(orderBy) != equalTo:
                right -= 1
        if startAt:
            while left <= right and resp.get(sorted_key_list[left]).get(orderBy) < startAt:
                left += 1
        if endAt:
            while left <= right and resp.get(sorted_key_list[right]).get(orderBy) > endAt:
                right -= 1
        if limitToFirst:
            end = left + limitToFirst - 1
            right = end if end <= right else right
        if limitToLast:
            start = right - limitToLast + 1
            left = start if start >= left else left
        
        while left <= right:
            output.append(sorted_key_list[left])
            left += 1
    
    response = {}
    for key in output:
        response[key] = resp[key]

    return process_resp(response)


### PUT requests will delete old data on current level and insert new data
@app.route('/', defaults={'myPath': ''}, methods=['PUT'])
@app.route('/<path:myPath>', methods=['PUT'])
def catch_all_put(myPath):
    if main.find_one({"_id": "root"}) == None or \
       main.find_one({"_id": "root"}).get("root") == None:
        reinsert_root_elem()

    path_list = process_path(myPath)
    data = json.loads(request.get_data().decode('utf-8'))
    data_type = type(data)

    first_item = path_list[0]  

    if first_item == "":
        reinsert_root_elem(data)
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

    if main.find_one({"_id": "root"}) == None or \
       main.find_one({"_id": "root"}).get("root") == None:
        reinsert_root_elem()

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

### POST is similar to PATCH except we add random string as key for data
@app.route('/', defaults={'myPath': ''}, methods=['POST'])
@app.route('/<path:myPath>', methods=['POST'])
def catch_all_post(myPath):

    if main.find_one({"_id": "root"}) == None or \
       main.find_one({"_id": "root"}).get("root") == None:
        reinsert_root_elem()

    path_list = process_path(myPath)
    new_data = json.loads(request.get_data().decode('utf-8'))

    print("new data = " + str(new_data))

    data = find(path_list)

    print("data is " + str(data))

    cur_uuid = str(uuid4())

    if data == -1: # no root
        data = {"root" : {str(cur_uuid): new_data}}
        data["_id"] = "root"
        main.insert_one(data)
        return "success"
    
    if not data: # data does not exist
        data = {}

    data[cur_uuid] = new_data

    # send message to front end
    # data_to_send = {cur_uuid: new_data}
    sio.send(new_data, "json")

    query_path = ".".join(path_list)
    if query_path == "":
        query_path = "root"
    else:
        query_path = "root." + query_path
    main.update_one({"_id": "root"}, {"$set": {query_path: data}}, upsert = True)


    return "success"

### DELETE will delete data
@app.route('/', defaults={'myPath': ''}, methods=['DELETE'])
@app.route('/<path:myPath>', methods=['DELETE'])
def catch_all_delete(myPath):

    if main.find_one({"_id": "root"}) == None or \
       main.find_one({"_id": "root"}).get("root") == None:
        reinsert_root_elem()

    path_list = process_path(myPath)

    if path_list[0] == "":
        reinsert_root_elem()
        return "successfully deleted everything"

    res = find_for_deletion(path_list)

    if res == -1:
        return "path not found"
    
    # if we want to delete everything
    if path_list[0] == "":
        reinsert_root_elem()
        return "successfully deleted everything"

    query_path = ""
    for i in range(0, res):
        query_path += "." + path_list[i]
    query_path = "root" + query_path
    main.update_one({"_id": "root"}, {"$unset": {query_path: None}}, upsert = True)

    # if we have deleted root element, add it back
    if main.find_one({"_id": "root"}).get("root") == None:
        reinsert_root_elem()


    # # send message to front end
    # sio.send(resp, json=True)

    return "success"


### For backend to accept websocket messages from frontend
# @sio.on('my_event')
# def handler():
#     print('received my event')

@sio.on("connect")
def handle_connect():
    print("\nclient connected!")
    print("sid = " + str(request.sid) + "\n")
    sio.send({"your_sid": request.sid}, "json", room=request.sid)

sio.run(app, debug=True)




### Documentations

# 1. socketio
# https://flask-socketio.readthedocs.io/en/latest/getting_started.html#rooms

# 2. PyMongo
# https://www.digitalocean.com/community/tutorials/how-to-use-mongodb-in-a-flask-application

# 3. install mongodb on mac
# https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/