import psycopg2
import secrets
import string
import requests
import json
conn = psycopg2.connect(host = "***REMOVED***",database = "***REMOVED***",user = "***REMOVED***",password= "***REMOVED***")
SQLcursor = conn.cursor()



def DatabaseRollback():
    curs = conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()

DatabaseRollback()