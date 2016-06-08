#Crowd modeling proof of concept

#Created 2016/06/08

#Description:
#initial analysis of tweets for capstone project
#modeling correlation of tweets and wait times at two Disney theme parks

import datetime
import re #regular expressions
import MySQLdb
import pandas as pd

#get data from db
conn = MySQLdb.connect(host="localhost", port=3306, user="root", db="disney_db") #make db connection
cursor = conn.cursor()

#twitter data
tweetquery = "SELECT id, timestamp FROM twitter_data_copy WHERE location = 'anaheim' "
cursor.execute(tweetquery)

#waittime data
waitquery = "SELECT * FROM twitter_data_copy WHERE location = 'anaheim' "
cursor.execute(waitquery)


            
conn.close() 
