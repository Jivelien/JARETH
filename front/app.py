from flask import Flask, jsonify, request, redirect
from flask import render_template
from flask_wtf import FlaskForm
from flask import render_template
from flask_wtf import FlaskForm
from datetime import datetime
import requests

app = Flask(__name__)
app.config.from_object("config.Config")

def get_last_cigarette():
    last_cigarette=requests.get("http://webservice:5000/get_last_cigarette").json()
    return last_cigarette

@app.route("/")
def main():
    last_cigarette = get_last_cigarette().get("event")
    if last_cigarette :
        last_cigarette_timestamp = datetime.strptime(last_cigarette, "%a, %d %b %Y %X GMT")
    else:
        last_cigarette_timestamp = ''
        last_cig_from_now = ''

    return render_template('test.html',
                            last_cigarette=last_cigarette_timestamp)

@app.route("/add_event", methods=['POST'])
def add_event():
    password = request.form.get("password") 
    eventdate = request.form.get("eventdate")
    eventtime = request.form.get("eventtime")
    eventdatetime = eventdate+'T'+eventtime

    event = {'password' : password, 'eventdatetime' : eventdatetime}

    add_cigarette = requests.post("http://webservice:5000/add_event", data=event)

    return redirect('/')    



if __name__ == "__main__":
    app()