from flask import Flask, make_response, jsonify, request, redirect, render_template, url_for, flash
from datetime import datetime
from dateutil.parser import parse
import requests
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.fields.html5 import DateField, TimeField


app = Flask(__name__)
app.config.from_object("config.Config")

WEBSERVICE_URL = "http://webservice:5000"
__SECONDS_PER_WEEK__   = 7*60*60*24
__SECONDS_PER_DAY__    = 60*60*24
__SECONDS_PER_HOUR__   = 60*60
__SECONDS_PER_MINUTE__ = 60

class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=4, max=25),
        validators.InputRequired()
        ])
    mail = StringField('Email Address', [
        validators.Email(),
        validators.Length(min=6, max=35),
        validators.InputRequired()
        ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    mail = StringField('Email Address', [
        validators.InputRequired()
        ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])

class RecordCigaretteForm(Form):
    date = DateField('Date', [
        validators.InputRequired()
        ])
    time = TimeField('Time', [
        validators.DataRequired()
    ])

def ws_call_create_user(username, mail, password):
    data = {
        "username": username,
        "mail": mail,
        "password": password
    }
    call = requests.post(f"{WEBSERVICE_URL}/user", json=data)
    return call


def ws_call_login(mail, password):
    user = {
        "mail": mail,
        "password": password
    }
    call = requests.post(f"{WEBSERVICE_URL}/login", json=user)
    return call

def ws_call_get_user(token, user_public_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    call = requests.get(f"{WEBSERVICE_URL}/user/{user_public_id}", headers=headers)
    return call

def ws_call_get_current_user(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    call = requests.get(f"{WEBSERVICE_URL}/whoami", headers=headers)
    return call

def ws_call_get_last_cigarettes(token, limit):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    call = requests.get(f"{WEBSERVICE_URL}/cigarettes?limit={limit}", headers=headers)
    return call

def ws_call_create_cigarette(token, event_time):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    cigarette = {
        "event_time": event_time
    }
    call = requests.post(f"{WEBSERVICE_URL}/cigarette", json=cigarette, headers=headers)
    return call

def get_last_cigarettes(cookie,limit):
    token = cookie.get('token')
    call = ws_call_get_last_cigarettes(token, limit)
    if call.status_code == 200:
        return call.json()
    else:
        return None

def create_cigarette(cookie, event_time):
    token = cookie.get('token')
    return ws_call_get_last_cigarettes(token, event_time)


def get_logged_in_user_if_exist(cookie):
    token = cookie.get('token')
    return get_logged_in_user_if_exist_with_token(token)

def get_logged_in_user_if_exist_with_token(token):
    if token:
        call = ws_call_get_current_user(token)
        if call.status_code == 200:
            return call.json()
        else:
            return None

@app.route("/")
def main():
    current_user = get_logged_in_user_if_exist(request.cookies)
    if current_user:
        return redirect(url_for('dashboard'))
    return render_template("index.html", current_user = current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    current_user = get_logged_in_user_if_exist(request.cookies)
    if current_user:
        return redirect(url_for("main"))

    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        call = ws_call_create_user(form.username.data, form.mail.data, form.password.data)
        if call.status_code == 201:
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
            
        else:
            flash(call.json().get('message', 'Registration failed: Something append ¯\_(ツ)_/¯'), 'danger')

    return render_template('register.html', form=form, current_user = current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    current_user = get_logged_in_user_if_exist(request.cookies)
    if current_user:
        return redirect(url_for("dashboard"))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        call = ws_call_login(form.mail.data, form.password.data)
        if call.status_code == 200:
            token = call.json().get('token')
            current_user = get_logged_in_user_if_exist_with_token(token)
            flash("Welcome to the jungle", "success")
            response = make_response(render_template('index.html', current_user = current_user))
            response.set_cookie('token', token)
            return response
        else:
            if call.json():
                message = call.json().get('message', 'Login failed: Something append ¯\_(ツ)_/¯')
            else:
                message = 'Login failed: Something append ¯\_(ツ)_/¯'  
            flash(message, 'danger')
    
    return render_template('login.html', form=form, current_user = current_user)

@app.route("/logout")
def logout():
    current_user = get_logged_in_user_if_exist(request.cookies)
    if not current_user:
        return redirect(url_for("login"))

    flash("Thanks bye bitch", 'success')
    response = make_response(render_template('index.html'))
    response.delete_cookie('token')
    return response


@app.route("/record_cigarette", methods=["GET", "POST"])
def record_cigarette():
    current_user = get_logged_in_user_if_exist(request.cookies)
    if not current_user:
        return redirect(url_for("login"))

    form = RecordCigaretteForm(request.form)

    if request.method == 'POST' and form.validate():
        call = ws_call_create_cigarette(request.cookies.get('token'), form.date.data.strftime("%Y-%m-%d") + " " + form.time.data.strftime("%H:%M:%S"))
        if call.status_code == 201:
            flash('Cigarette recorded', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(call.json().get('message', 'Something append ¯\_(ツ)_/¯'), 'danger')

    last_cigarette_timestamp = get_last_cigarettes(request.cookies, 1)
    if last_cigarette_timestamp:
        delta = (datetime.now() - parse(last_cigarette_timestamp[0].get('event_time'))).total_seconds()
        last_cigarette = duration_to_string(delta)
        advice = get_advice(delta)
    else:
        last_cigarette = ''
        advice = ''

    return render_template("record_cigarette.html", 
                            current_user=current_user,
                            form=form,
                            last_cigarette=last_cigarette,
                            advice=advice)


@app.route("/dashboard")
def dashboard():
    current_user = get_logged_in_user_if_exist(request.cookies)
    if not current_user:
        return redirect(url_for("login"))
    
    last_cigarettes = get_last_cigarettes(request.cookies, 10)

    return render_template("dashboard.html", current_user = current_user, last_cigarettes = last_cigarettes)

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

if __name__ == "__main__":
    app.run()