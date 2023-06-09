## To install all dependencies of web_server:

```
    pip install -r requirements.txt
```

## To get all dependencies of web_server:

```
    pip freeze > requirements.txt
```

## To start or stop mongodb on macOS

```
    brew services start mongodb-community@6.0
```

```
    brew services stop mongodb-community@6.0
```

## Query mongodb on macOS in terminal

```
    mongosh
```

## To run and query backend:

1. Run backend:

```
    python3 web_server.py
```

2. Send query to "localhost:5000". For example:

```
    curl -X GET 'localhost:5000/.json'
    curl -X PUT 'localhost:5000/101.json' -d '{"name": "Daniel"}'
```

## To run the frontend:

1. Make sure to install all packages

```
    npm install
```

2. run frontend

```
    npm start
```

### Documentations & Useful Websites

1. socketio  
   https://flask-socketio.readthedocs.io/en/latest/getting_started.html#rooms

2. PyMongo  
   https://pymongo.readthedocs.io/en/stable/tutorial.html  
   https://www.digitalocean.com/community/tutorials/how-to-use-mongodb-in-a-flask-application

3. install mongodb on mac  
   https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/
