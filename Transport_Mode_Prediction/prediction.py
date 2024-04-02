import pandas as pd
from datetime import datetime
import json
import haversine as hs
from haversine import Unit
from os import listdir
import sys

def nearStation(stops, datapoint, precision):
    #returns the id of the stop within a 10m radius from the user. If there isn't any, returns false

    precisionLat = precision*0.0001/20      #calculates the latitude 
    precisionLon = precision*0.0002/20      #and longitude range from the precision

    userLat = datapoint["latitude"]
    userLon = datapoint["longitude"]

    stopsClose = stops[(stops["stop_lat"] < userLat + precisionLat) &   #filters the stops <10m away from the users position
                       (stops["stop_lat"] > userLat - precisionLat) &
                       (stops["stop_lon"] < userLon + precisionLon) &
                       (stops["stop_lon"] > userLon - precisionLon)]
    
    if stopsClose.shape[0]:                 #There is a stop near the user
        nearStop = stopsClose["stop_id"][stopsClose.index[0]]
    else:                                   #There is no stops near the user
        nearStop = False
    return nearStop

def hourToSeconds(hour):
    #converts an hour ("HH:MM:SS" format) to a number of seconds elapsed since midnight
    #used for the GTFS documentation and for the next function
    hms = hour.split(":")                                           #splits the format into hours, minutes and seconds
    seconds = int(hms[0]) * 3600 + int(hms[1]) * 60 + int(hms[2])   #converts it into seconds
    return seconds

def timeToSeconds(date):
    #converts a time ("YYYY/MM/DD HH:MM:SS.SSS+00" or "YYYY-MM-DDTHH:MM:SS.SSSZ") to a number of seconds elapsed since midnight
    #gets a GFT time and returns in Irish time
    time = date[11:].split(".")[0]
    seconds = hourToSeconds(time) + 3600        #adding an hour to account for time zones
    return seconds

def timeToSecondsBis(date):
    #converts a time ("Wed Jul 12 2023 01:17:37 GMT+0200 (heure d’été d’Europe centrale)" to a number of seconds elapsed since midnight
    #print(f"date : {date}")
    time = date[16:].split(" ")
    timeZone = int(time[1][4:6])
    if time[1][3]=="-" : timeZone *= -1
    seconds = hourToSeconds(time[0]) - (timeZone - 1) * 3600
    return seconds


def dayNumberWeek(date):
    #returns the number of the day in the week, monday being 0 and sunday 6
    #from a "YYYY/MM/DD HH:MM:SS.SSS+00" or "YYYY-MM-DDTHH:MM:SS.SSSZ" format
    day = date[:10]
    dateObject = datetime.strptime(day, '%Y-%m-%d')
    dayNumber = dateObject.weekday()
    return dayNumber

def dayNumberWeekBis(date):
    #returns the number of the day in the week, monday being 0 and sunday 6
    #from a "Wed Jul 12 2023 01:17:37 GMT+0200 (heure d’été d’Europe centrale)" format
    day = date[:3]
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dayNumber = days.index(day)
    return dayNumber

def dayNameWeek(date):
    #returns the name of the day in the week
    #from a "YYYY/MM/DD HH:MM:SS.SSS+00" or "YYYY-MM-DDTHH:MM:SS.SSSZ" format
    day = date[:10]
    dateObject = datetime.strptime(day, '%Y-%m-%d')
    dayNumber = dateObject.strftime('%A')
    return dayNumber.lower()

def convertDate(timeStamp):
    #returns the date in the right format (YYYY-MM-DD)
    #from a "Wed Jul 12 2023 01:17:37 GMT+0200 (heure d’été d’Europe centrale)" format
    month = [0, "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Sep", "Nov", "Dec"]
    date = timeStamp[11:15] + "-"

    if month.index(timeStamp[5:7]) < 10 : date += "0" 
    date += str(month.index(timeStamp[4:7])) + "-" + timeStamp[8:10]
    return date

def dayNameWeekBis(date):
    #returns the name of the day in the week
    #from a "Wed Jul 12 2023 01:17:37 GMT+0200 (heure d’été d’Europe centrale)" format
    day = convertDate(date)
    dateObject = datetime.strptime(day, '%Y-%m-%d')
    dayNumber = dateObject.strftime('%A')
    return dayNumber.lower()


def listServiceActive(dataTime, calendar):
    #returns a shortened version of the calendar dataframe, whithout the services not operating on that day
    dayName = dayNameWeek(dataTime)

    #print(f"---\n date : {dataTime} ----\n")
    #print(dataTime[:10])

    #date = int(convertDate(dataTime).replace("-", ""))
    date = int(dataTime[:10].replace("-", ""))  #modif 2024

    activeCalendar = calendar[(calendar[dayName] == 1) &            #checks if the service is active for this day in the week
                              (calendar["start_date"] <= date) &    #checks if the service is active for this time period
                              (calendar["end_date"] >= date)]
    return list(activeCalendar["service_id"])

def scheduleDelay(tripsAtThisStop, answer): 
    #returns the dataframe tripID/arrivalDelay/departureDelay for all the trips alvailable at the stop
    listeDateTrip = pd.DataFrame({"trip_id" : [],
                                  "arrival_delay" : [],
                                  "departure_delay" : []})                      #creates the dataframe
    dateTrip = [0, 0, 0]    
    for trip in answer["entity"]:
        if "trip_id" in trip["trip_update"]["trip"].keys():                     #these check if the attribute we are looking for is in the current object
            if trip["trip_update"]["trip"]["trip_id"] in list(tripsAtThisStop["trip_id"]):
                dateTrip[0] = trip["trip_update"]["trip"]["trip_id"]            #found information about this trip, storing its ID
                stopSequence = tripsAtThisStop[tripsAtThisStop["trip_id"]==dateTrip[0]].iloc[0]["stop_sequence"]
                numberStop = 0
                if "stop_time_update" in trip["trip_update"].keys():            #cf last comment
                    numberMaxStop = len(trip["trip_update"]["stop_time_update"])
                    while (trip["trip_update"]["stop_time_update"][numberStop]["stop_sequence"] < stopSequence) and  (numberStop < numberMaxStop - 1):  #checking if the current stop is mentioned for this trip
                        numberStop += 1
                    if ("arrival" in trip["trip_update"]["stop_time_update"][numberStop].keys() and 
                        "delay" in trip["trip_update"]["stop_time_update"][numberStop]["arrival"].keys()):
                        dateTrip[1] = trip["trip_update"]["stop_time_update"][numberStop]["arrival"]["delay"]   #found information about arrival delay, storing the delay in seconds
                    if ("departure" in trip["trip_update"]["stop_time_update"][numberStop].keys() and 
                        "delay" in trip["trip_update"]["stop_time_update"][numberStop]["departure"].keys()):
                        dateTrip[2] = trip["trip_update"]["stop_time_update"][numberStop]["departure"]["delay"] #found information about arrival delay, storing the delay in seconds
                    listeDateTrip.loc[len(listeDateTrip.index)] = dateTrip      #adds the retrieved data to the dataframe
    return listeDateTrip
            

def tripToRouteName(trip, routes, trips):
    #returns the tuple shortname, longname associated with a tripID, using the GTFS documentation
    routeID = trips[trips["trip_id"]==trip].iloc[0]["route_id"]
    busName = routes[routes["route_id"]==routeID].iloc[0]["route_short_name"]
    busNameLong = routes[routes["route_id"]==routeID].iloc[0]["route_long_name"]
    return busName, busNameLong

def numberStopsTheory(tripScore, stop_times):
    #for a trip, with a starting and ending stop, returns the number of stops passed by the bus in between
    stopIDStart = tripScore[2]
    stopIDEnd = tripScore[3]
    stopsOnTrip = stop_times[stop_times["trip_id"] == tripScore[0]]                     #filters only stopTimes on this trip
    minRank = stopsOnTrip[stopsOnTrip["stop_id"]==stopIDStart].iloc[0]["stop_sequence"] #gets the sequence number of the starting stop
    maxRank = stopsOnTrip[stopsOnTrip["stop_id"]==stopIDEnd].iloc[0]["stop_sequence"]   #gets the sequence number of the ending stop
    stopsOnUserTrip = stopsOnTrip[(stopsOnTrip["stop_sequence"] >= minRank) &
                                  (stopsOnTrip["stop_sequence"] <= maxRank)]            #filters the stops which sequence is between the starting and ending
    numberStopMax = stopsOnUserTrip.shape[0]
    return numberStopMax


def busAtStop(texte, stop, tripScore, APIresponse, stop_times, datapoint, routes, trips, APIcalled):
    #prints the name(s) of the bus at the stop near the user
    #returns 5 if it detects a bus, 0 if not
    #also updates the tripscores (see below)

    isOnBus = 0
    dataTime = datapoint["created"]
    dataSecond = timeToSeconds(dataTime) # Modif 2024 (enlevement du bis)
    #dayNumber = dayNumberWeek(dataTime)                 supposed to already be dropped in the initialisation
    #date = dataTime[:10].replace("-", "")

    tripsAtThisStop = stop_times[stop_times["stop_id"]==stop]

    if APIcalled : listeDateTrip = scheduleDelay(tripsAtThisStop, APIresponse)

    for i in list(tripsAtThisStop.index):               #for each trip stopping where the user is,
        
        tripID = tripsAtThisStop["trip_id"][i]

        arrivalTime = hourToSeconds(tripsAtThisStop["arrival_time"][i])
        departureTime = hourToSeconds(tripsAtThisStop["departure_time"][i])

        if (APIcalled) and (tripID in listeDateTrip["trip_id"]):          #adjusts for delay if there is information in the API
            arrivalTime += listeDateTrip[listeDateTrip["trip_id"]==tripID].iloc[0]["arrival_delay"]
            departureTime += listeDateTrip[listeDateTrip["trip_id"]==tripID].iloc[0]["departure_delay"]

        if ((arrivalTime - 120 < dataSecond)            #checks whether a bus is supposed to be there
            and (max(arrivalTime, 
                    departureTime) + 120 > dataSecond)):
            isOnBus = 5

            busName, busNameLong = tripToRouteName(tripID, routes, trips)
            if texte: print("    ", busName, busNameLong, tripsAtThisStop["arrival_time"][i])

            scored = 0                                  #keeping score of the specific trip
            j = 0
            nbScored = len(tripScore)
            while (j < nbScored) and (scored == 0):
                if (tripScore[j][0] == tripID):     #if the trip has already been met, increments its counter and updates its last stop met
                    scored = 1
                    if tripScore[j][3] != stop:
                        tripScore[j][1] += 1
                        tripScore[j][3] = stop
                j += 1
            if scored == 0:                         #if met for the 1st time, creates a line for it, with the 1st stop met
                tripScore.append([tripID, 1, stop, stop])
    return isOnBus, tripScore


def busScoring(userFile, APIcall=True, texte=False):
    #Data from the GTFS Schedule Reference (for further information, visit https://gtfs.org/schedule/reference/)
    GTFSfile = "GTFS_Dublin_Bus"
    stops = pd.read_csv(GTFSfile + "/stops.txt")                                 #stops.txt is a file containing the names of the stops as well as their coordinate
    stop_times = pd.read_csv(GTFSfile + "/stop_times.txt", low_memory=False)     #stop_times.txt is a file containing when the differents trips arrive at different stops
    routes = pd.read_csv(GTFSfile + "/routes.txt")                               #routes.txt is a file containing the information on transit routes. A route is a group of trips that are displayed to riders as a single service.
    trips = pd.read_csv(GTFSfile + "/trips.txt", low_memory=False)                                 #routes.txt is a file containing the information on trips for each route. A trip is a sequence of two or more stops that occur during a specific time period.
    calendar = pd.read_csv(GTFSfile + "/calendar.txt")                           #service dates specified using a weekly schedule with start and end dates. 

    userData = pd.read_csv(userFile)

    generalTime = userData["created"][0]

    activeServiceID = listServiceActive(generalTime, calendar)                              #removes the services which are not operating on that day
    activeTrips = trips[trips["service_id"].isin(activeServiceID)]                          #keeps only the trips operating on the services listed above
    activeStopTimes = stop_times[stop_times["trip_id"].isin(list(activeTrips["trip_id"]))]  #keeps only the stopTimes serviced by the trips listed above

    APIcalled = True

    dictTypeRoute = ["tramway", "subway", "DART", "bus"]                        #translates the type_route code to the transport type name (see GTFS documentation)

    tripScore = []                                  #stores the score of the different trips, to figure out which the user was most likely on. Could also show someone passing stops while in a car if no clear majorities
                                                    #the format is : [tripID, score, 1stStopID, lastStopID]
    if isinstance(APIcall, str):
        with open(APIcall, 'r') as file:
            APIresponse = json.load(file)
    else:
        APIresponse = False
        APIcalled = False

    precision = 30                              #number of meters from which the user will be considered at a station
    busScore = 0                                #bus score - the higher the more likely the user is on a bus
    #distTotale = 0                              #total distance travelled by the user, in meters

    listStopsVisit = []                                #keeps the id of the last stop, in order not to score more if the user is recorded multiple times at the same spot
    if texte: print("*******")
    for i in list(userData.index):
        """if i > 0:
            distLocal = hs.haversine((userData["latitude"][i],userData["longitude"][i]),(userData["latitude"][i - 1],userData["longitude"][i - 1]), unit=Unit.METERS)
            distTotale += distLocal"""
        datapoint = userData.iloc[i]
        nearStop = nearStation(stops, datapoint, precision)         #gets the stopID of the nearest station from the user
        if nearStop and not(nearStop in listStopsVisit):                       #if there isn't a near stop, then the user is either between two stops or not on a route. We wait until the user gets to a stop.
            if texte: print(stops[stops["stop_id"] == nearStop].iloc[0]["stop_name"])
            busScoreTemp, tripScore = busAtStop(texte, nearStop, tripScore, APIresponse, activeStopTimes, datapoint, routes, activeTrips, APIcalled)
            busScore += 1 + busScoreTemp
            listStopsVisit.append(nearStop)
    #APIrequest()
    if texte: print("*******")

    maxScoreTrip = 0
    maxTrip = -1
    for n, trip in enumerate(tripScore):
        if trip[1] > maxScoreTrip:
            maxScoreTrip = trip[1]
            maxTrip = trip[0]
            scoreTripID = n
    
    returnText = ""

    if maxTrip == -1:
        returnText = "The user most likely has driven on this trip"
        busScore = 0
        routeType = 'transport'
        routeTypeID = 4
    else :                  #nonsense to print a nice summary
        busName, busNameLong = tripToRouteName(maxTrip, routes, trips)
        routeTypeID = routes[routes["route_short_name"]==busName].iloc[0]["route_type"]
        routeType = dictTypeRoute[routeTypeID]
        returnText = "The most likely {} taken is {} {} which was met {} times\n".format(routeType, busName, busNameLong, maxScoreTrip)
        numberStopMax = numberStopsTheory(tripScore[scoreTripID], activeStopTimes)
        returnText += "The user has likely taken this {} for {} stops,\n".format(routeType, numberStopMax)
        stopStartID = tripScore[scoreTripID][2]
        stopStart = stops[stops["stop_id"]==stopStartID].iloc[0]["stop_name"]
        stopEndID = tripScore[scoreTripID][3]
        stopEnd = stops[stops["stop_id"]==stopEndID].iloc[0]["stop_name"]
        returnText += "from {} to {}.\n".format(stopStart, stopEnd)
        if numberStopMax == 0:
            busScore = 0
        else:
            busScore = busScore * maxScoreTrip / numberStopMax
    return busScore, (routeTypeID + 3), returnText

def SACalculator(userData, i, isSpeed):
    #calculates the speed (if isSpeed = True) or the acceleration between two datapoints, in either km/h or km/h
    if isSpeed:
        distancePts = hs.haversine((userData["latitude"][i],userData["longitude"][i]),
                                   (userData["latitude"][i + 1],userData["longitude"][i + 1]),
                                   unit=Unit.METERS) / 1000
    else:
        distancePts = userData["speed"][i + 1] - userData["speed"][i]

    diffTimePts = float(timeToSeconds(userData["created"][i + 1]) - timeToSeconds(userData["created"][i])) / 3600.0
    if diffTimePts != 0.0:
            locSpeed = (distancePts / diffTimePts)
    else:
        locSpeed = 0
    return locSpeed

def likelihoodCalc(userSpeed, WCOodds):
    #returns the likelihood the user is walking, cycling or other, using his speed
    if userSpeed > 46:
        userSpeed = 46

    #roundSpeed = int(round(userSpeed/2, 0)*2)
    roundSpeed = (userSpeed // 4) * 4

    Wodds = WCOodds[WCOodds["speed"]==roundSpeed].iloc[0]["walk"]  / 100
    Codds = WCOodds[WCOodds["speed"]==roundSpeed].iloc[0]["cycle"] / 100
    Oodds = WCOodds[WCOodds["speed"]==roundSpeed].iloc[0]["other"] / 100
    likely = [Wodds, Codds, Oodds]
    return likely

def speedScoring(userFile, selection, texte=False):
    #returns various informations from the user's trip, including on speed and acceleration : mostly to separate walking, cycling from bus/car/train
    #selection is the transport mode selected by the user, with 0 = walking, 1 = cycling and 2 = other (bus, car, train...)
    if selection > 2:
        selection = 2
    userData = pd.read_csv(userFile)                            #GPS data collected from the user
    if userData.shape[0] > 4:
        WCOodds = pd.read_csv("probability_WCO.txt")  #calculated odds of using a transport mode at a given speed
        baseOdds = [[0.50, 0.25, 0.25],                             #starting odds based on the selection
                    [0.25, 0.50, 0.25],
                    [0.25, 0.25, 0.50]]
        
        ptSpeed = [SACalculator(userData, i, True) for i in userData.index[:-1]]        #calculates the speed
        ptSpeed.append(ptSpeed[-1])

        userData["speed"] = ptSpeed

        ptAcceleration = [SACalculator(userData, i, False) for i in userData.index[:-1]]#calculates the acceleration
        ptAcceleration[-1] = ptAcceleration[-2]
        ptAcceleration.append(ptAcceleration[-1])

        userData["acceleration"] = ptAcceleration

        

        time = [round(timeToSeconds(userData["created"][i]), -2) for i in userData.index]
        print("user index : ", userData.index)
        userData["time"] = time
        userDataClean = userData.drop(columns = ["created"])
        userDataAvg = userDataClean.groupby(["time"]).mean()

        priorOdds = baseOdds[selection]
        for i in userDataAvg.index:
            likelyOdds = likelihoodCalc(userDataAvg["speed"][i], WCOodds)
            print("userDataAvg : ", userDataAvg["speed"][i])
            norm = likelyOdds[0]*priorOdds[0] + likelyOdds[1]*priorOdds[1] + likelyOdds[2]*priorOdds[2]
            postOdds = [likelyOdds[j] * priorOdds[j] / norm for j in range(3)]
            print("round : ", [round(postOdds[i], 3) for i in range(3)])
            print("")
            priorOdds = postOdds
        finalOdds = [round(postOdds[i], 3) for i in range(3)]
    else:
        finalOdds = ["error"]
    return finalOdds

def generalScoring(dataFile):
    #creats a dataframe with the scoring for all data files, I'm using it to calibrate the scores
    dict = ["bus", "car", "walk", "train"]      #0 : Bus, 1 : car, 2 : walk, 3 : train
    training = pd.DataFrame({"trip_type" : [],
                        "bus_score" : [],
                        "walk" : [],
                        "bike" : [],
                        "other" : [],
                        "speed" : []})
    for userfileName in listdir(dataFile):
        if ((userfileName[-4:] == ".csv") and (userfileName[:-5]=="bus" or userfileName[:-5]=="car")):
            tripType = dict.index(userfileName[:-5])
            userFile = dataFile + "/" + userfileName
            userDataAvg, odds, isCorrect, avgSpeed = speedScoring(userFile, 2, texte=False)
            walking = odds[0]
            cycling = odds[1]
            othering = odds[2]
            score = busScoring(userFile, APIcall=False, texte=False)
            trainingFile = [tripType, score, walking, cycling, othering, avgSpeed]
            training.loc[len(training.index)] = trainingFile
    print(training.head(15))
    training.to_csv("generalScoring.csv")
    return 1

def main(userFile, apiCall):
    #main function that will be called in the back, with userFile string containing the GPS data from the front,
    #and userSelect the transport mode selectec by the user, with : 0 = walking, 1 = cycling, 2 = car, 3 = tramway, 4 = subway, 5 = DART, 6 = bus
    #frontToBack = [0, 2, 3, 0, 1]
    #backToFront = [3, 4, 1, 2]
    busText = ""
    #userSelect = frontToBack[userSelection]
    #transportChecked = userSelect
    odds = speedScoring(userFile, 1, texte=False)
    print(odds)
    if odds[0]== "error":
        finalText = "Too few datapoints, unable to process"
    else :
        if (odds[2] > 0.3):
            score, transportType, finalText = busScoring(userFile, APIcall=apiCall, texte=False)
            print(score)
            if score >= 10:
                transportChecked = 3
            else:
                if odds[2] > odds[1]:
                    transportChecked = 2
                else:
                    transportChecked = 1
        else:
            if odds[1] < odds[0]:
                transportChecked = 0
                finalText = "The user most likely has walked on this trip"
            else :
                transportChecked = 1
                finalText = "The user most likely has cycled on this trip"
    return finalText

userFile = sys.argv[1]
APIcalling = False
if APIcalling=="false" : APIcalling = False

print(main(userFile, APIcalling))