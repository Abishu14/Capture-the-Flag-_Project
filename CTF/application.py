import os

import datetime
from flask import Flask, render_template, redirect, jsonify, request, url_for, session
from flask_socketio import SocketIO, emit, send
from flask_session import Session
from channels import Channel

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
socketio = SocketIO(app)
Session(app)
channels = []


@app.route("/")
def index():
        return render_template("welcome.html")

'''
@app.route("/")
def index():
    try:
        return render_template("index.html", name=session["name"], lastChannel=session["lastChannel"], channels=channels)
    except KeyError:
        try:
            return render_template("index.html", name=session["name"], channels=channels)
        except KeyError:
            return render_template("index.html", channels=channels)
'''

@app.route("/sheepsProfile", methods=["POST"])
def profile():
        key = request.form.get("key")
        if (key) == 'abc':
            return render_template("sheepProfile.html")

@app.route("/viewas", methods=["POST"])
def viewas():
        key1 = request.form.get("key1")
        if (key1) == 'abc':
            return render_template("viewas.html")

@app.route("/name", methods=["POST"])
def name():
    name = request.form.get("name")
    if name is not '':
        session["name"] = name
        return jsonify({"success": True, "name": name})
    else:
        return jsonify({"success": False})

@app.route("/lastChannel", methods=["POST"])
def lastChannel():
    channel = request.form.get("lastChannel")
    session["lastChannel"] = channel
    return ''

@app.route("/channel", methods=["POST"])
def channel():
    channel = request.form.get('channel')
    for elem in channels:
        if channel in elem.name:
            return jsonify({"success": False})
    newChannel = Channel(channel)
    channels.append(newChannel)
    channelsFeed = []
    for object in channels:
        channelsFeed.append(object.__dict__)
    return jsonify({"success": True, "channel": channel, "channels": channelsFeed})

@socketio.on("sendMessage")
def chat(data):
    channel = data["channel"]
    message = data["message"]
    # Check all existing channels seeking for the same name
    for checkChannel in channels:
        # If exist then append the new message else emit a Not success message
        if checkChannel.name == channel:
            time = '{:%H:%M:%S}'.format(datetime.datetime.now())
            sender = session["name"]
            checkChannel.newMessage(message, sender, channel, time)

            last_message = checkChannel.messages[-1]
            emit("update", last_message, broadcast=True)
            return
    emit("update", 'Not success', broadcast=True)

@socketio.on("update")
def conect(data):
    channel = data["channel"]
    #Checking for an existing channel with that same name
    for checkChannel in channels:
        # If exist, charge all old messages stored there and emit
        if checkChannel.name == channel:
            oldMessages = checkChannel.messages
            name = session["name"]
            emit("updateChat", (oldMessages, name), broadcast=True)
            return
    # Else, emit a notFound message
    emit("updateChat", 'notFound', broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
