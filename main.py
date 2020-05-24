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
from flask import json, session
from spotifyMethods import *
from config import *
import random
import string
import secrets


app = Flask(__name__)
app.static_folder = "static"
app.template_folder = "templates"
app.config["SECRET_KEY"] = SECRET_KEY
conn = psycopg2.connect(host = DatabaseHost,database = Database,user = DatabaseUser,password= DatabasePassword)
SQLcursor = conn.cursor()
## go environment varible for user and password , will do for now
#Database

@app.route("/CreateGroup",methods=["GET"])
def CreateGroup():
    UserID = GetUserIDFromRefreshToken(str(request.cookies["RefreshToken"]))
    return CreateNewGroup(UserID)[1]

@app.route("/SpotifyCallback")
def SpotifyCallBack(): # Spotify Logins in the user, user redirected to the group entry page
    userReturnedCode = request.args["code"]
    if userReturnedCode == "access_denied":
        print("ERROR : User Denies access ")
        return render_template("index.html")
    AuthToken = GetAuthoristaionToken(userReturnedCode)
    RefreshToken = AuthToken["refresh_token"]#tokens expire after one hour
    resp = make_response(render_template("Login.html"))
    resp.set_cookie("RefreshToken",RefreshToken)
    resp.set_cookie("AuthToken",AuthToken["access_token"])
    AddUserToDatabase(RefreshToken)
    return resp
    
@app.errorhandler(KeyError)
def IncorrectKeyError(e):
    return jsonify(error=str(e)),440
    
@app.route("/")#index - start page, user asked to either authorise with spotify - or automatic forward to group entry
def indexStart():
    if "RefreshToken" in request.cookies:
        print(request.cookies)
        print("Cookie Present")#just check for the token
        PreviousAuthorisation = IsThisStillValid(request.cookies["RefreshToken"])
        
        resp = make_response(render_template("Login.html"))
        print(RefreshAccessToken(PreviousAuthorisation))
        resp.set_cookie("AuthToken",RefreshAccessToken(PreviousAuthorisation))
        return resp
    else:
        print("No Cookie Present")
        return render_template("index.html")   

@app.route("/form/EnterCode",methods=["POST"])
def LoadIntoGroup():
    GroupID = escape(request.form["GroupCode"])
    UserID = GetUserIDFromRefreshToken(str(request.cookies["RefreshToken"]))
    if DoesGroupExist(GroupID) == True:
        if AddUserToGroup(UserID,GroupID):
            return render_template("VotingPage.html")
    return "s"

@app.route("/SpotifyAuthorise") #Create a check to see if user is already registed, if they are then we need to call a refresh token rather than a new one
def SpotifyLogIn():
        return redirect(ApplicationVerification())

@app.route("/VotesReturned",methods = ["GET"])
def VotesReturned():
    UserID = GetUserIDFromRefreshToken(request.cookies["RefreshToken"])
    InFavour = json.loads(request.args["InFavourVotes"])
    Against = json.loads(request.args["VotesAgainst"])
    GroupID = request.args["GroupId"]
    if GroupID == "ALL":
        GroupID = None
    print("GroupID" + str(GroupID))
    for item in InFavour:
        AddSongVote(item,UserID,True,GroupID)
    for item in Against:
        AddSongVote(item,UserID,False,GroupID)
    return str(GroupID)

@app.route("/AllVotesCastCheck",methods = ["GET"])
def AllVotesCastCheck():
    GroupID = request.args["GroupId"]
    AuthToken = request.cookies["AuthToken"]
    return HaveAllVotesBeenReceived(GroupID,AuthToken)

@app.route("/ReturnSongsAwaitVote",methods = ["GET"])
def ReturnSongsToVoteOn():
    #GroupId = request.form["GroupId"]
    GroupId = request.args["GroupId"]
    UserId = GetUserIDFromRefreshToken(str(request.cookies["RefreshToken"]))
    if IsUserInGroup(UserId,GroupId) == False:
        return render_template("Login.html")
    AuthToken = request.cookies["AuthToken"]
    Playlists = ReturnGroupPropostionPlaylists(UserId,GroupId)
    Songs = []    
    for item in Playlists:##adds all songs to the playlist
        for song in GetItemsInPlaylist(item,AuthToken):
            Songs.append(song)
    
    PreclearedSongs = IsSongInUserLibrary(Songs,AuthToken,0,49)#returns the songs that are in the usesrs library
    #print("PreDeclared Songs"+str(PreclearedSongs))
    
    #return jsonify("s")
    #print("JSON" + str(list(set(Songs).difference(set(PreclearedSongs)))))
    Songs = list(set(Songs).difference(set(CheckIfVoteHasBeenMadePreviously(Songs,UserId,GroupId))))#Remove already voted against for that group ,or for public
    return jsonify(list(set(Songs).difference(set(PreclearedSongs)))) # sketchy , but will review later, about to have lunch, probably also should return up to json, but that can wait until after lunch
    ##Queries Submitted Playlists
    ##Gets all songs
    ##if song is in liked songs, then it doesn't need to be voted on 
    ## if song is not in liked songs, it's spotify id is added to an array to be returned out

    
##Removed the google and apple placeholder
@app.errorhandler(404)
def page_not_found_error(e):
    return render_template("404.html"),404


def IsThisStillValid(RefreshTokenToCheck):
    return "s"
def GetSongs(UserId,GroupId,AuthToken):
    Playlists = ReturnGroupPropostionPlaylists(UserId,GroupId)
    Songs = []    
    for item in Playlists:##adds all songs to the playlist
        for song in GetItemsInPlaylist(item,AuthToken):
            Songs.append(song)
    return Songs

#### Pass Data To Front ###

@app.route("/api/UserGroups",methods=["GET"])

def ReturnUserGroups():
    UserID = GetUserIDFromRefreshToken(str(request.cookies["RefreshToken"]))
    Groups = GetUsersGroups(UserID)
    Names = GetGroupNames(Groups)
    return jsonify(Groups,Names)
    
###### DATABASE METHODS ####

def DoesGroupExist(GroupId):
    params = {'g':tuple([GroupId])}
    SQLcursor.execute("SELECT \"GroupId\" from public.\"Groups\" WHERE \"GroupId\" in %(g)s ",params)
    if SQLcursor.rowcount > 0:
        return True
    else:
        return False;## use to determine if ID unique, yes can be done easily with a postgres func but this is easier to build around for now

def DoesUserExist(UserId):
    params = {'g':tuple([UserId])}
    SQLcursor.execute("SELECT \"UserId\" from public.\"Users\" WHERE \"UserId\" in %(g)s ",params)
    if SQLcursor.rowcount > 0:
        return True
    else:
        return False;
def GetUsersInGroup(GroupID):
    params = {"GroupId":tuple([GroupID])}
    SQLcursor.execute("SELECT DISTINCT \"UserId\" FROM public.\"Memberships\" WHERE \"GroupId\" in %(GroupId)s",params)
    return [item[0] for item in SQLcursor.fetchall()]

def AddUserToGroup(UserId,GroupId):## Adds user to group membership , creates record of memebership for that id for that user
    ##Changed Database Schema - Something slightly more normalised 
    if DoesGroupExist(GroupId):
        if GroupId not in GetUsersGroups(UserId):
            if GroupLocked(GroupId) == False:
                #only allow new users if group is unlocked
                params = {"UserId":tuple([UserId]),"GroupId":tuple([GroupId])}
                SQLcursor.execute("INSERT INTO public.\"Memberships\"(\"GroupId\", \"UserId\") VALUES (%(GroupId)s, %(UserId)s);",params)
                conn.commit();
                return True
        else:
            return True
    else:
        ## return an error to display - that the group does not exist - force user to enter new group
        return False
    #check if group exists
    #add a memebership
    #commit changes
    #user now in group
    return True

def CreateNewGroup(UserId):
    GroupId =''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10)) ## Ideally would like to do databse generates random id 
    UserID = str(UserId)
    Name = UserID+"'s Group" ## Array of the user id's - obvs just contianig just one here    
    params = {'GroupId':tuple([GroupId]),'Users':tuple([UserID]),"Name":tuple([Name])}
    SQLcursor.execute("INSERT INTO public.\"Groups\"(\"GroupId\",\"LeadUser\",\"GroupName\") VALUES (%(GroupId)s,%(Users)s,%(Name)s);",params)
    conn.commit()
    AddUserToGroup(UserID,GroupId)
    return (True,GroupId)

def AddUserToDatabase(refresh_token):
    if DoesUserExist == False:
        UserID = GetUserID((RefreshAccessToken(refresh_token)))
        params = {'UserID':tuple([UserID]),'Refresh_Token':tuple([refresh_token])}
        SQLcursor.execute("INSERT INTO public.\"Users\"(\"UserId\", \"RefreshToken\") VALUES (%(UserID)s,%(Refresh_Token)s);",params)
        conn.commit()
        return True;
    else:
        return True;
    return "s"

def IsUserInGroup(UserID,GroupID):
    if GroupID in GetUsersGroups(UserID):
        return True
    else:
        return False

def RemoveUserFromGroup(UserId,GroupId):#reverse of add pretty much - not convinced on usage but will make anyway
    if DoesGroupExist(GroupId):
        params = {"UserId":tuple([UserId]),"GroupId":tuple([GroupId])}
        SQLcursor.execute("DELETE FROM public.\"Memberships\" WHERE (\"GroupId\", \"UserId\") = (%(GroupId)s, %(UserId)s);",params)
        conn.commit();
        return True;
    else:
        return False;

def GetUsersGroups(UserId):
    UserGroups = []
    params = {"UserId":tuple([UserId])}
    SQLcursor.execute("SELECT \"GroupId\" FROM \"Memberships\" WHERE \"UserId\" in %(UserId)s",params)
    for item in SQLcursor.fetchall():
        UserGroups.append(item[0])
    return UserGroups

def GetGroupNames(Groups):
    if len(Groups)>0:
        Names = []
        params ={"Groups":tuple(Groups)}
        SQLcursor.execute("SELECT \"GroupName\" FROM \"Groups\" WHERE \"GroupId\" in %(Groups)s",params)
        for item in SQLcursor.fetchall():
            Names.append(item[0])
        return Names
    else:
        return ["You Are Not In Any Groups At This Point"]

def GroupLocked(GroupId):#check if group is locked
    params = {"GroupId":tuple([GroupId])}
    print(SQLcursor.execute("SELECT \"Locked\" FROM \"Groups\" WHERE \"GroupId\" in %(GroupId)s",params))
    return SQLcursor.fetchall()[0][0]

def AddOutputPlaylist(PlaylistUrl,GroupId):
    params = {"Playlist":tuple([PlaylistUrl]),"GroupId":tuple([GroupId])}#maybe change that to playlist id - idk , see what happens
    SQLcursor.execute("UPDATE public.\"Groups\" SET \"Output\" = %(Playlist)s WHERE \"GroupId\" in %(GroupId)s ;",params)
    conn.commit();
    return True

def UserPlaylistSubmit(PlaylistId,UserId,GroupId):
    params = {"Playlist":tuple([PlaylistId]),"GroupId":tuple([GroupId]),"UserId":tuple([UserId])}
    SQLcursor.execute("INSERT INTO public.\"PlaylistSubmission\"(\"UserId\",\"PlaylistId\",\"GroupRelation\") VALUES (%(UserId)s,%(Playlist)s,%(GroupId)s);",params)
    conn.commit()##user submits the playlist of their "bangers"
    ##User submits playlist ID
    ##playlist recorded
    ##maybe a check on how many that user has submitted - idk , does it go against what were doing?
    #when user submits their own playlist each song they put in it is added to the "banger" song table as a vote on their behalf
    return "s"

def ReturnGroupPropostionPlaylists(UserId,GroupId):
    Playlists = []
    params = {"GroupId":tuple([GroupId]),"UserId":tuple([UserId])}
    SQLcursor.execute("SELECT \"PlaylistId\" FROM \"PlaylistSubmission\" WHERE \"GroupRelation\" in %(GroupId)s AND \"UserId\" NOT in %(UserId)s",params)
    for item in SQLcursor.fetchall():
        Playlists.append(item[0])
    return Playlists

def GetUserIDFromRefreshToken(Refresh_Token):
    SQLcursor2 = conn.cursor();
    params = {"RefreshToken":tuple([Refresh_Token])}
    SQLcursor2.execute("SELECT \"UserId\" FROM public.\"Users\" WHERE \"RefreshToken\" in %(RefreshToken)s",params)
    for item in SQLcursor2.fetchall():
        print("UserID" + item[0])
        return item[0]

def CheckIfVoteHasBeenMadePreviously(Songs,UserId,GroupId):
    output = []
    params = {"SongId":tuple(Songs),"UserId":tuple([UserId]),"GroupId":tuple([GroupId])}
    SQLcursor.execute("SELECT DISTINCT \"SongId\" FROM public.\"Songs\" WHERE \"SongId\" in %(SongId)s AND \"User\" in %(UserId)s AND \"GroupRelation\" = NULL or \"GroupRelation\" IN %(GroupId)s",params)
    for item in SQLcursor.fetchall():
        output.append(item[0])
    return output

def AddSongVote(SongId,UserId,LikedBool,GroupID):
    params = {"SongId":tuple([SongId]),"UserId":tuple([UserId]),"Liked":tuple([LikedBool]),"GroupID":tuple([GroupID])}
    SQLcursor.execute("INSERT INTO public.\"Songs\"(\"SongId\",\"User\",\"VoteInFavour\",\"GroupRelation\") VALUES (%(SongId)s,%(UserId)s,%(Liked)s,%(GroupID)s);",params)
    conn.commit();
    return True

def HasAVoteBeenReceived(SongId,GroupID,Users):#for each song gets the distinct votes for it, if the amount of votes is the same as users then its true
    params = {"SongId":tuple([SongId]),"UserId":tuple(Users),"GroupId":tuple([GroupID])}
    SQLcursor.execute("SELECT DISTINCT \"User\" FROM public.\"Songs\" WHERE \"SongId\" in %(SongId)s AND \"User\" in %(UserId)s AND \"GroupRelation\" = NULL or \"GroupRelation\" IN %(GroupId)s",params)
    return [item for item in SQLcursor.fetchall()]#return users who have voted for that song

def IsSongInPlaylistSubmitted(SongId,UserId,GroupId,AuthToken):
    Playlists = []
    params = {"GroupId":tuple([GroupId]),"UserId":tuple([UserId])}
    SQLcursor.execute("SELECT \"PlaylistId\" FROM \"PlaylistSubmission\" WHERE \"GroupRelation\" in %(GroupId)s AND \"UserId\" in %(UserId)s",params)
    for item in SQLcursor.fetchall():
        Playlists.append(item[0])  
    for item in Playlists:##adds all songs to the playlist
        for song in GetItemsInPlaylist(item,AuthToken):
            if song == SongId:
                return True
    
    return False
### MISC ##

def HaveAllVotesBeenReceived(GroupId,AuthToken):##plan is sketchy but it will do for now
    Songs = GetSongs("",GroupId,AuthToken)
    Users = GetUsersInGroup(GroupId)
    for Song in Songs:
        for UserToCheck in list(set(Users).difference(HasAVoteBeenReceived(Song,GroupId,Users))):
            if IsSongInPlaylistSubmitted(Song,UserToCheck) == False:
                if OneTimeIsSongInLibrary(Song,AuthToken) == False:
                    return False
    return True
            


    ##runs when the user reaches the end of the users stack to vote with
    ##checks every song in the group
    ##counts the amounts of votes the song has(not in favour or against just number) and records
    ##checks each user to see if they have it in their liked songs(could check just those that havent voted for it) and increase the number on the count for that song
    ##if count still hasnt reached the amount of users in the group for that song
    ##then it checks within the submitted playlists to see if any users have marked it on a banger playlist
    ##once the count for all the songs is the same as the amount of users in the group , all votes have been recived
    return "s"

def PlaylistOutput(GroupId,AuthToken):
    Songs = GetSongs("",GroupId,AuthToken)
    Users = GetUsersInGroup(GroupId)
    ##not neccessarily all in this method but the plan
    ## Get lead user ID(first in Array)
    ## get refresh token from users table
    ## obtain access token using above
    ## create new playlist in that users library
    ## add neccessary songs to that playlist

    ##Check to see all songs have been voted on , done by checking accs then check the db for those not in accs
    ##once all done
    ##Those in db with all votes are added to playlist output
    ##then
    ## For every song not marked off by each user , the song is queried against that users library to see if liked, if liked that vote is then taken
    ##when all songs have received a vote then they are put on the output playlsit
    ##

    ##sketchy : but could assume that a missing vote on the db indicates it's already saved to that user's library as we record new likes and dislikes , meaning that old likes are the only ones missing
    ##would however mean that not voting counts in favour, but probably best incase someone fails to keep voting , idk

    ##
    return "s"


if __name__ == "__main__":
    debug = True
    port = int(os.environ.get("PORT",5000))
    app.run(host= '0.0.0.0',port=port,debug=debug)
    