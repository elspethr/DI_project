
#get MySQL connection
library(RMySQL)
con <- dbConnect(dbDriver("MySQL"), user = "root", password = "arctic", db="disney_db")

#create empty dataframe
getnames <- read.csv("Anaheim_2006_1_1.csv", header=TRUE, stringsAsFactors = FALSE)
Anaheim_weather <- as.data.frame(matrix(data=NA, nrow=0, ncol=length(colnames(getnames))))
colnames(Anaheim_weather) <- colnames(getnames)


#cycle over all years to create single data frame
for (year in 2006:2016) {
    for (month in 1:12) {
        for (day in 1:31) {
            filename <- paste("Anaheim_", year, "_", month, "_", day, ".csv", sep="")
            if (file.exists(filename)){
                temp <- read.csv(filename, header=TRUE, stringsAsFactors = FALSE)
                colnames(temp) <- colnames(Anaheim_weather)
                Anaheim_weather <- rbind(Anaheim_weather, temp)
            }
        }
    }
    print(year)
}

#clean up
colnames(Anaheim_weather)[14] <-  "DateUTC"
time <- strsplit(Anaheim_weather$DateUTC, "<")
time <- unlist(lapply(time, function(l) l[[1]]))
Anaheim_weather$DateUTC <- time

#export to MySQL
dbWriteTable(con, "Anaheim_weather", Anaheim_weather)
#dbSendQuery(con, "load data infile 'YWB_airport.csv' into table YWB_airport fields terminated by ','") #To write into existing table

#don't hold all that data here
rm(list=ls())
dbDisconnect(con)
