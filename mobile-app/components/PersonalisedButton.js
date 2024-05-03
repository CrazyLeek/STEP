import React, { useState, useContext } from 'react';

import { View, Text, Button, FlatList, StyleSheet,
         TouchableOpacity, Pressable, Modal  } from 'react-native';





export default function PersonalisedButton({onPress, text}){

    return (

        <TouchableOpacity
            onPress={onPress}

            style={style.button}
        >   
            
            <Text 
                style={style.text}
            >
                {text}
            </Text>


        </TouchableOpacity>

    );
}


const style = StyleSheet.create({

    button: {
        //maxHeight:"12%",
        flex: 1,
        flexWrap: "nowrap",
        backgroundColor: '#ff9a8d',
        padding: 15,
        margin: 5,
        justifyContent: 'center',
        alignItems: 'center',
        borderRadius: 10,
        alignContent: "center",
        
      },

    text: {
        fontSize:25, 
        borderRadius:10,
    }

})