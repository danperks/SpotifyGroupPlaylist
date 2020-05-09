import requests
import urllib
ClientID = "***REMOVED***"
ClientSecret = "***REMOVED***"

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

def RefreshAccessToken(RefreshToken):
    bodyParameters = {
        "grant_type":"refresh_token",
        "refresh_token":RefreshToken,
        "client_id":ClientID,
        "client_secret":ClientSecret
    }
    return requests.post("https://accounts.spotify.com/api/token",bodyParameters).json()

#code = "AQCkFA0FSjks0q9WmXlgIhNJWi1TuSrFs7Umw5g9JgZ6_8HaDb6yx1w_sTFt4uwHx0U-tQGuZTB9pywDOarw8pvrPzSvjuk5cZRG3yqprZc_b_0xPqgOLgjE312OE6QLVh8u0ykBZy-0XtirME12sdYNs6O2EeZX2Gl2fIkDfBznDLCD8DL2rC8zeCNA8KeH29htkMNvfVWJu9Q"
#print(RefreshAccessToken(GetAuthoristaionToken(code)["refresh_token"]))
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