import React from 'react';
import { Component } from 'react';
import { Button, View, Text, TextInput, StyleSheet, Image } from 'react-native';
import '../global.js'

export default class LoginScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      email: "",
      pword: ""
    };
  }

  login() {
    let data = {
      email:this.state.email,
      password:this.state.pword
    }
    console.log(data)
    fetch('http://127.0.0.1:8000/api/login',{
      method: "POST",
      body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
      global.token = result; // Stores the user token which proves they've logged in
    })
  }

  render() {
    return (

      <View>
        <Text>{global.token}</Text>
        <Text>afsdafds</Text>
        <TextInput
          autoCorrect={false}
          ref={el => {
            this.email = el;
          }}
          onChangeText={(email) => {
            this.setState({'email': email});
          }}
          keyboardType="email-address"
          returnKeyType="go"
          placeholder="Email or Mobile Num"
          placeholderTextColor="rgba(225,225,225,0.8)"
        />
        <TextInput
          autoCorrect={false}
          ref={el => {
            this.pword = el;
          }}
          onChangeText={(pword) => {
            this.setState({ pword });
          }}
          returnKeyType="go"
          placeholder="Password"
          placeholderTextColor="rgba(225,225,225,0.8)"
        />
        <Image source={require('../assets/cat.jpeg')} />
        <Button onPress={this.login.bind(this)} title="Login" />
      </View>
    );
  }
}
