
import React, { useState, useContext, useEffect } from 'react';
import { View, Text, Button, FlatList, StyleSheet,TouchableOpacity  } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { Picker } from '@react-native-picker/picker';
import { Link } from '@react-navigation/native';

import { GlobalContext } from './GlobalContext';
import PersonalisedButton from './PersonalisedButton';
import SharedStyles from './SharedStyles';

const busList  = 
    ['1', '11', '116', '118', '120', '122', '123', '13', '130', '14', '140',
     '142', '145', '15', '150', '151', '155', '15A', '15B', '15D', '16', '16D',
     '26', '27', '27A', '27B', '27X', '32X', '33', '33D', '33E', '33X', '37',
     '38', '38A', '38B', '38D', '39', '39A', '39X', '4', '40', '40B', '40D',
     '40E', '41', '41B', '41C', '41D', '41X', '42', '42D', '43', '44', '44B',
     '44D', '46A', '46E', '47', '49', '51D', '52', '53', '54A', '56A', '6',
     '60', '65', '65B', '68', '68A', '69', '69X', '7', '70', '70D', '74',
     '77A', '77X', '7A', '7B', '7D', '7E', '83', '83A', '84', '84A', '84X', 
     '9', '99', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'G1', 'G2', 'H1', 'H2', 
     'H3', 'L25', 'L53', 'L54', 'L58', 'L59', 'N4', 'P29', 'S2', 'X25', 'X26',
     'X27', 'X28', 'X30', 'X31', 'X32']

const luasList = ["Green", "Red"];


 

export default function TripEditor({ navigation})
{   
    const {setNewTripAdded} = useContext(GlobalContext);
    const [goToTripSelector, setGoToTripSelector] = useState(false);

    useEffect( () => {

        if (goToTripSelector){
            console.log(list);
            navigation.navigate("JourneySelector");
        }
        
    }, [goToTripSelector]);

    const [list, setList] = useState([["", ""]]);
    var journeys = [];

    const addItem = () => {

        if (list.length === 5){
            alert("Maximum number of trips reached");
        }
        else {
            setList([...list, ["", ""]]);
        }
        
    };

    const delItem = () => {
        if (list.length > 1){
            setList(list.slice(0, -1));
        }
    };

    const addNewTrip = async () => {

        // Reading the list of journeys
        try {
            const value = await AsyncStorage.getItem('@Journeys')
            if(value !== null && value !== undefined) {
                journeys = JSON.parse(value);
            } else {
                journeys = [];
            }

        } catch(e) {
            alert("Journeys reading has failed in TripEditor.");
            journeys = [];
        }
        
        // Adding the new journey
        journeys.push(list);
        
        // Saving the new list of journeys
        try {
            await AsyncStorage.setItem('@Journeys', JSON.stringify(journeys));

        } catch (e) {
            alert("Journeys saving has failed in TripEditor.", e);
        }

    }

    

    return (
        <View style={SharedStyles.page}>            

            <FlatList
                style={{ flex: 1}}
                data={list}
                keyExtractor={(item, index) => index.toString()}
                renderItem={({ item }) => {return (
                    <TripElement 
                        style={{ flex: 1 }}
                        dataForParent={item}
                    ></TripElement> 
                )}}
            />

            

            <View style={{flexDirection: "row"}}>

                <PersonalisedButton
                    text={"Add a trip"}
                    onPress={addItem}
                />

                <PersonalisedButton
                    text={"Delete a trip"}
                    onPress={delItem}
                />

            </View>

            <View style={{flex: 1 / 6}}>

                <PersonalisedButton
                    text={"Validate"}
                    onPress={async () => {
                        await addNewTrip();
                        
                        setNewTripAdded(true);
                        setGoToTripSelector(true);
                    }}
                />
                
            </View>
        </View>
    );
}




function TripElement ({dataForParent})
{   
    const [transportMode, setTransportMode] = useState("walk");
    const [selectedLine, setSelectedLine] = useState("none");
    const [availableLines, setAvailableLines] = useState(['']);

    dataForParent[0] = transportMode; // Need to understand the cycle of life of a component
    dataForParent[1] = selectedLine;  // and variables defined with useState

    return (
    <View style={tripElementStyle.container}>
        <Picker
            style={{ flex: 1, margin:3 }}
            selectedValue={transportMode}
            onValueChange={(itemValue, itemIndex) => {

                setTransportMode(itemValue);

                if (itemValue === "bus"){
                    setAvailableLines(busList);
                    setSelectedLine(busList[0]);

                } else if (itemValue === "luas") {
                    setAvailableLines(luasList);
                    setSelectedLine(luasList[0]);
                }
                else {
                    setSelectedLine("none");
                }
                
            }}
        >
            <Picker.Item label="Walk" value="walk" />
            <Picker.Item label="Bike" value="bike" />
            <Picker.Item label="Bus " value="bus" />
            <Picker.Item label="Luas" value="luas" />
            <Picker.Item label="DART" value="dart" />
            <Picker.Item label="Car " value="car" />
        </Picker>

        {
            ["bus", "luas"].includes(transportMode)
            &&
        <>
            <View style={tripElementStyle.verticalLine} />

            <Picker
                style={{ flex: 1}}
                selectedValue={selectedLine}
                onValueChange={(itemValue, itemIndex) => {
                    setSelectedLine(itemValue);
                }}
            >
            {
                availableLines.map(
                    (item, index) => (
                        <Picker.Item key={index} label={item} value={item} />
                    )
                )
            }
            </Picker>
        </>
        }
 
    </View>
    )
}



const tripElementStyle = StyleSheet.create({

    container: {

        flex:1, 
        backgroundColor: '#dad6d1',
        flexDirection: "row",
        flexWrap: "wrap",
        margin:7,
        borderRadius: 20,
        
      },

      verticalLine: {
        height: '100%',
        width: 1,
        backgroundColor: '#909090',

      },

      button: {
        flex: 1,
        backgroundColor: 'lightblue',
        padding: 15,
        margin: 5,
        justifyContent: 'center',
        alignItems: 'center',
        borderRadius: 10,
      },

      textButton: {
        fontSize:18
      },

});
