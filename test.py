from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_socketio import send, emit
import json
from pymongo import MongoClient
from uuid import uuid4
# from .extensions import socketio
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# cors = CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)
sio = SocketIO(app, cors_allowed_origins="*")

@app.route("/", methods = ['GET', 'POST', 'PUT'])
# @CORS(app)
def hello_world():
    sid = request.json["sid"]
    data = {"abc": 2, "def": 56}
    sio.send(data, "json", room = sid)
    # sio.emit('message', "jkl")
    response = jsonify("abc")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@sio.on("connect")
def handle_connect():
    print(request.sid)
    print("client connected!")
    # sio.send(request.sid, "xyz")
    sio.send({"your_sid": request.sid}, "json", room=request.sid)

sio.run(app, debug=True)
