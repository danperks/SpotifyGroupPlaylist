import requests
import os
from flask import Flask
from flask import render_template
from flask import redirect
from flask import send_file
from flask import request
from flask import make_response
from flask import send_from_directory
from flask import url_for
from flask import jsonify

from spotifyMethods import ApplicationVerification, GetAuthoristaionToken

app = Flask(__name__)
app.static_folder = "static"
app.template_folder = "templates"


@app.route("/SpotifyCallback")

def CallBack():
    userReturnedCode = request.args["code"]
    if userReturnedCode == "access_denied":
        print("ERROR : User Denies access ")
        return render_template("index.html")
    AuthToken = GetAuthoristaionToken(userReturnedCode)
    
    return "0"

@app.route("/")#index
def indexStart():
    return render_template("index.html")

@app.route("/Login/Spotify")
def SpotifyLogIn():
    print("connected")
    return redirect(ApplicationVerification())
    
@app.route("/Login/Apple")
def AppleLogIn():
    return "0";
@app.route("/Login/Google")
def GoogleLogin():
    return "0";

if __name__ == "__main__":
    debug = True
    port = int(os.environ.get("PORT",5000))
    app.run(host= '0.0.0.0',port=port,debug=debug)