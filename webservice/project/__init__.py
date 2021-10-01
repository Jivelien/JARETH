from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    eventtime = db.Column(db.DateTime, unique=True, nullable=False)
    label = db.Column(db.String(26), default=True, nullable=False)

    def __init__(self, eventtime):
        self.label = "cigarette"
        self.eventtime = eventtime

@app.route("/get_last_cigarette", methods=['GET'])
def last_cigarette():
    # datetime.strptime("Thu, 30 Sep 2021 20:53:00 GMT", "%a, %d %b %Y %X GMT")
    last = Event.query.order_by(Event.eventtime.desc()).first()
    if last:
        return jsonify(event=last.eventtime)
    else:
        return jsonify(event='')

    

@app.route("/add_event", methods=['POST'])
def add_event():
    if request.form.get("password") != os.getenv('TMP_PASS'):
        return "Nope, motherfucker"

    eventdatetime = request.form.get("eventdatetime")

    event = Event(eventdatetime)

    db.session.add(event)
    db.session.commit()
    
    return jsonify(event=event.eventtime)