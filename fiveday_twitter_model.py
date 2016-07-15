#load packages and data
import datetime
import holidays
import MySQLdb
import pandas.io.sql as sql
import pandas as pd
import numpy as np
import scipy.stats
import sklearn as sk
from sklearn import cross_validation, preprocessing, linear_model, neighbors, feature_extraction, grid_search, pipeline, metrics, ensemble
import dill
import sys
dill.settings['recurse']=True


#get and organize data

#get current twitter data from db
conn = MySQLdb.connect(host="localhost", port=3306, user="root", db="disney_db") #make db connection
cursor = conn.cursor()
cursor.execute("SELECT id, user, timestamp, search, location FROM twitter_data_copy WHERE location = 'anaheim'")
rows = cursor.fetchall()
tweetdf = pd.DataFrame( [[ij for ij in i] for i in rows] )
tweetdf.rename(columns={0: 'tweetid', 1: 'user', 2: 'timestamps', 3: 'search', 4: 'location'}, inplace=True)
tweetdf.search = tweetdf.search.apply(lambda x: x.title())

tweetdf['dates'] = [str(dt.date()) for dt in tweetdf.timestamps]
#print len(tweetdf.search)
#print tweetdf[(tweetdf['search'] == 'Disneyland') & (tweetdf['dates'] =='2015-07-22')]
tweetdf.drop(tweetdf[(tweetdf['search'] == 'Disneyland') & (tweetdf['dates'] =='2015-07-17')].index, inplace=True)
#print tweetdf[(tweetdf['search'] == 'Disneyland') & (tweetdf['dates'] =='2015-07-17')]
#print tweetdf[(tweetdf['search'] == 'California Adventure') & (tweetdf['dates'] =='2015-07-22')]
tweetdf.drop('dates', axis=1, inplace=True)
#print len(tweetdf.search)

#now bin tweets by day
tweetdf['hour'] = [dt.hour for dt in tweetdf.timestamps]
tweetdftrim = tweetdf[tweetdf.hour >= 8]
tweetdftrim = tweetdftrim[tweetdftrim.hour <= 22]
tweetdftrim['day'] = [datetime.datetime(dt.year, dt.month, dt.day) for dt in tweetdftrim.timestamps]
tweets_per_day = pd.DataFrame(tweetdftrim.groupby(['search','day'])['user'].count()).reset_index()

#import weather data
cursor.execute("SELECT TemperatureF, Wind_SpeedMPH, PrecipitationIN, Conditions, Humidity, DateUTC FROM anaheim_weather WHERE DateUTC > '2014-12-30'")
wrows = cursor.fetchall()
weatherdf = pd.DataFrame( [[ij for ij in i] for i in wrows] )
weatherdf.rename(columns={0: 'temp', 1:'wind', 2:'precip', 3:'conditions', 4:'humidity', 5: 'datetimeUTC'}, inplace=True)
weatherdf['datetimeUTC'] =  pd.to_datetime(weatherdf['datetimeUTC'], format='%Y-%m-%d %H:%M:%S.')
weatherdf['timestamp'] = weatherdf['datetimeUTC'] - datetime.timedelta(hours=8)
weatherdf['day'] = [datetime.datetime(dt.year, dt.month, dt.day) for dt in weatherdf.timestamp]
weatherdf.wind.replace(-9999.0, float('NaN'), inplace=True)
weatherdf.temp.replace(-9999.0, float('NaN'), inplace=True)
weatherdf.precip.replace(-9999.0, float('NaN'), inplace=True)
weatherdf.humidity.replace(-9999.0, float('NaN'), inplace=True)
weatherdf.precip.replace('N/A', 0, inplace=True)
weatherdf.humidity.replace('N/A', float('NaN'), inplace=True)
weatherdf['precip'] = pd.to_numeric(weatherdf['precip'])
weatherdf['humidity'] = pd.to_numeric(weatherdf['humidity'])
weatherdf['lotemp'] = weatherdf['temp']
weatherdf = weatherdf.dropna()
daily_weather = pd.DataFrame(weatherdf.groupby(['day']).agg({'temp':np.max, 'lotemp':np.min, 'wind':np.nanmean, 'humidity':np.nanmean, 'precip':np.sum, 'conditions':scipy.stats.mode})).reset_index()

#join weather and twitter data
tweetwaits = pd.merge(tweets_per_day, daily_weather, on='day')

#get business days and holidays
tweetwaits['business_day'] = [dt.weekday() >= 5 for dt in tweetwaits.day]
us_holidays = holidays.UnitedStates()
tweetwaits['holiday'] = [day in us_holidays for day in tweetwaits.day]
tweetwaits['month'] = [dt.strftime('%B') for dt in tweetwaits.day]
result = tweetwaits.dropna()

#close SQL connection
conn.close()


#prep data for modelling
CAm2 = 67.
DLm2 = 85.
KNm2 = 160.
LGm2 = 128.
USm2 = 415.

result['size'] = np.where(result['search']=='Disneyland', 85, 67)
result['tweetsperacre'] = result['user']/result['size']

#add squares of hod, temp, and wind
result['dow'] = [dt.strftime('%A') for dt in result.day]
#result['dow'] = [dt.weekday() for dt in result.day]
#result['dow2'] = result['dow']**2
result['temp2'] = result['temp']**2
result['lotemp2'] = result['lotemp']**2
result['wind2'] = result['wind']**2

result['conditions'] = [str(x[0]).strip("[]'") for x in result['conditions']]
result = pd.concat([result, pd.get_dummies(result.conditions), pd.get_dummies(result.search), pd.get_dummies(result.month), pd.get_dummies(result.dow)], axis=1)
result.reset_index(inplace=True)
result.drop('index', axis=1, inplace=True)
result = result.dropna()

#export daily averages for comparison
daily_averages = pd.DataFrame(result.groupby(['dow', 'search']).agg({'user':np.mean, 'size':'first'})).reset_index()
daily_averages['peracre'] = daily_averages['user']/daily_averages['size']
daily_averages.drop(['user', 'size'], axis=1, inplace=True)
day_averages = daily_averages.T.to_dict().values()
dill.dump(day_averages, open('day_averages.pkl', 'w'))

#data for modeling
result.drop(['conditions', 'search'], axis=1, inplace=True)
data = result.T.to_dict().values()
y = result.tweetsperacre.as_matrix()

#print data[0]
#sys.exit()

#model definition

class ColumnSelector(sk.base.BaseEstimator, sk.base.TransformerMixin):
    def __init__(self, column_names): #initialize
        self.column_names = column_names

    def fit(self, X, y=None): #fit the transformation, optional here
        return self

    def transform(self, X):
        return [[x[column] for column in self.column_names] for x in X]
   

linpredictors = ['Clear', 'Haze', 'Heavy Rain', 'Light Rain', 'Mostly Cloudy', 'Overcast', 'Partly Cloudy', 
                 'business_day', 'California Adventure', 'Disneyland', 'holiday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
                 'Friday', 'Saturday', 'Sunday','temp', 'lotemp', 'wind', 'humidity', 'precip', 'January', 'February', 'March',
                 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


class EnsembleRegressor(sk.base.BaseEstimator, sk.base.RegressorMixin):
    """Joins a linear, random forest, and nearest neighbors model."""
    def __init__(self, nbrs, samples):
        self.nbrs = nbrs
        self.samples = samples
        pass
    
    def fit(self, X, y):
        self.linear_regression = linear_model.LinearRegression().fit(X, y)
        y_err = y - self.linear_regression.predict(X)

        self.nearest_neighbors = neighbors.KNeighborsRegressor(n_neighbors=self.nbrs).fit(X, y_err)
        self.random_forest = ensemble.RandomForestRegressor(min_samples_leaf=self.samples).fit(X, y_err)

        X_ensemble = pd.DataFrame({
            "NEAR": self.nearest_neighbors.predict(X),
            "FOREST": self.random_forest.predict(X),
            "LINEAR": self.linear_regression.predict(X),
        })
        self.ensemble_regression = linear_model.LinearRegression().fit(X_ensemble, y)
        return self
    
    def predict(self, X):
        X_ensemble = pd.DataFrame({
            "NEAR": self.nearest_neighbors.predict(X),
            "FOREST": self.random_forest.predict(X),
            "LINEAR": self.linear_regression.predict(X),
        })
        return self.ensemble_regression.predict(X_ensemble)


#run the model

#grid search
#nbrs = 5 
#samples = 5
#nestedreg = pipeline.Pipeline([('colsel', ColumnSelector(linpredictors)),
#                               ('est', EnsembleRegressor(nbrs, samples))])  

#parameters = dict(est__nbrs=range(110,130,1), est__samples=range(100,125,1))
#nested_cv = sk.grid_search.GridSearchCV(nestedreg, param_grid=parameters)
#nested_cv.fit(data, y)
#print nested_cv.best_params_
#print nested_cv.score(data, y)    


#final run with good params
nbrs = 126
samples = 106
tweet_reg = pipeline.Pipeline([('colsel', ColumnSelector(linpredictors)),
                               ('est', EnsembleRegressor(nbrs, samples))]) 

#cross-validation
loo = cross_validation.KFold(len(y), 10, shuffle=True)
scores = cross_validation.cross_val_score(tweet_reg, data, y, cv=loo)
print scores.mean()
tweet_reg.fit(data, y)
print tweet_reg.score(data, y)
dill.dump(tweet_reg, open('fiveday_model.pkl', 'w'))
