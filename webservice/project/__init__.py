from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask import render_template
from flask_wtf import FlaskForm
from datetime import date
from wtforms.fields.html5 import DateField, TimeField, SearchField
from wtforms.fields.html5 import TimeField

app = Flask(__name__, template_folder="/home/app/web/project")
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

class TestForm(FlaskForm):
    password = SearchField('Password:')
    eventdate = DateField('Date:')
    eventtime = TimeField('time:')

@app.route("/")
def hello_world():
    forms = TestForm()
    last_cigarette = Event.query.order_by(Event.eventtime.desc()).first().eventtime
    if forms.validate_on_submit():
        return 'From Date is : {} To Date is : {}'.format(forms.startdate.data, forms.todate.data)
    import os
    print(f"you are here : {os.getcwd()}")
    return render_template('test.html',form=forms, last_cigarette=last_cigarette)

@app.route("/get_last_cigarette", methods=['GET'])
def last_cigarette():
    return jsonify(event=Event.query.order_by(Event.eventtime.desc()).first().eventtime)
    

@app.route("/add_event", methods=['POST', 'GET'])
def add_event():
    if request.method == 'POST':
        if request.form.get("password") != os.getenv('TMP_PASS'):
            return "Nope, motherfucker"
        eventdate = request.form.get("eventdate")
        eventtime = request.form.get("eventtime")
        eventdatetime = eventdate+'T'+eventtime
    else:
        eventdatetime = request.args.get('t')

    event = Event(eventdatetime)
    db.session.add(event)
    db.session.commit()
    return jsonify(added=event.eventtime)