import React, {useContext, useState} from "react";

import * as TaskManager from 'expo-task-manager';
import * as Location from 'expo-location';


const LOCATION_TASK_NAME     = 'background-location-task';
const LOCATION_TIME_INTERVAL = 15000;

const gpsData = [];

TaskManager.defineTask(LOCATION_TASK_NAME, ({ data: { locations }, error }) => {
    if (error) {
        console.error(error);
        return;
    }
    console.log(locations.length, "new locations available");

    locationService.setLocation(locations);

});

const LocationService = () => {
    let subscribers = []

    return {
        subscribe: (sub) => subscribers.push(sub),

        setLocation: (newLocation) => {
            newLocation.forEach((e) => gpsData.push(e));
            subscribers.forEach((sub) => sub(newLocation));
        },

        unsubscribe: (sub) => {
            subscribers = subscribers.filter((_sub) => _sub !== sub)
        },


        startService: async () => {
            await Location.startLocationUpdatesAsync(LOCATION_TASK_NAME, {
                accuracy: Location.Accuracy.BestForNavigation,
                deferredUpdatesDistance: 0,

                timeInterval: LOCATION_TIME_INTERVAL,
                distanceInterval: 0,

                deferredUpdatesInterval: LOCATION_TIME_INTERVAL,
                //deferredUpdatesTimeout: LOCATION_TIME_INTERVAL,
                foregroundService: {
                    notificationTitle: "Salut mon reuf",
                    notificationBody: "L'app enregistre là où tu zones en ce moment",
                    notificationColor: "#ffffff"
                }
            });
        },

        stopService: async () => {
            await Location.stopLocationUpdatesAsync(LOCATION_TASK_NAME);
        },

        getAllGpsData: () => gpsData,
        resetAllGpsData: () => gpsData.length = 0,
    }
}


const locationService = LocationService();
export default locationService;