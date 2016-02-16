#DISNEY CROWDS ANALYSIS

#Author: Elspeth Ready
#Date: 2016/01/30

#weather data scraped from wunderground.com using python's urllib; I grabbed ten years of hourly weather data from the Anaheim airport (that means ~3650 csv files adding up to ~11MB of data):
#here is the python code for that:
#import urllib
#import time
#import random

#for year in range(2006, 2017):
#    for month in range(1,13):
#        for day in range (1, 32):
#            urllib.urlretrieve("http://www.wunderground.com/history/airport/KFUL/%d/%d/%d/DailyHistory.html?req_city=Anaheim&req_state=CA&reqdb.zip=92801&reqdb.magic=1&reqdb.wmo=99999&format=1" %(year, month, day), "Anaheim_%d_%d_%d.csv" %(year, month, day))
#           time.sleep(random.uniform(1,3)) #randomize time delay between accessing pages so we don't get caught

        
#park attendance data is basically impossible to get from anyhwere, but I found a one month snapshot of data kindly collected by a redditor: https://www.reddit.com/user/cyiwin

#then after I used R to stuff all the data into a mysql database called "disney_db" that I use for the analysis (so I don't have to load all the data into R)

##############################


library(RMySQL)
con <- dbConnect(dbDriver("MySQL"), user = "root", password = "arctic", db="disney_db")


#First, let's look at the crowds at the two parks (Disneyland and California Adventure)

#CA data
crowdsCA <- dbGetQuery(con, "SELECT * FROM recorded_ca_crowd_data")
head(crowdsCA)
crowdsCA$time <- strptime(crowdsCA$time, "%Y-%m-%d %H:%M:%OS")
crowdsCA <- crowdsCA[-which(crowdsCA$hours_open < 0),]

#DL data
crowdsDL <- dbGetQuery(con, "SELECT * FROM recorded_dl_crowd_data")
for (i in 6:length(colnames(crowdsDL))) { #needs some cleaning
    crowdsDL[,i] <- replace(crowdsDL[,i], which(crowdsDL[,i]=="CL"), values=NA)
    crowdsDL[,i] <- as.numeric(crowdsDL[,i])
}
crowdsDL$time <- strptime(crowdsDL$time, "%Y-%m-%d %H:%M:%OS")

totalwaitDL <- apply(crowdsDL[,6:length(colnames(crowdsDL))], 1, sum, na.rm=TRUE)
totalwaitCA <- apply(crowdsCA[,6:length(colnames(crowdsCA))], 1, sum, na.rm=TRUE)
crowdsDL <- crowdsDL[-which(totalwaitDL <= 0),]
crowdsCA <- crowdsCA[-which(totalwaitCA <= 0),]

#create some metrics of total crowds using wait times across all open rides
meanwaitDL <- apply(crowdsDL[,6:length(colnames(crowdsDL))], 1, mean, na.rm=TRUE)
meanwaitCA <- apply(crowdsCA[,6:length(colnames(crowdsCA))], 1, mean, na.rm=TRUE)


#now model the crowds at each place based on temperature and whether it's not a work day 
library(timeDate)

#DL model
timesDL <- timeDate(as.character(crowdsDL$time))
holisDL <- isHoliday(timesDL, holidays = holidayNYSE()) #quick and dirty way to create a vector identifying non-business days
DLtemp1 <- crowdsDL$temperature
DLtemp2 <- (crowdsDL$temperature)^2
DLtime <- crowdsDL$time$hour
DLtime2 <- crowdsDL$time$hour^2
quadDL <- lm(meanwaitDL~DLtemp1+ DLtemp2 + DLtime + DLtime2 + holisDL) #polynomial regression model based on temp and holidays

newx1 <- seq(63,100, 0.1)
newx2 <- seq(63,100, 0.1)^2
newx3 <- as.logical(rep(0, length(newx1)))
newtime <- rep(14, length(newx1))
newtime2 <- sort(sample(8:23, length(newx1), replace=TRUE))
predDL1 <- predict.lm(quadDL, newdata=data.frame(DLtemp1 = newx1, DLtemp2 = newx2, DLtime=newtime, DLtime2=(newtime^2), holisDL=newx3), interval=c("prediction"), level = 0.95)
predDL2 <- predict.lm(quadDL, newdata=data.frame(DLtemp1 = rep(75, length(newtime2)), DLtemp2 = rep(75, length(newtime2))^2, DLtime=newtime2, DLtime2=(newtime2^2), holisDL=newx3), interval=c("prediction"), level = 0.95)


#CA model
timesCA <- timeDate(as.character(crowdsCA$time))
holisCA <- isHoliday(timesCA, holidays = holidayNYSE())
CAtemp1 <- crowdsCA$temperature
CAtemp2 <- (crowdsCA$temperature)^2
CAtime <- crowdsCA$time$hour
CAtime2 <- crowdsCA$time$hour^2
quadCA <- lm(meanwaitCA~CAtemp1+ CAtemp2 + CAtime + CAtime2 + holisCA)
predCA1 <- predict.lm(quadCA, newdata=data.frame(CAtemp1 = newx1, CAtemp2 = newx2, CAtime=newtime, CAtime2=(newtime^2), holisCA=newx3), interval=c("prediction"), level = 0.95)
predCA2 <- predict.lm(quadCA, newdata=data.frame(CAtemp1 = rep(75, length(newtime2)), CAtemp2 = rep(75, length(newtime2))^2, CAtime=newtime2, CAtime2=(newtime2^2), holisCA=newx3), interval=c("prediction"), level = 0.95)


#make a plot
png("crowdsvstemp.png", width = 8, height = 4.5, units = "in", pointsize = 7, res = 250)
par(mfrow=c(2,2), mar=c(4,4,3,1))
plot(crowdsDL$time$hour, meanwaitDL, pch=19, cex=0.5, main="Disneyland mean wait times (Fitted model + 95% P.I.)", ylab="Mean wait times across all open rides (min)", xlab="Time of day (24H)")
lines(newtime2,predDL2[,1], col="red",lwd=2)
lines(newtime2,predDL2[,2],col="red",lty=2)
lines(newtime2,predDL2[,3],col="red",lty=2)
plot(crowdsDL$temperature, meanwaitDL, pch=19, cex=0.5, main="Disneyland mean wait times (Fitted model + 95% P.I.)", ylab="Mean wait times across all open rides (min)", xlab="Temperature (F)")
lines(newx1,predDL1[,1], col="red",lwd=2)
lines(newx1,predDL1[,2],col="red",lty=2)
lines(newx1,predDL1[,3],col="red",lty=2)
plot(crowdsCA$time$hour, meanwaitCA, pch=19, cex=0.5, main="California Adventure mean wait times (Fitted model + 95% P.I.)", ylab="Mean wait times across all open rides (min)", xlab="Time of day (24H)")
lines(newtime2,predCA2[,1], col="blue",lwd=2)
lines(newtime2,predCA2[,2],col="blue",lty=2)
lines(newtime2,predCA2[,3],col="blue",lty=2)
plot(crowdsCA$temperature, meanwaitCA, pch=19, cex=0.5, main="California Adventure mean wait times (Fitted model + 95% P.I.)", ylab="Mean wait times across all open rides (min)", xlab="Temperature (F)")
lines(newx1,predCA1[,1], col="blue",lwd=2)
lines(newx1,predCA1[,2],col="blue",lty=2)
lines(newx1,predCA1[,3],col="blue",lty=2)
dev.off()


#now let's look at the Anaheim weather data and make some predictions about busy days in the past 10 years based on our simple model
AHweather <- dbGetQuery(con, "SELECT TemperatureF, PrecipitationIN, DateUTC FROM Anaheim_weather")
AHweather$DateUTC <- strptime(AHweather$DateUTC, "%Y-%m-%d %H:%M:%OS")
AHweatheroriginal <- AHweather
AHweather <- AHweather[which(AHweather$DateUTC$hour > 8 & AHweather$DateUTC$hour < 21),]

                
#organize the data, fix some NAs etc
AHweather$holidatesAH <- isHoliday(timeDate(AHweather$DateUTC), holidays=holidayNYSE()) #again a vector assigning holidays
AHweather$TemperatureF[which(AHweather$TemperatureF == -9999)] <- NA
AHweather <- AHweather[order(AHweather$DateUTC),]
AHweather$PrecipitationIN <- as.numeric(replace(AHweather$PrecipitationIN, which(AHweather$PrecipitationIN=="N/A"), values=NA))
AHweather$hour <- AHweather$DateUTC$hour


#consider only august dates because our model is not well-defined outside of that
AHweatherAS <- AHweather[which(AHweather$DateUTC$mon > 6 & AHweather$DateUTC$mon < 8),]

#create model predictions
pred10yCAonly <- predict.lm(quadCA, newdata=data.frame(CAtemp1 = AHweatherAS$TemperatureF, CAtemp2 = (AHweatherAS$TemperatureF)^2, holisCA=AHweatherAS$holidatesAH, CAtime=AHweatherAS$hour), interval=c("prediction"), level = 0.95)
pred10yDLonly <- predict.lm(quadDL, newdata=data.frame(DLtemp1 = AHweatherAS$TemperatureF, DLtemp2 = (AHweatherAS$TemperatureF)^2, holisDL=AHweatherAS$holidatesAH, DLtime=AHweatherAS$hour), interval=c("prediction"), level = 0.95)
AHweatherAS$pred10yCAonly <- pred10yCAonly[,1]
AHweatherAS$pred10yDLonly <- pred10yDLonly[,1]


#plot
png("weatherpreds.png", width = 8, height = 5, units = "in", pointsize = 7, res = 250)
par(mar=c(3,4,3,1))
layout(matrix(c(1,2,3,4), 4, 1, byrow = TRUE), widths=c(1,1,1,1), heights=c(3,3,2,2.5))
plot(AHweather$DateUTC, AHweather$TemperatureF, type='l', lwd=0.25, ylim=c(30, 105), col="gray50", main="Temperature in Anaheim 2006-2013 (9am-9pm)", ylab="Temp (F)")
plot(AHweatherAS$DateUTC, pred10yCAonly[,1], type='n', ylim=c(-5,40), main="Modeled park wait times (August 2006-2013)", ylab="Mean wait time predictions (min)")
for (i in 106:115) {
    data <- AHweatherAS[which(AHweatherAS$DateUTC$year == i),]
    lines(data$DateUTC, data$pred10yCAonly, col=rgb(0,0,1,alpha=0.4))
    lines(data$DateUTC, data$pred10yDLonly, col=rgb(1,0,0,alpha=0.3))
}
legend(strptime("2015-04-09 23:00:00", "%Y-%m-%d %H:%M:%OS"), 39, legend=c("Disneyland", "California Adventure"), pch=19, col=c(rgb(1,0,0,alpha=0.3), rgb(0,0,1,alpha=0.4)), cex=0.75)
plot(AHweather$DateUTC, AHweather$PrecipitationIN, type='l', lwd=0.5, col="green4", ylab="Precipitation (In)", main="Precipitation")
data2007 <- AHweatherAS[which(AHweatherAS$DateUTC$year == 108),]
        plot(data2007$DateUTC, data2007$pred10yCAonly, col=rgb(0,0,1), type='n', ylim=c(0,40), main="Modeled park wait times (August 2008 9am-9pm)", ylab="Mean wait time predictions (min)", pch=19, cex=0.25)
for (i in 1:31) {
    dataday <- data2007[which(data2007$DateUTC$mday== i),]
    lines(dataday$DateUTC, dataday$pred10yDLonly, col=rgb(1,0,0), cex=0.25, pch=19)
    lines(dataday$DateUTC, dataday$pred10yCAonly, col=rgb(0,0,1), cex=0.25, pch=19)
}
    legend(strptime("2008-08-30 12:00:00", "%Y-%m-%d %H:%M:%OS"), 39, legend=c("Disneyland", "California Adventure"), pch=19, col=c("red", "blue"),cex=0.75)
    dev.off()


#find the best days to go in the past 10 years based on the earlier models (not finished)
#bestdldays <- AHweather[-which(is.na(AHweather$pred10yDL)),]
#bestdldays <- bestdldays[-order(bestdldays$pred10yDL),]
#bestdldays[1:50,]
#bestcadays <- AHweather[order(AHweather$pred10yCA, na.last=NA),]
#bestdldays[length(bestdldays$pred10yDL)-50:length(bestdldays$pred10yCA),] #Sept27: hottest day on record LA
#bestcadays[1:50,]


#close out
rm(list=ls())
dbDisconnect(con)

