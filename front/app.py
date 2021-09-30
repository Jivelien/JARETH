from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def hello_world():
    last_cigarette=requests.get("http://webservice:5000/get_last_cigarette").json()
    return last_cigarette

if __name__ == "__main__":
    app()