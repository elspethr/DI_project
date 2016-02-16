#Twitter scraper

#2016/02/14

#Description:
#remember to source ~/.bashrc before running to get correct version of python on my mac
#code to scrape a twitter page without API; include scrolling to get entire search contents
#this code modified from http://stackoverflow.com/questions/28871115/, with some help

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
        for i in range(1,3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(2,5))
        html_source = driver.page_source
        data = html_source.encode('utf-8')
        #with open("%s.txt"%(output_name), "wb") as f:
        #    f.write(data)
        soup = BeautifulSoup(data, "html.parser")
        tweets = soup.find_all('li', 'js-stream-item')
        tweet_text = soup.find_all('p', 'js-tweet-text')
        print tweet_text[1]
        tweet_timestamps = soup.find_all('a', 'tweet-timestamp')
        print tweet_timestamps[1]
        for i in range(0, len(tweet_text)):
            text = tweets[i].contents[1]#get_text().encode('ascii', 'ignore')
            timestamp = tweet_timestamps[i]["title"]
            #print(i, timestamp, text)


        #tweettext = soup('p', {'class': ''})
        #tweetid = tweettext[0]
        #datetext = soup('p', {'class': 'tweet-timestamp js-permalink js-nav js-tooltip'})
        #date = datetext[0]
        #messagetext = soup('p', {'class': 'TweetTextSize  js-tweet-text tweet-text'})
        #message = messagetext[0]
        #print (username, "\n", "@", userhandle, "\n", "\n", url, "\n", "\n", message, "\n", "\n", retweetcount, "\n", "\n", favcount) #extra linebreaks for ease of reading

if __name__ == "__main__":
    scrap = Scraper()
    scrap.process("golden gate", "san francisco",
                    {"year":2015,"month":7,"day":5},
                    {"year":2015,"month":7,"day":7})

#/search?q=disneyland%20near%3A%22disneyland%22%20within%3A15mi%20since%3A2015-08-01%20until%3A2015-09-31&src=typd") my real query for later
   
