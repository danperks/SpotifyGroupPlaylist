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
    


def GetAuthoristaionToken(): 
    #current understanding is on user authorisation i receive a code , i then send this off to /api/token as a post request to get the code proper
    return "0"
