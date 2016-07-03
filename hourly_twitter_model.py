#load packages and data
import datetime
import holidays
import MySQLdb
import pandas.io.sql as sql
import pandas as pd
import numpy as np
import scipy.stats
import sklearn as sk
from sklearn import preprocessing, cross_validation, linear_model, neighbors, feature_extraction, grid_search, pipeline, metrics, ensemble
import dill
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

#now bin tweets by hour
tweetdf['hod'] = [datetime.datetime(dt.year, dt.month, dt.day, dt.hour) for dt in tweetdf.timestamps]
tweetdf['hour'] = [dt.hour for dt in tweetdf.timestamps]
tweetdftrim = tweetdf[tweetdf.hour >= 8]
tweetdftrim = tweetdftrim[tweetdftrim.hour <= 22]
tweets_per_hour = pd.DataFrame(tweetdftrim.groupby(['search','hod'])['user'].count()).reset_index()

#import weather data
cursor.execute("SELECT TemperatureF, Wind_SpeedMPH, PrecipitationIN, Conditions, DateUTC FROM anaheim_weather WHERE DateUTC > '2014-12-30'")
wrows = cursor.fetchall()
weatherdf = pd.DataFrame( [[ij for ij in i] for i in wrows] )
weatherdf.rename(columns={0: 'temp', 1:'wind', 2:'precip', 3:'conditions', 4:'datetimeUTC'}, inplace=True)

#fix time zone on weather data and process
weatherdf['datetimeUTC'] =  pd.to_datetime(weatherdf['datetimeUTC'], format='%Y-%m-%d %H:%M:%S.')
weatherdf['timestamp'] = weatherdf['datetimeUTC'] - datetime.timedelta(hours=8)
weatherdf['hod'] = [datetime.datetime(dt.year, dt.month, dt.day, dt.hour) for dt in weatherdf.timestamp] 
weatherdf.wind.replace(-9999.0, float('NaN'), inplace=True)
weatherdf.temp.replace(-9999.0, float('NaN'), inplace=True)
hourly_weather = pd.DataFrame(weatherdf.groupby(['hod']).agg({'temp': np.nanmean, 'wind': np.nanmean, 'conditions': 'first'})).reset_index()

#join weather and twitter data
tweetwaits = pd.merge(tweets_per_hour, hourly_weather, on='hod')

#get business days and holidays
tweetwaits['business_day'] = [dt.weekday() >= 5 for dt in tweetwaits.hod]
us_holidays = holidays.UnitedStates()
tweetwaits['holiday'] = [day in us_holidays for day in tweetwaits.hod]

#close SQL connection
conn.close()



#prep data for modelling

#one hot encoding
result = pd.concat([tweetwaits, pd.get_dummies(tweetwaits.search), pd.get_dummies(tweetwaits.conditions)], axis=1)
result.reset_index(inplace=True)
result.drop('index', axis=1, inplace=True)
result = result.dropna()

#parks: KNOTT'S BERRY FARM, LEGOLAND CALIFORNIA RESORT (CALRSBAD), UNIVERSAL STUDIOS (HOLLYWOOD)
CAm2 = 67.
DLm2 = 85.
KNm2 = 160.
LGm2 = 128.
USm2 = 415.

result['size'] = np.where(result['search']=='Disneyland', 85, 67)
result['tweetsperacre'] = result['user']/ result['size']

#add squares of hod, temp, and wind
result['hour'] = [dt.hour for dt in result.hod]
result['temp2'] = result['temp']**2
result['hour2'] = result['hour']**2
result['wind2'] = result['wind']**2

#export hourly averages for comparison
hourly_averages = pd.DataFrame(result.groupby(['hour', 'search']).agg({'user':np.mean, 'size': 'first'})).reset_index()
hourly_averages['peracre'] = hourly_averages['user']/hourly_averages['size']
hourly_averages.drop(['user', 'size'], axis=1, inplace=True)
hour_averages = hourly_averages.T.to_dict().values()
dill.dump(hour_averages, open('hourly_averages.pkl', 'w'))

#data for running the model
result.drop(['conditions', 'search'], axis=1, inplace=True)
data = result.T.to_dict().values()
y = result.tweetsperacre.as_matrix()



#model definition

#define scikit learn classes
class ColumnSelector(sk.base.BaseEstimator, sk.base.TransformerMixin):
    def __init__(self, column_names): #initialize
        self.column_names = column_names

    def fit(self, X, y=None): #fit the transformation, optional here
        return self

    def transform(self, X):
        return [[x[column] for column in self.column_names] for x in X]

linpredictors = ['Clear', 'Fog', 'Haze', 'Heavy Rain', 'Light Rain', 
                 'Mostly Cloudy', 'Overcast', 'Partly Cloudy', 'Rain', 'Scattered Clouds', 
                 'business_day', 'California Adventure', 'Disneyland', 'holiday', 'hour', 
                 'hour2', 'temp', 'temp2', 'wind', 'wind2']
    
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

        #X_ensemble = pd.DataFrame({
        #    "NEAR": self.nearest_neighbors.predict(X),
        #    "FOREST": self.random_forest.predict(X),
        #    "LINEAR": self.linear_regression.predict(X),
        #})
        
        near=self.nearest_neighbors.predict(X)
        forest=self.random_forest.predict(X)
        linear=self.linear_regression.predict(X)
        X_ensemble=[[near[i],forest[i],linear[i]] for i in range(len(X))]

        self.ensemble_regression = linear_model.LinearRegression().fit(X_ensemble, y)
        return self
    
    def predict(self, X):
        #X_ensemble = pd.DataFrame({
        #    "NEAR": self.nearest_neighbors.predict(X),
        #    "FOREST": self.random_forest.predict(X),
        #    "LINEAR": self.linear_regression.predict(X),
        #})

        near=self.nearest_neighbors.predict(X)
        forest=self.random_forest.predict(X)
        linear=self.linear_regression.predict(X)
        X_ensemble=[[near[i],forest[i],linear[i]] for i in range(len(X))]

        return self.ensemble_regression.predict(X_ensemble)


      
#run the model

#nbrs=100
#samples=57
#nestedreg = pipeline.Pipeline([('colsel', ColumnSelector(linpredictors)),
#                               ('est', EnsembleRegressor(nbrs, samples))])  
#parameters = dict(est__nbrs=range(90,122,3), est__samples=range(30,70,3))
#nested_cv = sk.grid_search.GridSearchCV(nestedreg, param_grid=parameters)
#nested_cv.fit(data, y)
#print nested_cv.best_params_
#print nested_cv.score(data, y)    

#use good params
nbrs = 117
samples = 51
tweet_reg = pipeline.Pipeline([('colsel', ColumnSelector(linpredictors)),
                               ('est', EnsembleRegressor(nbrs, samples))])  

#cross validate
loo = cross_validation.KFold(len(y), 100, shuffle=True)
scores = cross_validation.cross_val_score(tweet_reg, data, y, cv=loo)
print scores.mean()

#finalize
tweet_reg.fit(data,y)
print tweet_reg.score(data, y)
dill.dump(tweet_reg, open('hourly_model.pkl', 'w'))




