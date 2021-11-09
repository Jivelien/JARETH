from flask import Flask, make_response, jsonify, request, redirect, render_template, url_for, flash
from datetime import datetime
from dateutil.parser import parse
import requests
from wtforms import Form, BooleanField, StringField, PasswordField, validators


app = Flask(__name__)
app.config.from_object("config.Config")

WEBSERVICE_URL = "http://webservice:5000"


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

def get_logged_in_user_if_exist(cookie):
    token = cookie.get('token')
    if token:
        call = ws_call_get_current_user(token)
        if call.status_code == 200:
            return call.json()
        else:
            return None

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
        return redirect(url_for("main"))

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


@app.route("/record_cigarette")
def record_cigarette():
    current_user = get_logged_in_user_if_exist(request.cookies)
    if not current_user:
        return redirect(url_for("login"))

    return render_template("index.html", current_user = current_user)


@app.route("/dashboard")
def dashboard():
    current_user = get_logged_in_user_if_exist(request.cookies)
    if not current_user:
        return redirect(url_for("login"))
        
    return render_template("index.html", current_user = current_user)


if __name__ == "__main__":
    app.run()