#Twitter scraper

#2016/02/14

#Description:
#remember to source ~/.bashrc before running to get correct version of python on my mac
#code to scrape a twitter page without API; include scrolling to get entire search contents
#this code modified from http://stackoverflow.com/questions/28871115/

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

conn = MySQLdb.connect(host="localhost", port=3306, user="root", db="disney_db")
cursor = conn.cursor()

class Scraper:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://twitter.com"
        self.verificationErrors = []
        self.accept_next_alert = True

    def process(self, search_term, location, start_date, end_date):
        driver = self.driver
        delay = 3
        search_query=urllib.quote_plus("%s near:\"%s\" within:15mi since:%d-%d-%d until:%d-%d-%d"%(search_term,
                                                                    location,
                                                                    start_date["year"],start_date["month"],start_date["day"],
                                                                    end_date["year"],end_date["month"],end_date["day"]))
        url="%s/search?q=%s&src=typd"%(self.base_url,search_query)
        driver.get(url)
        for i in range(1,2):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(2,5))
        html_source = driver.page_source
        data = html_source.encode('utf-8')
        #with open("testdate.txt", "wb") as f:
        #    f.write(data)  #write text straight to file if needed
        soup = BeautifulSoup(data, "html.parser")
        tweets = soup.find_all('li', 'js-stream-item')
        for tweet in tweets:
            if tweet.find('p','tweet-text'):
                tweet_user = tweet.find('span','username').text.encode('utf8')
                tweet_text = tweet.find('p','tweet-text').text.encode('utf8')
                tweet_id = tweet['data-item-id'].encode('utf8')
                timestamp = tweet.find('a','tweet-timestamp')['title'].encode('utf8')
                tweet_timestamp = str(datetime.datetime.strptime(timestamp, '%I:%M %p - %d %b %Y')) #this is poorly encoded but ok for now
                #print(tweet_id, tweet_user, tweet_timestamp, tweet_text)
                cursor.execute("INSERT INTO twitter_data (tweet_id, timestamp, user, text) VALUES (%s,%s,%s,%s)",(tweet_id, tweet_timestamp, tweet_user, tweet_text))
                conn.commit()
            else:
                continue
        driver.quit()

if __name__ == "__main__":
    scrap = Scraper()
    scrap.process("golden gate", "san francisco",
                    {"year":2015,"month":7,"day":5},
                    {"year":2015,"month":7,"day":7}) #run a test query

conn.close()                    

#/search?q=disneyland%20near%3A%22disneyland%22%20within%3A15mi%20since%3A2015-08-01%20until%3A2015-09-31&src=typd") my real query for later
   
