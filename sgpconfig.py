import configparser
from os import path

_config = configparser.ConfigParser()
_configPath = "sgpconfig.ini"

def __CreateConfig():
    __config = configparser.ConfigParser()
    __config["PostgreSQL Database"] = {
        "Host": "localhost",
        "Port": "5740",
        "Database": "sgp",
        "User": "foo",
        "Password": "bar"}
    __config["Spotify API"] = {
        "ClientID": "",
        "ClientSecret": ""
    }
    with open(_configPath, "w") as configfile:
        __config.write(configfile)
    
class SGPConfig():
    Host = ""
    Database = ""
    Port = ""
    User = ""
    Password = ""
    ClientID = ""
    ClientSecret = ""
    def __new__(self):
        try:
            c = configparser.ConfigParser()
            c.read(_configPath)
            self.Host =         c["PostgreSQL Database"]["Host"]
            self.Database =     c["PostgreSQL Database"]["Database"]
            self.Port =         c["PostgreSQL Database"]["Port"]
            self.User =         c["PostgreSQL Database"]["User"]
            self.Password =     c["PostgreSQL Database"]["Password"]
            self.ClientID =     c["Spotify API"]["ClientID"]
            self.ClientSecret = c["Spotify API"]["ClientSecret"]
            return self

        except KeyError as e:
            try:
                __CreateConfig()
                return "Created" #Once the config has been created, return string so we can warn the user to configure it
            except FileExistsError:
                raise FileExistsError(_configPath+" config file exists but we can't read it")
            raise e
        return None