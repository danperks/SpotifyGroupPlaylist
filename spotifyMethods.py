import requests
import urllib
import json
import os

if 'DATABASE_URL' in os.environ:
    from config import ClientID , ClientSecret,RedirectURL
else:
    from localconfig import ClientID , ClientSecret,RedirectURL


##Thoughts about database - instead of tracking the votes, we can jsut add a "local file " to each database which just has SongName - Vote Count - idk , maybe althouhg would need to think about what is done to stop multiple voting and it is a bodge
def ApplicationVerification():#https://developer.spotify.com/documentation/general/guides/authorization-guide/
    auth_parameters ={
        "client_id":ClientID,
        "response_type" : "code",
        "redirect_uri" : RedirectURL,
        "scope":"user-library-read user-library-modify user-read-private playlist-modify-public playlist-read-private playlist-modify-private"#ok proof of redirect method to the bbc. cant go wrong.
    }
    #print("https://accounts.spotify.com/authorize?"+for)
    return ("https://accounts.spotify.com/authorize?" + str(urllib.parse.urlencode(auth_parameters)))
    
def GetAuthoristaionToken(AppVerificationToken): 
    #current understanding is on user authorisation i receive a code , i then send this off to /api/token as a post request to get the code proper
    bodyParameters = {
        "grant_type":"authorization_code",
        "code":AppVerificationToken,
        "redirect_uri" : RedirectURL,  
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
    r = requests.post("https://accounts.spotify.com/api/token",bodyParameters).json()
    return r["access_token"]

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
        "ids":str(ListOfSpotifyID)
    }
    
    r= requests.get("https://api.spotify.com/v1/me/tracks/contains",headers=headers,params=bodyParameters)
    for item in ListOfSpotifyID:
        if r.json() == True:
            return True
        else:
            return False

def IsSongInUserLibrary(ListOfSpotifyID,UserAccessToken,start,end):
    try:
        if start >= len(ListOfSpotifyID):
            return []
        if end>len(ListOfSpotifyID):
            return []
        if start == end:
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
        
        for item in ListOfSpotifyID[start:end]:
            if r.json()[(ListOfSpotifyID.index(item,start,end)-start)] ==True:        
                    AlreadyPresent.append(item)
            else:
                continue
        if len(ListOfSpotifyID)<=(end+49):
            AlreadyPresent=[*AlreadyPresent,*IsSongInUserLibrary(ListOfSpotifyID,UserAccessToken,end,len(ListOfSpotifyID))]
        if len(ListOfSpotifyID)>(end+49):
            AlreadyPresent=[*AlreadyPresent,*IsSongInUserLibrary(ListOfSpotifyID,UserAccessToken,end,(end+49))]
        
        return AlreadyPresent
        #for every 50ID's
        #send API Request
        #if true add song ID to ArrayOfUserApproved
    
    except Exception as e:
        print(e)
        return AlreadyPresent
    

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
    headers = {
    'Authorization': 'Bearer '+str(UserAccessToken),
    
    }
    r = requests.get("https://api.spotify.com/v1/me/playlists",headers = headers)
    return r.json()

def FollowGroupPlaylist(Playlist,UserAccessToken):    
    headers = {
    'Authorization': 'Bearer '+str(UserAccessToken),
    'Content-Type': 'application/json',
    }
    data = '{"public": false}'
    response = requests.put('https://api.spotify.com/v1/playlists/'+str(Playlist)+'/followers', headers=headers, data=data)
    print(response.text)
    if response.status_code == 200:
        print("response true")       
        return True
    if response.status_code == 400:
        print(response.text)
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
        "description":str(description)+str("A Playlist Created By Spotify Bangers")
    }
    
    r = requests.post("https://api.spotify.com/v1/users/"+UserId+"/playlists",headers=headers,data = json.dumps(bodyParameters)).json()
    #print(json.dumps(bodyParameters))
    
    return r["id"]

def CopyPlaylist(OriginalPlaylistID, UserAccessToken):
    return "s"

def GetItemsInPlaylist(PlaylistId,UserAccessToken,ReturnAsSet=False):
    SongIds = []
    length = 0 ## off playlist
    offset = 0
    ##print("161 called")
    if ReturnAsSet == False:
        SongIds = []
    else:
        SongIds = set()
    while True:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization":'Bearer '+str(UserAccessToken)
            
        }
        r = requests.get("https://api.spotify.com/v1/playlists/"+PlaylistId+"/tracks?offset="+str(offset),headers=headers).json()
        length = int(r["total"])
        if ReturnAsSet == False:        
            for item in r["items"]:
                if item["is_local"] == False:
                    SongIds.append(item["track"]["id"])
            offset = offset+99
            if offset >length:## can see a logic error coming a mile off here , shouldnt do this at 1215 am
                break
        else:
            for item in  r["items"]:
                SongIds.add(item["track"]["id"])
            offset = offset+99
            if offset >length:
                break
    #print("183 lenght" +str(len(SongIds)))
    return SongIds

def DoesPlaylistExist(PlaylistId,AccessToken): ## check the string actually exists before going anywhere near the db
    SongIds = []
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization":'Bearer '+str(AccessToken)
        
    }
    r = requests.get("https://api.spotify.com/v1/playlists/"+PlaylistId+"/tracks",headers=headers).json()
    if r["items"]:
        return True
    else:
        return False


def PushToNewPlaylistController(UserAccessToken,ArrayOfSongs,PlaylistId,start,end):
    IsSongInPlaylist = GetItemsInPlaylist(PlaylistId,UserAccessToken,True)
    print("Current Amount in Playlist = " +  str(len(IsSongInPlaylist)))
    SongsToDelete = [i for i in IsSongInPlaylist if i not in ArrayOfSongs]
    print("After Deletion " + str(len(DeleteFromPlaylist(UserAccessToken,SongsToDelete,PlaylistId,start,end))))
    #print(IsSongInPlaylist)
    
    ArrayOfSongs = [i for i in ArrayOfSongs if i not in IsSongInPlaylist]
    
    #print("After " +str(len(ArrayOfSongs)))
    return  PushToNewPlaylist(UserAccessToken,ArrayOfSongs,PlaylistId,start,end)


def DeleteFromPlaylist(UserAccessToken,ArrayOfSongs,PlaylistId,start,end):
    if start == len(ArrayOfSongs):
        return []
    AlreadyPresent = []
    ArrayToSendOff = ["spotify:track:" + s for s in ArrayOfSongs[start:end]]## wonders why array is seemingly overwritten, doesnt see it, finds array being over written * owo shocked pikachu*
    headers = {
        "Accept": "application/json",
        "Authorization":'Bearer '+UserAccessToken
    }
    params = {"uris":ArrayToSendOff} ## might check later if this is inclusive or not , in which case somethign will have to be done
    r= requests.delete("https://api.spotify.com/v1/playlists/"+str(PlaylistId)+"/tracks",headers=headers,json=params)
    if len(ArrayOfSongs)<=end+99:
        DeleteFromPlaylist(UserAccessToken,ArrayOfSongs,PlaylistId,end,len(ArrayOfSongs))
    if len(ArrayOfSongs)>end+99:
        DeleteFromPlaylist(UserAccessToken,ArrayOfSongs,PlaylistId,end,(end+99))
    
    return AlreadyPresent

def PushToNewPlaylist(UserAccessToken,ArrayOfSongs,PlaylistId,start,end):
    if start == len(ArrayOfSongs):
        return []
    AlreadyPresent = []
    ArrayToSendOff = ["spotify:track:" + s for s in ArrayOfSongs[start:end]]## wonders why array is seemingly overwritten, doesnt see it, finds array being over written * owo shocked pikachu*
    headers = {
        "Accept": "application/json",
        "Authorization":'Bearer '+UserAccessToken
    }
    params = {"uris":ArrayToSendOff} ## might check later if this is inclusive or not , in which case somethign will have to be done
    r= requests.post("https://api.spotify.com/v1/playlists/"+str(PlaylistId)+"/tracks",headers=headers,json=params)
    if len(ArrayOfSongs)<=end+99:
        PushToNewPlaylist(UserAccessToken,ArrayOfSongs,PlaylistId,end,len(ArrayOfSongs))
    if len(ArrayOfSongs)>end+99:
        PushToNewPlaylist(UserAccessToken,ArrayOfSongs,PlaylistId,end,(end+99))
    
    return AlreadyPresent
    #do this https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/
    ##Takes array
    ##spotify api -> add items to playlist
    ##voila
