import urllib
import time
import random

for year in range(2006, 2017):
    for month in range(1,13):
        for day in range (1, 32):
            urllib.urlretrieve("http://www.wunderground.com/history/airport/KFUL/%d/%d/%d/DailyHistory.html?req_city=Anaheim&req_state=CA&reqdb.zip=92801&reqdb.magic=1&reqdb.wmo=99999&format=1" %(year, month, day), "Anaheim_%d_%d_%d.csv" %(year, month, day))
            time.sleep(random.uniform(1,3)) #randomize time delay between accessing pages so we don't get caught

        
