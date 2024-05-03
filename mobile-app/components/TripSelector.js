import React, { useState, useContext } from 'react';
import { View, Text, Button, FlatList, StyleSheet,TouchableOpacity, Pressable, Modal  } from 'react-native';

import { Link } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { GlobalContext, selectedJourneyFromGlobal } from './GlobalContext';


import SharedStyles from './SharedStyles';



export default function TripSelector({route, navigation})
{   
    const [journeys, setJourneys] = useState(null);
    const {newTripAdded, setNewTripAdded,
           setSelectedjourney} = useContext(GlobalContext);


    const saveJourneys = async (journeys) => {
        try {
            await AsyncStorage.setItem('@Journeys', JSON.stringify(journeys));
          } catch (e) {
            alert("Journeys saving has failed", e);
          }
    }

    const readJourneys = async () => {
        try {
            const value = await AsyncStorage.getItem('@Journeys')
            if(value !== null && value !== undefined) {
                setJourneys(JSON.parse(value));
            }
            else {
                setJourneys([]);
            }
        
        } catch(e) {
            alert("Journeys reading has failed ");
        }
    }
    

    if (journeys === null || newTripAdded) {

        if (newTripAdded){
            setNewTripAdded(false);
        }
        
        readJourneys();
        return ;
    }
    
    return (

    <View style={SharedStyles.page}>
        
        <Text>Note: to delete a journey, long-press it</Text>

        <View style={{flex: 1}}>
        {
            journeys.map( (journey, index) => {

                return (
                    <TouchableOpacity
                        key={index}

                        onLongPress={() => {
                            journeys_copy = [...journeys];
                            journeys_copy.splice(index, 1);

                            saveJourneys(journeys_copy);
                            setJourneys(journeys_copy);
                        }}

                        onPress={() => {
                            setSelectedjourney(journey);
                            selectedJourneyFromGlobal.set(journey);
                            navigation.navigate("HomePage");
                        }}

                    >
                        <JourneyElement 
                            key={index}
                            journey={journey}
                        >

                        </JourneyElement>
                        

                    </TouchableOpacity>
                    
                );
                
            })

        }
        </View>
        
        <View 
            style={{flex: 1 / 5}}
        >
            <TouchableOpacity
                onPress={ () => {
                    saveJourneys(journeys); 
                    navigation.navigate("JourneyEditor");
                    }}

                style={style.button}
            >   
                
                <Text 
                    style={{
                        fontSize: 24, 
                        marginHorizontal: 5,
                        backgroundColor:"#ff9a8d",
                        borderRadius:10,
                    }}
                >
                    Create a Journey
                </Text>
                
                
            </TouchableOpacity>
        </View>

        
    </View>
    );
}



export function JourneyElement({journey})
{
    return (

    <View style={{
        backgroundColor:"#aed6dc", 
        flexDirection:"row",
        flexWrap:"wrap",
        borderRadius:10,
        margin:5,
        }}>
        {   
        
            journey.map((trip, index) => {

                let text;

                if (["bus", "luas"].includes(trip[0])){
                    text = trip[0] + "-" + trip[1];
                }
                else {
                    text = trip[0];
                }

                return (
                    <Text 
                        key={index}
                        style={{
                            color: "#1d3c45",
                            fontSize:25, 
                            margin:10, 
                            backgroundColor:"#ffd79d", 
                            borderRadius:10, 
                            padding:5}}
                    >
                        {text}
                    </Text>
                );
                
                })
        }

    </View>

    );
}



const style = StyleSheet.create({

    button: {
        flex: 1,
        flexWrap: "wrap",
        backgroundColor: '#ff9a8d',
        padding: 15,
        margin: 5,
        justifyContent: 'center',
        alignItems: 'center',
        borderRadius: 10,
      },

})