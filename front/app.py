from flask import Flask, jsonify, request, redirect, render_template, url_for, flash
from datetime import datetime
from dateutil.parser import parse
import requests

app = Flask(__name__)
app.config.from_object("config.Config")
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

from wtforms import Form, BooleanField, StringField, PasswordField, validators

class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=4, max=25),
        validators.InputRequired()
        ])
    email = StringField('Email Address', [
        validators.Email(),
        validators.Length(min=6, max=35),
        validators.InputRequired()
        ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login")
def login():
    return render_template("index.html")

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