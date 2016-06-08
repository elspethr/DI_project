#Crowd modeling proof of concept

#Created 2016/06/08

#Description:
#initial analysis of tweets for capstone project
#modeling correlation of tweets and wait times at two Disney theme parks

import datetime
import re #regular expressions
import MySQLdb
import pandas.io.sql as sql
import pandas as pd
from matplotlib import pyplot as plt

#get data from db
conn = MySQLdb.connect(host="localhost", port=3306, user="root", db="disney_db") #make db connection
cursor = conn.cursor()

#twitter data
cursor.execute("SELECT id, timestamp, location FROM twitter_data_copy WHERE location = 'anaheim' AND timestamp > '2015-08-04' AND timestamp < '2015-08-30' ")
rows = cursor.fetchall()
tweetdf = pd.DataFrame( [[ij for ij in i] for i in rows] )
tweetdf.rename(columns={0: 'tweetid', 1: 'timestamps'}, inplace=True)
print len(tweetdf.index)

#wait time data
cursor.execute("SELECT * FROM recorded_dl_crowd_data")
wtrows = cursor.fetchall()
waitdf = pd.DataFrame( [[ij for ij in i] for i in wtrows] )
print len(waitdf.index)

#done importing so close SQL connection
conn.close() 

#bin tweets by hour in range
#bin wait times by hour in range
            

