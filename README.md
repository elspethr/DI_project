#DI Capstone Project

##Far from the madding crowd? Modeling crowding at outdoor parks

I am working on a project that uses twitter and weather data to develop a predictive model of outdoor recreational park usage. 

**View the website (in development) at:  [put heroku url here]**

This is an important application because:
- Users care about crowds: they want to avoid delays and long lines, and to maximize their enjoyment of their recreation time (and they may be willing to pay more to avoid delays!)
- Government cares about crowds: they want to deploy public transportation efficiently and avoid traffic congestion, etc. 
- Companies care about crowds: they want to maximize profit by providing services efficiently, they want to improve user experience, and they may want to take advantage of advertising opportunities! 

Eventually I plan to set up an interactive website that provides summaries of historical use data of several major parks in San Francisco, based on location-tagged twitter data, and that produces predictions of park use in the near using weather forecasting. However, prior to that I need to prove that twitter feeds correlate with how busy outdoor parks are. So, I’m first working on a test case for which I could get some ground truth data about actual attendance: Disneyland and California Adventure theme parks in Anaheim. I was able to find some detailed ride wait time data recorded by a redditor (https://www.reddit.com/user/cyiwin) in August-September 2015. 

So far I have built two different webscrapers and scraped historical weather data for Anaheim and over 130000 location-tagged tweets mentioning Disneyland and California Adventure. I’ve put all of this in a MySQL database—actually my twitter scraper feeds the scraped data right into my database, which is really convenient once it's working although tricky to implement!

I am currently working on building machine learning models with my training data and constructing the website.

**In this repository, you'll find:""
- a simple urllib scraper to get weather data (https://github.com/elspethr/DI_project/blob/master/get_weather_data.py)
- a more complex selenium/BeautifulSoup scraper to get twitter data and port it to a MySQL database (https://github.com/elspethr/DI_project/blob/master/SE_twit_scraper.py)
- an R file that tidies up the scraped weather data (https://github.com/elspethr/DI_project/blob/master/clean_weather_data.R)
- an R file conducting regression of the recorded wait times vs. historical weather data at Disneyland and California Adventure (https://github.com/elspethr/DI_project/blob/master/pilot_analysis.R)
- beginnings of python script for a model that will compare the actual wait time data with the twitter data (https://github.com/elspethr/DI_project/blob/master/twitter_model.py)

**A second repository (https://github.com/elspethr/DI_app) contains the materials for the project website.**
