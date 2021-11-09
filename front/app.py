from flask import Flask, make_response, jsonify, request, redirect, render_template, url_for, flash
from datetime import datetime
from dateutil.parser import parse
import requests

app = Flask(__name__)
app.config.from_object("config.Config")

from wtforms import Form, BooleanField, StringField, PasswordField, validators

#WEBSERVICE_URL = "http://webservice:5000"
WEBSERVICE_URL = "http://localhost:42001"
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

def ws_call_login(mail, password):
    user = {
        "mail": mail,
        "password": password
    }
    call = requests.post(f"{WEBSERVICE_URL}/login", json=user)
    return call

@app.route("/")
def main():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        call = ws_call_create_user(form.username.data, form.mail.data, form.password.data)
        if call.status_code == 201:
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
            
        else:
            flash(call.json().get('message', 'Registration failed: Something append ¯\_(ツ)_/¯'), 'danger')

    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        call = ws_call_login(form.mail.data, form.password.data)
        if call.status_code == 200:
            token = call.json().get('token')
            response = make_response(render_template('index.html'))
            response.set_cookie('token', token)
            flash("Welcome to the jungle", "success")
            return response
        else:
            if call.json():
                message = call.json().get('message', 'Login failed: Something append ¯\_(ツ)_/¯')
            else:
                message = 'Login failed: Something append ¯\_(ツ)_/¯'  
            flash(message, 'danger')
    
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    return render_template("index.html")


@app.route("/record_cigarette")
def record_cigarette():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()