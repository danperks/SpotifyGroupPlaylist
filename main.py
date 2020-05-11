import requests
import os
import psycopg2
from flask import Flask
from flask import render_template
from flask import redirect
from flask import send_file
from flask import request
from flask import make_response
from flask import send_from_directory
from flask import url_for
from flask import jsonify
from flask import escape

from spotifyMethods import ApplicationVerification, GetAuthoristaionToken,RefreshAccessToken,GetUsersLikedSongs

app = Flask(__name__)
app.static_folder = "static"
app.template_folder = "templates"
conn = psycopg2.connect(host = "***REMOVED***",database = "***REMOVED***",user = "***REMOVED***",password= "***REMOVED***")
SQLcursor = conn.cursor()
## go environment varible for user and password , will do for now
#Database
@app.route("/SpotifyCallback")

def SpotifyCallBack():
    userReturnedCode = request.args["code"]
    if userReturnedCode == "access_denied":
        print("ERROR : User Denies access ")
        return render_template("index.html")
    AuthToken = GetAuthoristaionToken(str(userReturnedCode))
    RefreshToken = AuthToken["refresh_token"]#tokens expire after one hour
    resp = make_response(render_template("GroupCodeEntry.html"))
    resp.set_cookie("RefreshToken",RefreshToken)
    #print("Access Token " + str(AuthToken["access_token"]))
    print("Refreshed Token " + str(RefreshAccessToken(RefreshToken)))
    #return GetUsersLikedSongs(RefreshAccessToken(RefreshToken)["access_token"])
    return resp
    #return GetUsersLikedSongs("BQBt2vXxSs9m17_2vz9EUlW4f_F27AUl9d34b-_VdO8DM4i4OFZ380JVZj80-bDPi4lweS-_GND8tf48EYfN4QPAI-QdwVWjcVSSlus4NXXuZUrHkhwIkBKGIAzVtUHuhPrizm7acRlBi0bnPwNYcPg_aF2BYmv48P0Lax5eFeRgWiI4taLvMrONC2iVGEWAfGKZFTvBP15zw3UdGc6yKAMhuj4V2p35scV2yPuxXw")
@app.route("/")#index
def indexStart():
    if "RefreshToken" in request.cookies:#just check for the token
        PreviousAuthorisation = request.cookies["RefreshToken"]
    #check cookie to see if spotify authorised
    #if spotify authorised, then allow user to enter group id
    #if not, authoirse, then redirect to group id - set refresh token as the cookie
    
    return render_template("index.html")
@app.route("/test")
def test():
    return GetUsersLikedSongs("BQCUaytGjGYYwSGIEIbMK53tLdTBJMtO-wM_1aoPbrMH887eMw9luaZ1RqyZEjEoOF6Mb45nKLoQqB4gcB1N3LljW92nSwMTKe7emv9j3LhNY6saiV73VkndUdvPd9YwHOw6U3cwnfKdVEKLFtBnHMY2rgNXY1l36mT5OSPKakHmHtDzgOiX164LXuIbIV6-Bn7sv4NHn2_yFTl5HLkki0FD6pjQOzB6v3EGMmNlTA")
@app.route("/form/EnterCode",methods=["POST"])
def LoadIntoGroup():
    GroupID = escape(request.form["GroupCode"])
    if DoesGroupExist(GroupID) == True:
        return "s"
    return "s"
@app.route("/Login/Spotify") #Create a check to see if user is already registed, if they are then we need to call a refresh token rather than a new one
def SpotifyLogIn():
    return render_template("Login.html")
    print("connected")
    #return redirect(ApplicationVerification())
    
@app.route("/Login/Apple")
def AppleLogIn():
    return "0";
@app.route("/Login/Google")
def GoogleLogin():
    return "0";
@app.errorhandler(404)
def page_not_found_error(e):
    return render_template("404.html"),404




###### DATABASE METHODS ####
def DoesGroupExist(GroupID):
    params = {'g':tuple([GroupID])}
    SQLcursor.execute("SELECT \"GroupId\" from Groups WHERE \"GroupId\" in %(g)s ",params)
    if SQLcursor.rowcount > 0:
        return True
    else:
        return False;

def AddUserToGroup(UserID,GroupID):
    
    return True

def CreateNewGroup(GroupID):
    return True


if __name__ == "__main__":
    debug = True
    port = int(os.environ.get("PORT",5000))
    app.run(host= '0.0.0.0',port=port,debug=debug)