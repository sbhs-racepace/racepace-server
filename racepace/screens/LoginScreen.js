import React from 'react';
import { Component } from 'react';
import { Button, View, Text, TextInput, StyleSheet, Image, Alert } from 'react-native';
import "../global.js"

export default class LoginScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      'email': "aaa",
      'pword': "bbb"
    };
  }

  check_login(res) {
    console.log(res)
    if (res.success) {
      global.login_status = res
    }
    else {
      Alert.alert("Error",res.error)
    }
  }

  login() {
    console.log("asd")
    let data = {
      'email':this.state.email,
      'password':this.state.pword
    }
    fetch('http://192.168.0.5:8000/api/login',{
      method: "POST",
      body: JSON.stringify(data)
    })
    .catch(res => Alert.alert("Error connecting to login server",res))
    .then(res => res.json())
    .then(res => this.check_login(res))
    console.log(global.login_status)
  }
  
  render() {
    return (
      <View>
      <Text>Login</Text>
        <TextInput
          autoCorrect={false}
          defaultValue="aaa"
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
          defaultValue="bbb"
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
