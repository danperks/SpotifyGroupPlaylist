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
from spotifyMethods import *
import sgpconfig


config = sgpconfig.SGPConfig()
if config == None:
    print("ERROR: Config was not properly initialised, it may not exist")
    exit(1)
elif config == "Created":
    print("WARNING: The config has been created, you will need to edit it")
    exit(1)

app = Flask(__name__)
app.static_folder = "static"
app.template_folder = "templates"
conn = psycopg2.connect(host=config.Host, database=config.Database, user=config.User, password=config.Password)
SQLcursor = conn.cursor()
## go environment varible for user and password , will do for now
#Database
@app.route("/SpotifyCallback")

def SpotifyCallBack(): # Spotify Logins in the user, user redirected to the group entry page
    userReturnedCode = request.args["code"]
    if userReturnedCode == "access_denied":
        print("ERROR : User Denies access ")
        return render_template("index.html")
    AuthToken = GetAuthoristaionToken(str(userReturnedCode))
    RefreshToken = AuthToken["refresh_token"]#tokens expire after one hour
    resp = make_response(render_template("Login.html"))
    resp.set_cookie("RefreshToken",RefreshToken)
    AddUserToDatabase(RefreshToken)
    return resp
    
@app.route("/")#index - start page, user asked to either authorise with spotify - or automatic forward to group entry
def indexStart():
    if "RefreshToken" in request.cookies:
        print(request.cookies)
        print("Cookie Present")#just check for the token
        PreviousAuthorisation = request.cookies["RefreshToken"]
        return render_template("Login.html")
    else:
        print("No Cookie Present")
        return render_template("index.html")   

@app.route("/form/EnterCode",methods=["POST"])
def LoadIntoGroup():
    GroupID = escape(request.form["GroupCode"])
    if DoesGroupExist(GroupID) == True:
        return "s"
    return "s"
@app.route("/SpotifyAuthorise") #Create a check to see if user is already registed, if they are then we need to call a refresh token rather than a new one
def SpotifyLogIn():
        return redirect(ApplicationVerification())
    
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
def DoesGroupExist(GroupId):
    params = {'g':tuple([GroupId])}
    SQLcursor.execute("SELECT \"GroupId\" from Groups WHERE \"GroupId\" in %(g)s ",params)
    if SQLcursor.rowcount > 0:
        return True
    else:
        return False;

def AddUserToGroup(UserId,GroupId):
    #check if group exists
    #either alter the user array and add the id, or just pull it down unpack, add , and repack with the new one
    #commit changes
    #user now in group
    return True

def CreateNewGroup(UserId,GroupId):
    GroupId ="" ## Ideally would like to do databse generates random id 
    UserID = "" ## Array of the user id's - obvs just contianig just one here    
    params = {'GroupId':tuple([GroupId]),'Users':tuple([UserID])}
    SQLcursor.execute("INSERT INTO public.\"Groups\"(\"GroupId\",\"Users\") VALUES (%(GroupId)s,%(Users)s);",params)
    conn.commit()
    return True

def AddUserToDatabase(refresh_token):
    UserID = GetUserID(RefreshAccessToken(refresh_token)["access_token"])
    params = {'UserID':tuple([UserID]),'Refresh_Token':tuple([refresh_token])}
    SQLcursor.execute("INSERT INTO public.\"Users\"(\"UserId\", \"RefreshToken\") VALUES (%(UserID)s,%(Refresh_Token)s);",params)
    conn.commit()
    return "s"

### MISC ##

def PlaylistOutput():
    ##not neccessarily all in this method but the plan
    ## Get lead user ID(first in Array)
    ## get refresh token from users table
    ## obtain access token using above
    ## create new playlist in that users library
    ## add neccessary songs to that playlist
    return "s"


if __name__ == "__main__":
    debug = True
    port = int(os.environ.get("PORT",5000))
    app.run(host= '0.0.0.0',port=port,debug=debug)