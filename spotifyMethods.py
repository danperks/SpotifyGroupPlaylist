import requests
import urllib
ClientID = "***REMOVED***"
ClientSecret = "***REMOVED***"

def ApplicationVerification():#https://developer.spotify.com/documentation/general/guides/authorization-guide/
    auth_parameters ={
        "client_id":"***REMOVED***",
        "response_type" : "code",
        "redirect_uri" : "http://127.0.0.1:5000/SpotifyCallback"#ok proof of redirect method to the bbc. cant go wrong.
    }
    #print("https://accounts.spotify.com/authorize?"+for)
    return ("https://accounts.spotify.com/authorize?" + str(urllib.parse.urlencode(auth_parameters)))
    


def GetAuthoristaionToken(AppVerificationToken): 
    #current understanding is on user authorisation i receive a code , i then send this off to /api/token as a post request to get the code proper
    print(AppVerificationToken)
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
    return requests.post("https://accounts.spotify.com/api/token",bodyParameters).json()

def RefreshAccessToken():
    return "s"

def GetUserID(UserAccessToken):
    return "s"
def GetUsersLikedSongs(UserAccessToken):
    return "s"

def GetUsersPlaylists(UserAccessToken):
    return "s"

def GetItemsInPlaylist(UserAccessToken):
    return "s"

def PushToNewPlaylist(UserAccessToken,ArrayOfSongs):
    return "s"