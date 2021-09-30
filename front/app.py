from flask import Flask, jsonify, request, redirect
from flask import render_template
from flask_wtf import FlaskForm
from flask import render_template
from flask_wtf import FlaskForm
from datetime import date
from wtforms.fields.html5 import DateField, TimeField, SearchField
from wtforms.fields.html5 import TimeField
import requests

app = Flask(__name__)
app.config.from_object("config.Config")

def get_last_cigarette():
    last_cigarette=requests.get("http://webservice:5000/get_last_cigarette").json()
    return last_cigarette

class TestForm(FlaskForm):
    password = SearchField('Password:')
    eventdate = DateField('Date:')
    eventtime = TimeField('time:')


@app.route("/")
def main():
    forms = TestForm()
    last_cigarette = get_last_cigarette()

    return render_template('test.html',form=forms, last_cigarette=last_cigarette)

@app.route("/add_event", methods=['POST'])
def add_event():
    password = request.form.get("password") 
    eventdate = request.form.get("eventdate")
    eventtime = request.form.get("eventtime")

    event = {'password' : password, 'eventdate' : eventdate, 'eventtime' : eventtime}

    add_cigarette = requests.post("http://webservice:5000/add_event", data=event)

    return redirect('/')    



if __name__ == "__main__":
    app()