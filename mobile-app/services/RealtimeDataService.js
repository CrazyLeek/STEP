import React, {useContext, useState} from "react";

import * as BackgroundFetch from 'expo-background-fetch';
import * as TaskManager from 'expo-task-manager';

import PersonalisedButton from "../components/PersonalisedButton";
import { selectedJourneyFromGlobal } from '../components/GlobalContext';


const FETCH_DATA_TASK = 'FETCH_DATA_TASK';

var allRealtimeData = [];

var assoc_bus_name_id = {
    '6': '4021_65701', '11': '4021_65702', '4': '4021_65703', '13': '4021_65704', '14': '4021_65705', 
    '15': '4021_65706', '16': '4021_65707', '16D': '4021_65708', 'L53': '4021_65709', '26': '4021_65710', 
    '27': '4021_65711', '27X': '4021_65712', '77X': '4021_65713', '32X': '4021_65714', '33': '4021_65715', 
    '33X': '4021_65716', '33D': '4021_65717', '33E': '4021_65718', '37': '4021_65719', '38': '4021_65720', 
    '38A': '4021_65721', '38B': '4021_65722', '70': '4021_65723', '38D': '4021_65724', '70D': '4021_65725', 
    '39X': '4021_65726', '39': '4021_65727', '39A': '4021_65728', '40': '4021_65729', '40B': '4021_65730', 
    '40E': '4021_65731', '40D': '4021_65732', '41': '4021_65733', '41D': '4021_65734', '41B': '4021_65735', 
    '41C': '4021_65736', '41X': '4021_65737', '42': '4021_65738', '43': '4021_65739', '44D': '4021_65740', 
    '44': '4021_65741', '44B': '4021_65742', '46A': '4021_65743', '46E': '4021_65744', '7': '4021_65745', 
    '7A': '4021_65746', '7B': '4021_65747', '7D': '4021_65748', '7E': '4021_65749', '47': '4021_65750', 
    '49': '4021_65751', '51D': '4021_65752', '52': '4021_65753', '27A': '4021_65754', '53': '4021_65755', 
    '54A': '4021_65756', '56A': '4021_65757', '60': '4021_65758', '65B': '4021_65759', '65': '4021_65760', 
    '69': '4021_65761', '69X': '4021_65762', '68': '4021_65763', '68A': '4021_65764', '74': '4021_65765', 
    '77A': '4021_65766', '83': '4021_65767', '83A': '4021_65768', '84A': '4021_65769', '84': '4021_65770', 
    '99': '4021_65771', '116': '4021_65772', '118': '4021_65773', '120': '4021_65774', '9': '4021_65775', 
    '122': '4021_65776', '123': '4021_65777', '130': '4021_65778', '140': '4021_65779', '1': '4021_65780', 
    '142': '4021_65781', '84X': '4021_65782', '145': '4021_65783', '150': '4021_65784', '151': '4021_65785', 
    '155': '4021_65786', 'P29': '4021_65787', 'X25': '4021_65788', 'X26': '4021_65789', 'X27': '4021_65790', 
    'X28': '4021_65791', 'X30': '4021_65792', 'X31': '4021_65793', 'X32': '4021_65794', 'C1': '4021_65795', 
    'C2': '4021_65796', 'C3': '4021_65797', 'C4': '4021_65798', 'C6': '4021_65799', 'C5': '4021_65800', 
    'G1': '4021_65801', 'G2': '4021_65802', 'H1': '4021_65803', 'H2': '4021_65804', 'H3': '4021_65805', 
    'N4': '4021_65806', 'S2': '4021_65807', '15B': '4021_65808', '15D': '4021_65809', '15A': '4021_65810', 
    '27B': '4021_65811', '42D': '4021_65812', 'L25': '4021_65813', 'L54': '4021_65814', 'L58': '4021_65815', 
    'L59': '4021_65816'
}



TaskManager.defineTask(FETCH_DATA_TASK, async () => {

    console.log('Tâche en arrière-plan exécutée !');
    console.log("Date : ", Date());

    try {
        let response = await fetchRealtimeData();
        
        await processRealtimeData(response);
      
        return BackgroundFetch.BackgroundFetchResult.NewData;
    } catch (error) {
        console.error(error);
        return BackgroundFetch.BackgroundFetchResult.Failed;
    }
});

export async function fetchRealtimeData(){


    try {
        let response = await fetch(
            'https://api.nationaltransport.ie/gtfsr/v2/gtfsr?format=json',
            {
                method: 'GET',
                headers: {
                    'Cache-Control': 'no-cache',
                    'x-api-key': '0f564cc3440841d9a6433fd3a109c4d0',
                }
            }
        );

        let json = await response.json();
        //console.log(json);

        return json;

    } catch (error) {
        console.error(error);
    }
}

export function get_bus_names_in_journey(){

    selectedJourney = selectedJourneyFromGlobal.get();

    console.log("get_bus_names_in_journey appelé");

    let bus_names = [];
    let bus_ids   = [];

    selectedJourney.map((trip, index) => {

        if (trip[0] === "bus"){
            let bus_name = trip[1];

            bus_names.push(bus_name);
            bus_ids.push(assoc_bus_name_id[bus_name]);
        }
    });

    return [bus_names, bus_ids];
}

async function processRealtimeData(realtimeData=null){

    if (realtimeData === null){
        console.log("No realtime data, fetching it from internet...");
        realtimeData = await fetchRealtimeData();
        console.log("Fetch finished");
    }
    console.log("Processing the data...");

    var [buses_name_in_journey, buses_id_in_journey] = get_bus_names_in_journey();


    let filtered_data = [];

    console.log(buses_name_in_journey, buses_id_in_journey);

    realtimeData["entity"].forEach(element => {

        let route_id = element["trip_update"]["trip"]["route_id"];

        if (buses_id_in_journey.includes(route_id)){
            filtered_data.push(element["trip_update"]);
        }
        
    });


    allRealtimeData.push({
        "timestamp": realtimeData["header"]["timestamp"],
        "entity": filtered_data,
    });

    console.log(allRealtimeData);


}




const RealtimeDataService = () => {

    let isRunning = false;

    TaskManager.isTaskRegisteredAsync(FETCH_DATA_TASK)
        .then(((isRegistred) => {
            if (isRegistred) {
                BackgroundFetch.unregisterTaskAsync(FETCH_DATA_TASK);
            }
        })
    );


    return {
        runService: async () => {

            if (!isRunning){
                await BackgroundFetch.registerTaskAsync(
                    FETCH_DATA_TASK, 
                    {
                        minimumInterval: 60 * 15, // 15 minutes
                        stopOnTerminate: true,
                        startOnBoot: false,
                    }
                );
                BackgroundFetch.setMinimumIntervalAsync(60 * 15);
                console.log("Background service for realtime started");
                isRunning = true;
            }
        },

        stopService: async () => {

            if (isRunning){
                await BackgroundFetch.unregisterTaskAsync(FETCH_DATA_TASK);
                console.log("Background service for realtime stopped");
                isRunning = false;
            }
        },

        fetchRealtimeData: async () => {
            let response = await fetchRealtimeData();
            await processRealtimeData(response);
        },

        getAllrealtimeData: () => allRealtimeData,

        isActive: () => isRunning,
    }
}

const realtimeDataService = RealtimeDataService();
export default realtimeDataService;



export function FetchDataButton(){

    const [isRunning, setIsRunning] = useState(realtimeDataService.isActive());

    console.log("is running : ", isRunning);
    var text;
    isRunning? 
        text="Stop background service"
    : 
        text="Start background service";

    return (
        <>
        <PersonalisedButton
            onPress={() => {
                /*isRunning?
                    realtimeDataService.stopService():
                    realtimeDataService.runService();*/

                console.log(allRealtimeData);

                setIsRunning(!isRunning);  

            }}
            text={"Print allRealtimeData"}
        />


        </>
       
    )
}