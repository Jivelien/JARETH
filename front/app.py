from flask import Flask, jsonify, request, redirect, render_template
from datetime import datetime
from dateutil.parser import parse
import requests

app = Flask(__name__)
app.config.from_object("config.Config")

__SECONDS_PER_WEEK__   = 7*60*60*24
__SECONDS_PER_DAY__    = 60*60*24
__SECONDS_PER_HOUR__   = 60*60
__SECONDS_PER_MINUTE__ = 60

def get_last_cigarette():
    last_cigarette=requests.get("http://webservice:5000/get_last_cigarette").json()
    return last_cigarette

def duration_to_string(duration):
    duration = int(duration)

    if duration // __SECONDS_PER_MINUTE__  == 0:
        return "just now"

    absolute_duration = abs(duration)

    days = absolute_duration // __SECONDS_PER_DAY__
    seconds_left = absolute_duration - days * __SECONDS_PER_DAY__

    hours = seconds_left //60//60
    seconds_left = seconds_left - hours * __SECONDS_PER_HOUR__

    minuts = seconds_left //60
    seconds = seconds_left - minuts * __SECONDS_PER_MINUTE__

    result_part = []
    if days > 1:
        result_part.append(f"{days} days")
    elif days > 0:
        result_part.append(f"{days} day")
    if hours > 1:
        result_part.append(f"{hours} hours")
    elif hours > 0:
        result_part.append(f"{hours} hour")
    if minuts > 1:
        result_part.append(f"{minuts} minuts")
    elif minuts > 0:
        result_part.append(f"{minuts} minut")

    if len(result_part) > 1:
        result_part.insert(-1, "and")

    if duration > 0:
        result_part.append("ago")
    else:
        result_part.insert(0,"in")

    return " ".join(result_part)

def get_advice(duration):
    if duration <= 1.5 * __SECONDS_PER_HOUR__:
        return "You should wait..."
    else:
        return ""

@app.route("/")
def main():
    last_cigarette_timestamp = get_last_cigarette().get("event")
    if last_cigarette_timestamp != '':
        delta = (datetime.now() - parse(last_cigarette_timestamp)).total_seconds()
        last_cigarette = duration_to_string(delta)
        advice = get_advice(delta)
    else:
        last_cigarette = ''
        advice = ''

    return render_template('test.html',
                            last_cigarette=last_cigarette,
                            advice= advice)

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