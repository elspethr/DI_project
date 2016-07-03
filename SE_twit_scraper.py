#Twitter scraper

#2016/02/14

#Description:
#code to scrape a twitter page without API; include scrolling to get entire search contents


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import urllib
import sys
import random
import time
import datetime
import re #regular expressions
from bs4 import BeautifulSoup
import MySQLdb


conn = MySQLdb.connect(host="localhost", port=3306, user="root", db="disney_db") #make db connection
cursor = conn.cursor() #mysqldb needs this

class Scraper:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://twitter.com" #I'm only scraping twitter, could pass this as an object instead
        self.verificationErrors = []
        self.accept_next_alert = True

    def process(self, search_term, location, distance, start_date, end_date):
        driver = self.driver
        delay = 3
        search_query=urllib.quote_plus("%s near:\"%s\" within:%dmi since:%d-%d-%d until:%d-%d-%d"%(search_term,
                                                                    location,
                                                                    distance,
                                                                    start_date["year"],start_date["month"],start_date["day"],
                                                                    end_date["year"],end_date["month"],end_date["day"]))
        url="%s/search?q=%s&src=typd"%(self.base_url,search_query)
        print "processing page:", url
        driver.get(url) #open the webpage I want to scroll
        for i in range(1,31): #scroll this number of times (get 20 tweets per scroll on twitter)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(1,3)) #sleep in between scrolls to look human
        html_source = driver.page_source
        data = html_source.encode('utf-8')
        #with open("testdate.txt", "wb") as f:
        #    f.write(data)  #write page html straight to file if needed (then could parse after)
        soup = BeautifulSoup(data, "html.parser")
        tweets = soup.find_all('li', 'js-stream-item') #yayyyy built-in functions
        for tweet in tweets:
            if tweet.find('p','tweet-text'):
                tweet_user = tweet.find('span','username').text.encode('utf8')
                tweet_text = tweet.find('p','tweet-text').text.encode('utf8')
                tweet_id = tweet['data-item-id'].encode('utf8')
                timestamp = tweet.find('a','tweet-timestamp')['title'].encode('utf8')
                tweet_timestamp = str(datetime.datetime.strptime(timestamp, '%I:%M %p - %d %b %Y')) #a bit hacky but works for now at least
                query = "INSERT INTO twitter_data (tweet_id, timestamp, user, text, search, location, distance) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                try: #try is for exception handling (Russian, etc.)
                    cursor.execute(query, (tweet_id, tweet_timestamp, tweet_user, tweet_text, search_term, location, distance))
                except:
                    tweet_text = ""
                    cursor.execute(query, (tweet_id, tweet_timestamp, tweet_user, tweet_text, search_term, location, distance))
                conn.commit() #commit each line in case something fails
        print "added", len(tweets), "tweets"
       
if __name__ == "__main__":
    scrap = Scraper()
    
    #now what we want to scrape is...
    searchterms = [("knott's berry farm", "buena park", 5)]#, [("ocean beach", "san francisco", 5)], ("great america", "santa clara", 5)]
    start = datetime.datetime.strptime("31-12-2014", "%d-%m-%Y")
    end = datetime.datetime.strptime("07-01-2016", "%d-%m-%Y")
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]

    print "start scraping!"
    #now get it!    
    for term, place, distance in searchterms:
        for date in date_generated:
            check = "SELECT * FROM completed_searches WHERE date=%s AND search=%s AND location=%s AND distance=%s"
            cursor.execute(check, (date, term, place, distance))
            if cursor.fetchone() != None: continue
            next_date = date + datetime.timedelta(days=1)
            #print term, place, date.year, date.month, date.day, next_date.year, next_date.month, next_date.day #test
            scrap.process(term, place, 5,
                            {"year":date.year, "month":date.month, "day":date.day}, 
                            {"year":next_date.year, "month":next_date.month, "day":next_date.day})
            completed = "INSERT INTO completed_searches (date, search, location, distance) VALUES (%s, %s, %s, %s)"
            cursor.execute(completed, (date, term, place, distance))
            conn.commit() #commit each line in case something fails

    scrap.driver.quit()
                   
conn.close() #close down SQL connection                   

#/search?q=disneyland%20near%3A%22disneyland%22%20within%3A5mi%20since%3A2015-08-01%20until%3A2015-09-30&src=typd" (my full query)
   
