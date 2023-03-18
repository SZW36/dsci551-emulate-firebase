from flask import Flask
from flask_socketio import SocketIO
from flask_socketio import send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# sio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True, logger=True)
sio = SocketIO(app, cors_allowed_origins="*")

@app.route("/", methods = ['GET', 'POST'])
def hello_world():
    sio.send('my_event', 'zewei')
    return "abc"

@sio.on('my_event')
def handler():
    print('received my event')

# app.run()
sio.run(app, debug=True)

# socketio
# https://flask-socketio.readthedocs.io/en/latest/getting_started.html#rooms