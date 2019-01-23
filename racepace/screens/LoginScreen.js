import React from "react";
import {Component} from "react"
import { View, Text, TextInput, StyleSheet, Image} from 'react-native';
import '../global.js'

export default class LoginScreen extends React.Component {
  constructor(props) {
    super(props)
    global.token = "Not NULL";
  }
  render() {
    return (

      <View>
        <Text>{global.token}</Text>
        <Text>afsdafds</Text>
        <TextInput
               autoCorrect={false}
               keyboardType='email-address'
               returnKeyType="go"
               placeholder='Email or Mobile Num'
               placeholderTextColor='rgba(225,225,225,0.7)'>
        </TextInput>
        <TextInput
               autoCorrect={false}
               returnKeyType="go"
               placeholder='Password'
               placeholderTextColor='rgba(225,225,225,0.7)'>
        </TextInput>
        <Image
          source={require('../assets/cat.jpeg')}
        />
      </View>
    );
  }
}
