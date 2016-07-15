#DI Capstone Project

##Far from the madding crowd? Modeling crowding at outdoor parks

I am working on a project that uses twitter and weather data to develop predictive models of outdoor recreational park usage. For this project I take advantage of the fact that social media posts can track crowds, and that crowds at outdoor parks are correlated with weather.

**For more background information view the website at: http://madcrowds.herokuapp.com/**

This is an important application because:
- Users care about crowds at parks: they want to avoid delays and long lines, and to maximize their enjoyment of their recreation time (and they may be willing to pay more to avoid delays!)
- Government cares about crowds: they want to deploy public transportation efficiently and avoid traffic congestion, etc. 
- Companies care about crowds: they want to maximize profit by providing services efficiently, they want to improve user experience, and they may want to take advantage of advertising opportunities! 

To create a dataset for this project I built two different webscrapers and scraped historical weather data for Anaheim and over 160000 location-tagged tweets mentioning Disneyland, California Adventure and Universal Studios. I have built some basic machine learning models for Disneyland and California Adventure with these data, and I am currently working on developing more sophisticated time series models as well as adding more parks.

**In this repository, you'll find:**
- a simple urllib scraper to get weather data (https://github.com/elspethr/DI_project/blob/master/get_weather_data.py)
- a more complex selenium/BeautifulSoup scraper to get twitter data and port it to a MySQL database (https://github.com/elspethr/DI_project/blob/master/SE_twit_scraper.py)
- an R file that tidies up the scraped weather data (https://github.com/elspethr/DI_project/blob/master/clean_weather_data.R)
- an R file conducting regression of the recorded wait times vs. historical weather data at Disneyland and California Adventure, based on a small sample of ride wait time data recorded by a redditor in August-September 2015.  (https://github.com/elspethr/DI_project/blob/master/pilot_analysis.R)
- a python script that builds a model of hourly tweets for the two parks  (https://github.com/elspethr/DI_project/blob/master/hourly_twitter_model.py)
- a python script that builds a model of daily tweets for the two parks  (https://github.com/elspethr/DI_project/blob/master/fiveday_twitter_model.py)
- a python script that does some exploratory neural network analysis of the hourly data (unfinished!!!)  (https://github.com/elspethr/DI_project/blob/master/hourly_twitter_model_neural.py)

**A second repository (https://github.com/elspethr/DI_app) contains the materials for the project website.**
