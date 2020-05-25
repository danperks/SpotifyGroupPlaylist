import requests
import urllib
import json
from config import ClientID , ClientSecret

##Thoughts about database - instead of tracking the votes, we can jsut add a "local file " to each database which just has SongName - Vote Count - idk , maybe althouhg would need to think about what is done to stop multiple voting and it is a bodge
def ApplicationVerification():#https://developer.spotify.com/documentation/general/guides/authorization-guide/
    auth_parameters ={
        "client_id":"***REMOVED***",
        "response_type" : "code",
        "redirect_uri" : "http://127.0.0.1:5000/SpotifyCallback",
        "scope":"user-library-read user-library-modify user-read-private playlist-modify-public playlist-read-private playlist-modify-private"#ok proof of redirect method to the bbc. cant go wrong.
    }
    #print("https://accounts.spotify.com/authorize?"+for)
    return ("https://accounts.spotify.com/authorize?" + str(urllib.parse.urlencode(auth_parameters)))
    
def GetAuthoristaionToken(AppVerificationToken): 
    #current understanding is on user authorisation i receive a code , i then send this off to /api/token as a post request to get the code proper
    bodyParameters = {
        "grant_type":"authorization_code",
        "code":AppVerificationToken,
        "redirect_uri" : "http://127.0.0.1:5000/SpotifyCallback",  
        "client_id":ClientID,
        "client_secret":ClientSecret      
    }
    ##headerParameters = { think it might want client id and secret base 64 but the api docs imply it wil take it in the body ,not convinced but here we go
    #}
    #print("https://accounts.spotify.com/api/token?"+str(urllib.parse.urlencode(bodyParameters)))
    #print(requests.post("https://accounts.spotify.com/api/token",bodyParameters).json())
    return requests.post("https://accounts.spotify.com/api/token",bodyParameters).json()

def RefreshAccessToken(RefreshToken):
    bodyParameters = {
        "grant_type":"refresh_token",
        "refresh_token":RefreshToken,
        "client_id":ClientID,
        "client_secret":ClientSecret
    }
    return requests.post("https://accounts.spotify.com/api/token",bodyParameters).json()["access_token"]

def GetUserID(UserAccessToken):
    headers = {
    "Authorization":'Bearer '+UserAccessToken,
    }
    return requests.get('https://api.spotify.com/v1/me', headers=headers).json()["id"]

def OneTimeIsSongInLibrary(ListOfSpotifyID,UserAccessToken):## Same func ,but doesnt need recursin for one time thing ,about that O you know
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization":'Bearer '+UserAccessToken
    }
    bodyParameters={
        "ids":",".join(ListOfSpotifyID)
    }
    
    r= requests.get("https://api.spotify.com/v1/me/tracks/contains",headers=headers,params=bodyParameters)
    for item in ListOfSpotifyID:
        if r.json() == True:
            return True
        else:
            return False

def IsSongInUserLibrary(ListOfSpotifyID,UserAccessToken,start,end):
    if start == len(ListOfSpotifyID):
        return []
    AlreadyPresent = []
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization":'Bearer '+UserAccessToken
    }
    bodyParameters={
        "ids":",".join(ListOfSpotifyID[start:end])
    }
    
    r= requests.get("https://api.spotify.com/v1/me/tracks/contains",headers=headers,params=bodyParameters)
    print(r)
    for item in ListOfSpotifyID[start:end]:
       if r.json()[ListOfSpotifyID.index(item)-start] ==True:        
            AlreadyPresent.append(item)
            
    if len(ListOfSpotifyID)<=end+49:
        AlreadyPresent=[*AlreadyPresent,*IsSongInUserLibrary(ListOfSpotifyID,UserAccessToken,end,len(ListOfSpotifyID))]
        #print(AlreadyPresent)
    if len(ListOfSpotifyID)>end+49:
        #print("lower")
        AlreadyPresent=[*AlreadyPresent,*IsSongInUserLibrary(ListOfSpotifyID,UserAccessToken,end,(end+49))]
       # print(AlreadyPresent)
    
    return AlreadyPresent
    #for every 50ID's
    #send API Request
    #if true add song ID to ArrayOfUserApproved
    

def GetUsersLikedSongs(UserAccessToken):#Pagination - Deprecated
    LikedSoFar = "";
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization":'Bearer '+UserAccessToken
        
    }
    bodyParameters={
        #"Authorization":UserAccessToken,
        "limit":50
        #"header":header
    }
    return requests.get("https://api.spotify.com/v1/me/tracks",headers=headers,params=bodyParameters).json()
    for item in requests.get("https://api.spotify.com/v1/me/tracks",headers=headers,params=bodyParameters).json():
        LikedSoFar = LikedSoFar + str(item["name"])
    return LikedSoFar
    

def GetUsersPlaylists(UserAccessToken):
    return "s"

def FollowGroupPlaylist(Playlist,UserAccessToken):    
    headers = {
    'Authorization': 'Bearer '+str(UserAccessToken),
    'Content-Type': 'application/json',
    }
    data = '{"public": false}'
    response = requests.put('https://api.spotify.com/v1/playlists/'+str(Playlist)+'/followers', headers=headers, data=data)
    if response.status_code == 200:       
        return True
    if response.status_code == 400:
        return False
        
def CreateGroupPlaylist(UserId,Name,UserAccessToken,description):
    print("called")
    headers = {
        'Authorization': 'Bearer ' + str(UserAccessToken),
        'Content-Type': 'application/json'
    }
    bodyParameters={
        "name":str(Name),
        "public":"false",
        "description":str(description)
    }
    
    r = requests.post("https://api.spotify.com/v1/users/"+UserId+"/playlists",headers=headers,data = json.dumps(bodyParameters)).json()
    #print(json.dumps(bodyParameters))
    
    return r["id"]

def GetItemsInPlaylist(PlaylistId,UserAccessToken):
    SongIds = []
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization":'Bearer '+str(UserAccessToken)
        
    }
    r = requests.get("https://api.spotify.com/v1/playlists/"+PlaylistId+"/tracks",headers=headers).json()
    
    for item in r["items"]:
        SongIds.append(item["track"]["id"])
    
    return SongIds


def PushToNewPlaylist(UserAccessToken,ArrayOfSongs,PlaylistId):
    ##Takes array
    ##spotify api -> add items to playlist
    ##voila
    return "s"
