import React, { useState, useContext, useEffect } from 'react';

import { View, Text, Button, FlatList, StyleSheet,
         TouchableOpacity, Pressable, Modal  } from 'react-native';

import * as Location from 'expo-location';

import { GlobalContext } from './GlobalContext';
import { JourneyElement } from './TripSelector';
import PersonalisedButton from './PersonalisedButton';
import LocationComponent from './LocationComponent';
import SharedStyles from './SharedStyles';
import { FetchDataButton } from '../services/RealtimeDataService';


export default function HomePage({navigation}){

    const {selectedJourney, setSelectedjourney} = useContext(GlobalContext);


    return (

        <View style={SharedStyles.page}>

            <View
                style={{
                    flex: 1 / 4,
                    justifyContent: 'center',
                    alignItems: 'center',
                }}>
                <Text 
                    style={{
                        fontSize: 30,
                    }}
                >
                    Record your journey !
                </Text>

            </View>
            
            {
                selectedJourney.length !== 0 ? // if
                <>
                    <TouchableOpacity
                        onPress={() => navigation.navigate("JourneySelector")}
                    >
                        <JourneyElement 
                            journey={selectedJourney}
                        />

                    </TouchableOpacity>

                    <View style={{flex:1 / 10}} />

                    <View style={{flex: 2 / 5, alignItems: "flex-end", flexDirection:"row"}}>
                        <LocationComponent />
                    </View>
                </>
                : // else
                
                <View style={{flex: 2 / 5}}>
                    <PersonalisedButton 
                        onPress={ () => {
                            navigation.navigate("JourneySelector");
                        }}

                        text={"No journey selected"}
                    />

                </View>
            }
        </View>
    )
}




