#DI Capstone Project

##Far from the madding crowd? Modeling crowding at outdoor parks

I am working on a project that deploys data for predicting crowds at outdoor recreation parks. In particular, I’m interested in deploying both weather data and historical use data for recreational sites to build a predictive model of park use.

This is an important application because:

(1) Users care about crowds: they want to avoid delays and long lines, and to maximize their enjoyment of their recreation time (and they may be willing to pay more to avoid delays!)

(2) Government cares about crowds: they want to deploy public transportation efficiently and avoid traffic congestion, etc. 

(3) Companies care about crowds: they want to maximize profit by providing services efficiently, they want to improve user experience, and they may want to take advantage of advertising opportunities! 

Eventually I plan to set up an interactive website that provides summaries of historical use data of several major parks in San Francisco, based on location-tagged twitter data, and possibly with some forecasting using weather forecasting. But prior to that I need to prove that twitter feeds correlate with how busy outdoor parks are. So, I’m first working on a test case for which I could get some ground truth data about actual attendance: Disneyland and California Adventure theme parks in Anaheim. I was able to find some detailed ride wait time data recorded by a redditor (https://www.reddit.com/user/cyiwin) in August-September 2015. 

So far I have built two different webscrapers and scraped historical weather data for Anaheim and over 130000 location-tagged tweets mentioning Disneyland and California
Adventure. I’ve put all of this in a MySQL database—actually my twitter scraper feeds the scraped data right into my database, which is really convenient once it's working although tricky to implement! I’ve just started to work on building a model that will compare the actual wait time data with the twitter data.

In this repository, you'll find:
- a simple urllib scraper to get weather data (get\_weather_data.py)
- a more complex selenium/BeautifulSoup scraper to get twitter data and port it to my MySQL database (SE\_twit_scraper.py)
- an R file that tidies up the scraped weather data (clean\_weather_data.R)
- an R file conducting regression of the recorded wait times vs. historical weather data at Disneyland and California Adventure (pilot_analysis.R)
- beginnings of python script for a model that will compare the actual wait time data with the twitter data (twitter_model.py) 
