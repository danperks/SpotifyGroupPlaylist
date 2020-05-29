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
def GetNewSQLCursor():
    conn = psycopg2.connect(host = DatabaseHost,database = Database,user = DatabaseUser,password= DatabasePassword)
    return conn

@app.route('/favicon.ico')    
def icon():
    return send_file("./static/favicon.ico", mimetype='image/ico')
@app.route("/CreateGroup",methods=["GET"])
def CreateGroup():
    UserID = GetUserIDFromRefreshToken(str(request.cookies["RefreshToken"]))
    return CreateNewGroup(UserID)[1]
@app.route("/Output")

def RunOutput():
     return PlaylistOutput("J9r9J30pwi",str(request.cookies["AuthToken"]))
   

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
    resp.set_cookie("UserId",GetUserID(AuthToken["access_token"]))
    resp.set_cookie("AuthToken",AuthToken["access_token"])
    AddUpdateUserRefreshToken(GetUserID(AuthToken["access_token"]),RefreshToken)##Used to add a new user to the database
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
        print("pass")
        if AddUserToGroup(UserID,GroupID):
            return render_template("VotingPage.html")
    return "Failure Loading Into Group"
@app.route("/Management/AbandonGroup",methods = ["GET"])
def AbandonGroup():
    UserID = GetUserIDFromRefreshToken(str(request.cookies["RefreshToken"]))
    GroupCode = request.args["GroupCode"]
    if GroupCode:
        RemoveUserFromGroup(UserID,GroupCode)
    return "True"
@app.route("/SpotifyAuthorise") #Create a check to see if user is already registed, if they are then we need to call a refresh token rather than a new one
def SpotifyLogIn():
        return redirect(ApplicationVerification())

@app.route("/VotesReturned",methods = ["GET"])
def VotesReturned():## function originally designed to process all votes at once, but doign one individually will work , not a big enough priority to refine further
    UserID = GetUserIDFromRefreshToken(request.cookies["RefreshToken"])
    InFavour = request.args.get("InFavourVotes",None)
    Against = request.args.get("VotesAgainst",None)
    GroupID = request.args["GroupId"]
    if GroupID == "ALL":
        GroupID = None
    print("GroupID" + str(GroupID))
    if InFavour:
        for item in json.loads(InFavour):
            AddSongVote(item,UserID,True,GroupID)
    if Against:
        for item in json.loads(Against):
            AddSongVote(item,UserID,False,GroupID)
    return str(GroupID)

@app.route("/AllVotesCastCheck",methods = ["GET"])
def AllVotesCastCheck():
    GroupID = request.args["GroupId"]
    AuthToken = request.cookies["AuthToken"]
    return HaveAllVotesBeenReceived(GroupID,AuthToken)

@app.route("/ReturnSongsAwaitVote",methods = ["GET"])
def ReturnSongsToVoteOn():
    print("ssssdjsjd")
    #GroupId = request.form["GroupId"]
    GroupId = request.args["GroupId"]
    UserId = GetUserIDFromRefreshToken(str(request.cookies["RefreshToken"]))
    if IsUserInGroup(UserId,GroupId) == False:
        print("Wong group")
        return render_template("Login.html")
    AuthToken = request.cookies["AuthToken"]
    print("22")
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
    output =  jsonify(list(set(Songs).difference(set(PreclearedSongs)))) # sketchy , but will review later, about to have lunch, probably also should return up to json, but that can wait until after lunch
    print(list(set(Songs).difference(set(PreclearedSongs))))
    return output
    ##Queries Submitted Playlists
    ##Gets all songs
    ##if song is in liked songs, then it doesn't need to be voted on 
    ## if song is not in liked songs, it's spotify id is added to an array to be returned out

    
##Removed the google and apple placeholder
@app.errorhandler(404)
def page_not_found_error(e):
    return render_template("404.html"),404


def IsThisStillValid(RefreshTokenToCheck):
    try:
        GetUserIDFromRefreshToken(RefreshTokenToCheck)
        return RefreshTokenToCheck
    except KeyError:
        return render_template("index.html")
    
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
    try:
        #SQLcursor = GetNewSQLCursor()
        params = {'g':tuple([GroupId])}
        SQLcursor.execute("SELECT \"GroupId\" from public.\"Groups\" WHERE \"GroupId\" in %(g)s ",params)
        if SQLcursor.rowcount > 0:
            return True
        else:
            print("false")
            return False;## use to determine if ID unique, yes can be done easily with a postgres func but this is easier to build around for now
    except Exception as e:
        print(e)
        DatabaseRollback()
        return render_template("index.html")
def DoesUserExist(UserId):
    try:
        #SQLcursor = GetNewSQLCursor()
        params = {'g':tuple([UserId])}
        SQLcursor.execute("SELECT \"UserId\" from public.\"Users\" WHERE \"UserId\" in %(g)s ",params)
        if SQLcursor.rowcount > 0:
            return True
        else:
            return False;
    except:
        DatabaseRollback()
        return render_template("index.html")
def GetUsersInGroup(GroupID):
    try:
        #SQLcursor = GetNewSQLCursor()
        params = {"GroupId":tuple([GroupID])}
        SQLcursor.execute("SELECT DISTINCT \"UserId\" FROM public.\"Memberships\" WHERE \"GroupId\" in %(GroupId)s",params)
        return [item[0] for item in SQLcursor.fetchall()]
    except:
        DatabaseRollback()
        return render_template("index.html")
def AddUpdateUserRefreshToken(UserId,RefreshToken): ## Name could do with rectification 
    try:
        #SQLcursor = GetNewSQLCursor()
        params = {"UserId":tuple([UserId]),"RefreshToken":tuple([RefreshToken])}
        SQLcursor.execute("INSERT INTO public.\"Users\"(\"UserId\",\"RefreshToken\") VALUES (%(UserId)s,%(RefreshToken)s) ON CONFLICT (\"UserId\") DO UPDATE SET \"RefreshToken\" = %(RefreshToken)s RETURNING \"RefreshToken\" ",params)
        conn.commit()
        return "s"
    except:
        DatabaseRollback()
        return render_template("index.html")
def AddUserToGroup(UserId,GroupId):## Adds user to group membership , creates record of memebership for that id for that user
    ##Changed Database Schema - Something slightly more normalised 
    try:
        print("ss")
        #SQLcursor = GetNewSQLCursor()
        if DoesGroupExist(GroupId):
            print("cle")
            if GroupId not in GetUsersGroups(UserId):
                if GroupLocked(GroupId) == False:
                    #only allow new users if group is unlocked
                    params = {"UserId":tuple([UserId]),"GroupId":tuple([GroupId])}
                    SQLcursor.execute("INSERT INTO public.\"Memberships\"(\"GroupId\", \"UserId\") VALUES (%(GroupId)s, %(UserId)s);",params)
                    conn.commit()
                    SQLcursor.execute("SELECT \"Output\" FROM public.\"Groups\" WHERE \"GroupId\" IN %(GroupId)s",params)
                    print(SQLcursor.fetchall())
                    if FollowGroupPlaylist(SQLcursor.fetchall()[0],request.cookies["AuthToken"]):
                        return True
            else:
                return True
        else:
            print("flas")
            ## return an error to display - that the group does not exist - force user to enter new group
            return False
        #check if group exists
        #add a memebership
        #commit changes
        #user now in group
        return True
    except Exception as e:
        print(e)
        DatabaseRollback()
        return render_template("index.html")

def CreateNewGroup(UserId):
    try:
        #SQLcursor = GetNewSQLCursor()
        GroupId =''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10)) ## Ideally would like to do databse generates random id 
        UserID = str(UserId)
        Name = UserID+"'s Group" ## Array of the user id's - obvs just contianig just one here    
        params = {'GroupId':tuple([GroupId]),'Users':tuple([UserID]),"Name":tuple([Name]),"Output":tuple([CreateGroupPlaylist(UserId,str(Name),request.cookies["AuthToken"],str(UserId))])}
        SQLcursor.execute("INSERT INTO public.\"Groups\"(\"GroupId\",\"Output\",\"LeadUser\",\"GroupName\") VALUES (%(GroupId)s,%(Output)s,%(Users)s,%(Name)s);",params)
        conn.commit()
        print("Group Created")
        AddUserToGroup(UserID,GroupId)
        # return (True,GroupId)
    except Exception as e:
        print(e)
        DatabaseRollback()
        return render_template("index.html")

def AddUserToDatabase(refresh_token): ## Deprecated - In Favour of Update Refresh Token - Insert on Conflict
    try:
        #SQLcursor = GetNewSQLCursor()
        UserId = GetUserID((RefreshAccessToken(refresh_token)))
        if DoesUserExist(UserId) == False:        
            params = {'UserID':tuple([UserId]),'Refresh_Token':tuple([refresh_token])}
            SQLcursor.execute("INSERT INTO public.\"Users\"(\"UserId\", \"RefreshToken\") VALUES (%(UserID)s,%(Refresh_Token)s);",params)
            conn.commit()
            return True;
        else:
            return True;
        return "s"
    except:
        DatabaseRollback()
        return render_template("index.html")

def IsUserInGroup(UserID,GroupID):
    try:
        #SQLcursor = GetNewSQLCursor()
        if GroupID in GetUsersGroups(UserID):
            return True
        else:
            return False
    except:
        DatabaseRollback()
        return render_template("index.html")

def RemoveUserFromGroup(UserId,GroupId):#reverse of add pretty much - not convinced on usage but will make anyway
    try:
        #SQLcursor = GetNewSQLCursor()
        if DoesGroupExist(GroupId):
            if IsUserLeadUser(UserId,GroupId):
                if SetNewLeadUser(UserId,GroupId) == False:##If the user is the last person in the group then they remain listed against the group but without membership, an error but not one big enough for now
                    return "False"
            params = {"UserId":tuple([UserId]),"GroupId":tuple([GroupId])}
            SQLcursor.execute("DELETE FROM public.\"Memberships\" WHERE (\"GroupId\", \"UserId\") = (%(GroupId)s, %(UserId)s);",params)
            conn.commit();
            return "True"
        else:
            return "False";
    except:
        print("ERROR : Database Rolled Back")
        DatabaseRollback()
        return render_template("/index.html")

def SetNewLeadUser(UserIdToDelete,GroupId):
    try:
        #SQLcursor = GetNewSQLCursor()
        params = {"UserId":tuple([UserIdToDelete]),"GroupId":tuple([GroupId])}
        SQLcursor.execute("SELECT \"UserId\" FROM public.\"Memberships\" WHERE \"GroupId\" IN %(GroupId)s AND \"UserId\" NOT IN %(UserId)s",params)
        NewUserId = SQLcursor.fetchall()[0][0]
        if NewUserId == None:
            return False
        else:
            params["NewUserLead"] = tuple([NewUserId])## not so sure about this 
            SQLcursor.execute("UPDATE public.\"Groups\" SET \"LeadUser\" = %(NewUserLead)s WHERE \"GroupId\" IN %(GroupId)s",params)
            conn.commit()
            ##Get the access token for the replacment user
            SQLcursor2 = conn.cursor()
            SQLcursor2.execute("SELECT \"RefreshToken\" FROM public.\"Users\" WHERE \"UserId\" IN %(NewUserLead)s",params)
            AccessToken = RefreshAccessToken(SQLcursor2.fetchall()[0][0])
            AddOutputPlaylist(CreateGroupPlaylist(NewUserId,str(NewUserId)+"'s New Group",AccessToken,"Group Playlist"),GroupId)
            return True
    except:
        DatabaseRollback()
        return False# might regret not having this redirect back to the front page but for now
def IsUserLeadUser(UserId,GroupId):
    try:
        #SQLcursor = GetNewSQLCursor()
        params = {"GroupId":tuple([GroupId])}
        SQLcursor.execute("SELECT \"LeadUser\" FROM public.\"Groups\" WHERE \"GroupId\" IN %(GroupId)s",params)
        if (SQLcursor.fetchall()[0][0]) == UserId:
            return True
        else:
            return False
    except:
        DatabaseRollback()
        return render_template("index.html")
def GetLeadUser(GroupId):
    try:
        #SQLcursor = GetNewSQLCursor()
        params = {"GroupId":tuple([GroupId])}
        SQLcursor.execute("SELECT \"LeadUser\" FROM public.\"Groups\" WHERE \"GroupId\" IN %(GroupId)s",params)
        LeadUser = SQLcursor.fetchall()[0][0]
        return LeadUser
    except:
        DatabaseRollback()
        return render_template("index.html")
    
def GetUsersGroups(UserId):
    try:
        #SQLcursor = GetNewSQLCursor().cursor()
        UserGroups = []
        params = {"UserId":tuple([UserId])}
        SQLcursor.execute("SELECT \"GroupId\" FROM \"Memberships\" WHERE \"UserId\" in %(UserId)s",params)
        for item in SQLcursor.fetchall():
            UserGroups.append(item[0])
        return UserGroups
    except Exception as e:
        DatabaseRollback()
        return render_template("index.html")
def GetGroupNames(Groups):
    try:
        #SQLcursor = GetNewSQLCursor().cursor()
        if len(Groups)>0:
            Names = []
            params ={"Groups":tuple(Groups)}
            SQLcursor.execute("SELECT \"GroupName\" FROM \"Groups\" WHERE \"GroupId\" in %(Groups)s",params)
            for item in SQLcursor.fetchall():
                Names.append(item[0])
            return Names
        else:
            return ["You Are Not In Any Groups At This Point"]
    except:
        DatabaseRollback()
        return render_template("index.html")
def GroupLocked(GroupId):#check if group is locked
    try: 
        #SQLcursor = GetNewSQLCursor().cursor()           
        params = {"GroupId":tuple([GroupId])}
        print(SQLcursor.execute("SELECT \"Locked\" FROM \"Groups\" WHERE \"GroupId\" in %(GroupId)s",params))
        return SQLcursor.fetchall()[0][0]
    except:
        DatabaseRollback()
        return render_template("index.html")

def AddOutputPlaylist(PlaylistUrl,GroupId):
    try:
        #SQLcursor = GetNewSQLCursor()
        params = {"Playlist":tuple([PlaylistUrl]),"GroupId":tuple([GroupId])}#maybe change that to playlist id - idk , see what happens
        SQLcursor.execute("UPDATE public.\"Groups\" SET \"Output\" = %(Playlist)s WHERE \"GroupId\" in %(GroupId)s ;",params)
        conn.commit();
        return True
    except:
        DatabaseRollback()
        return render_template("index.html")
def GetOutputPlaylist(GroupId):
    try:
        #SQLcursor = GetNewSQLCursor().cursor()
        params = {"GroupID":tuple([GroupId])}
        SQLcursor.execute("SELECT \"Output\" FROM \"Groups\" WHERE \"GroupId\" in %(GroupId)s",params)
        return SQLcursor.fetchall()[0][0]
    except Exception as e:
        print(e)
        DatabaseRollback()
        render_template("/index.html")

def UserPlaylistSubmit(PlaylistId,UserId,GroupId):
    try:
        #SQLcursor = GetNewSQLCursor()
        params = {"Playlist":tuple([PlaylistId]),"GroupId":tuple([GroupId]),"UserId":tuple([UserId])}
        SQLcursor.execute("INSERT INTO public.\"PlaylistSubmission\"(\"UserId\",\"PlaylistId\",\"GroupRelation\") VALUES (%(UserId)s,%(Playlist)s,%(GroupId)s);",params)
        conn.commit()##user submits the playlist of their "bangers"
        ##User submits playlist ID
        ##playlist recorded
        ##maybe a check on how many that user has submitted - idk , does it go against what were doing?
        #when user submits their own playlist each song they put in it is added to the "banger" song table as a vote on their behalf
        return "s"
    except:
        DatabaseRollback()
        return render_template("index.html")
def ReturnGroupPropostionPlaylists(UserId,GroupId):
    try:
        #SQLcursor = GetNewSQLCursor().cursor()
        Playlists = []
        params = {"GroupId":tuple([GroupId]),"UserId":tuple([UserId])}
        SQLcursor.execute("SELECT \"PlaylistId\" FROM \"PlaylistSubmission\" WHERE \"GroupRelation\" in %(GroupId)s AND \"UserId\" NOT in %(UserId)s",params)
        for item in SQLcursor.fetchall():
            Playlists.append(item[0])
        return Playlists
    except Exception as e:
        print(e)
        DatabaseRollback()
        return render_template("index.html")
def GetUserIDFromRefreshToken(Refresh_Token):
    try:
        SQLcursor2 = conn.cursor();
        params = {"RefreshToken":tuple([Refresh_Token])}
        SQLcursor2.execute("SELECT \"UserId\" FROM public.\"Users\" WHERE \"RefreshToken\" in %(RefreshToken)s",params)
        for item in SQLcursor2.fetchall():
            print("UserID" + item[0])
            return item[0]
    except Exception as e:
        print(e)
        DatabaseRollback()
        return render_template("index.html")

def GetRefreshTokenFromUserId(UserId):
    try:
        SQLcursor2 = conn.cursor();
        params = {"UserId":tuple([UserId])}
        SQLcursor2.execute("SELECT \"RefreshToken\" FROM public.\"Users\" WHERE \"UserId\" in %(UserId)s",params)
        for item in SQLcursor2.fetchall():
            #print("UserID" + item[0])
            print("Refresh Token Returned")
            return item[0]
    except:
        DatabaseRollback()
        return render_template("index.html")
    

def CheckIfVoteHasBeenMadePreviously(Songs,UserId,GroupId):
    try:
        #SQLcursor = GetNewSQLCursor().cursor()
        output = []
        params = {"SongId":tuple(Songs),"UserId":tuple([UserId]),"GroupId":tuple([GroupId])}
        if(len(Songs) == 0):
            return "No Songs have been submitted yet, why not try and add some "
        SQLcursor.execute("SELECT DISTINCT \"SongId\" FROM public.\"Songs\" WHERE \"SongId\" in %(SongId)s AND \"User\" in %(UserId)s AND (\"GroupRelation\" IS NULL or \"GroupRelation\" IN %(GroupId)s)",params)
        #print(SQLcursor.mogrify("SELECT DISTINCT \"SongId\" FROM public.\"Songs\" WHERE \"SongId\" in %(SongId)s AND \"User\" in %(UserId)s AND \"GroupRelation\" = NULL or \"GroupRelation\" IN %(GroupId)s",params))
        for item in SQLcursor.fetchall():
            output.append(item[0])
       # print(output)
        return output
    except Exception as e:
        print(e)
        DatabaseRollback()
        return render_template("index.html")

def AddSongVote(SongId,UserId,LikedBool,GroupID):
    try:
        #SQLcursor = GetNewSQLCursor()        
        params = {"SongId":tuple([SongId]),"UserId":tuple([UserId]),"Liked":tuple([LikedBool]),"GroupID":tuple([GroupID])}
        SQLcursor.execute("INSERT INTO public.\"Songs\"(\"SongId\",\"User\",\"VoteInFavour\",\"GroupRelation\") VALUES (%(SongId)s,%(UserId)s,%(Liked)s,%(GroupID)s);",params)
        conn.commit();
        print("Vote Recorded for " +str(SongId) +" "+ str(UserId)+" "+str(LikedBool))
        return True
    except:
        DatabaseRollback()
        return render_template("index.html")

def HasAVoteBeenReceived(SongId,GroupID,Users):
    try:#for each song gets the distinct votes for it, if the amount of votes is the same as users then its true
        #SQLcursor = GetNewSQLCursor().cursor()
        params = {"SongId":tuple([SongId]),"UserId":tuple(Users),"GroupId":tuple([GroupID])}
        SQLcursor.execute("SELECT DISTINCT \"User\" FROM public.\"Songs\" WHERE \"SongId\" in %(SongId)s AND \"User\" in %(UserId)s AND (\"GroupRelation\" IS NULL or \"GroupRelation\" IN %(GroupId)s)",params)
        return [item for item in SQLcursor.fetchall()]#return users who have voted for that song
    except:
        DatabaseRollback()
        return render_template("index.html")
def ReturnPostiveVoesForSong(SongId,GroupID,Users):
    try:#for each song gets the distinct votes for it, if the amount of votes is the same as users then its true
        #SQLcursor = GetNewSQLCursor().cursor()
        params = {"SongId":tuple([SongId]),"UserId":tuple(Users),"GroupId":tuple([GroupID])}
        SQLcursor.execute("SELECT DISTINCT \"User\" FROM public.\"Songs\" WHERE \"SongId\" in %(SongId)s AND \"User\" in %(UserId)s AND (\"GroupRelation\" IS NULL or \"GroupRelation\" IN %(GroupId)s) AND \"VoteInFavour\" = TRUE",params)
        return [item[0] for item in SQLcursor.fetchall()]#return users who have voted for that song
    except Exception as e:
        print(e)
        DatabaseRollback()
        return redirect("index.html") ##not so sure about this but itll do
def IsSongInPlaylistSubmitted(SongId,UserId,GroupId,AuthToken):
    Playlists = []
    try:
        #SQLcursor = GetNewSQLCursor().cursor()
        params = {"GroupId":tuple([GroupId]),"UserId":tuple([UserId])}
        SQLcursor.execute("SELECT \"PlaylistId\" FROM \"PlaylistSubmission\" WHERE \"GroupRelation\" in %(GroupId)s AND \"UserId\" in %(UserId)s",params)
        for item in SQLcursor.fetchall():
            Playlists.append(item[0])  
        print("Playlists Submittd" + str(Playlists) + str(UserId))
        for item in Playlists:##adds all songs to the playlist
            for song in GetItemsInPlaylist(item,AuthToken):
                if song == SongId:
                    print ("Song in Playlist Submitted by " + str(UserId))
                    return True
    except:
        DatabaseRollback()

    
    return False

### Meta as in the other meta##
def DatabaseRollback():
    curs = conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()

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
    UserKeys = {}
    for User in Users:
        UserKeys[User] = RefreshAccessToken(GetRefreshTokenFromUserId(User))

    LeadUserAccessToken = RefreshAccessToken(GetRefreshTokenFromUserId(GetLeadUser(GroupId))) # i think hti smight bring up t he cookie mistmatch error again with the amount of refreshes im doing rn
    ##if HaveAllVotesBeenReceived(GroupId,AuthToken): ## Might have it work only when all votes have been recieived, but if its called on every vote idk
    OutputPlaylist = str(GetOutputPlaylist(GroupId))
    SongsToAdd = []
    for Song in Songs:
        UsersWhoVotedPostive = ReturnPostiveVoesForSong(Song,GroupId,Users)
        print("Users Who Voted Positive " + str(set(UsersWhoVotedPostive)))
        #print(str(Users)+" - Total Users")
        #print(str(UsersWhoVotedPostive) +" - Users Pos Votes")
        if set(UsersWhoVotedPostive) == set(Users):
            SongsToAdd.append("spotify:track:"+str(Song)) ## Song has been voted on as a banger by all users, this will very rarely be achevied as it can only be triggered if the person who propsed it leaves the group after votes have been cast
        else:
            IsSongApproved = True # Assumption of True - famous last words
            for User in set(Users).difference(UsersWhoVotedPostive):
                print("Current User " + str(User))
                UserAccessToken = UserKeys[User]                
                if OneTimeIsSongInLibrary(Song,UserAccessToken):
                    print(str(Song) + " -  Positive " + str(User))
                    pass #do nothing - its calm                    
                elif IsSongInPlaylistSubmitted(Song,User,GroupId,UserAccessToken):
                    print(str(Song) + " -  Positive " + str(User))
                    pass ## do nothing -its calm . assumption will take care of it
                    
                else:
                    print(str(Song) +" is not approved")
                    IsSongApproved = False
                
            if IsSongApproved == True:
                print(str(Song) + " Song Approved")
                SongsToAdd.append("spotify:track:"+str(Song))## this is sketchy , would need to see if somehow i can push to the spotofy playlist jsut off song id(i would think i can as they are returned when you go the other way), but for now as the URI are just id+what was detailed, it'll do
   
   
    ## Pushing of selected  songs
    if PushToNewPlaylist(LeadUserAccessToken,SongsToAdd,OutputPlaylist):
        return str(SongsToAdd)
    else:
        return str(SongsToAdd)

## New Plan

## At Present,  I am 90% confident that the above works. Will check a bit further.
## But it is so slow and inefficent

## I propose , Query spotify first , for all the songs in the playlist - store the true and false in a dictionary for each song for that user
## for song not true for that user, then check if it was them that submitted it
## lastly check our db to see what their votes were for the songs that are still false

## the above can in theroy work in either order, the reverse will mean easier reqs to send to spotify

## then once all of the above is done,
##check the dictionaries of all 3 of the users and find the songs in common that are marked as true
## this will in theory make the system more efficent

## as it stands, whilst confident in obtaining the data to produce an accurate result(i.e the concept is fine), the product is not deliverable being this inefficent 

                    

                    
                
        

        
    




    return "s"


def ExceptionHandler(ExceptionData):
    ##export exception data to a log file
    
    return "s"

if __name__ == "__main__":
    debug = True
    port = int(os.environ.get("PORT",5000))
    app.run(host= '0.0.0.0',port=port,debug=debug)
    