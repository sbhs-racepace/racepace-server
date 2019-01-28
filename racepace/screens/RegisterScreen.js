import React from 'react';
import { Component } from 'react';
import {
  Button,
  View,
  Text,
  TextInput,
  StyleSheet,
  Image,
  Alert,
} from 'react-native';
import '../global';

export default class RegisterScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      name: 'ccc',
      email: 'aaa',
      pword: 'bbb',
      type: "s",
      std_txt: "✓ Standard",
      coach_txt: "Coach",
    };
    
    this.setState({
      std_txt: "Standard",
      coach_txt: "Coach ✓",
      type: "c"
    })
  }
  
  check_login(res) {
    if (res === null) {
      Alert.alert('Error connecting to login server');
      return 0; //exit
    }
    if (res.success) {
      global.login_status = res;
    } else {
      Alert.alert('Error', res.error);
    }
  }

  login() {
    let data = {
      email: this.state.email,
      password: this.state.pword,
      name: this.state.name
    };
    fetch('http://192.168.0.5:8000/api/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
      .catch(res => {Alert.alert('Error connecting to login server', res);})
      .then(res => res.json())
      .then(res => this.check_login(res));
    this.props.navigation.navigate('App');
  }

  render() {
    return (
      <View>
        <Text>{"\n"}Register</Text>
        <Image source={require('../assets/cat.jpeg')} />
        <TextInput
          autoCorrect={false}
          defaultValue="ccc"
          ref={el => {
            this.name = el;
          }}
          onChangeText={name_ => {
            this.setState({ name: name_ });
          }}
          returnKeyType="go"
          placeholder="Name"
          placeholderTextColor="rgba(225,225,225,0.8)"
        />
        <TextInput
          autoCorrect={false}
          defaultValue="aaa"
          ref={el => {
            this.email = el;
          }}
          onChangeText={email => {
            this.setState({ email: email });
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
          onChangeText={pword => {
            this.setState({ pword });
          }}
          returnKeyType="go"
          placeholder="Password"
          secureTextEntry={true}
          placeholderTextColor="rgba(225,225,225,0.8)"
        />
        <View style={{flexDirection: 'row'}}>
          <Button title={this.state.std_txt} onclick= {() => {
            this.setState({
              std_txt: "✓ Standard",
              coach_txt: "Coach",
              type: "s"
            });
          }}>{this.state.std_txt}</Button>
          <Text>{"   "}</Text>
          <Button title={this.state.coach_txt} onclick= {() => {
            this.setState({
              std_txt: "Standard",
              coach_txt: "Coach ✓",
              type: "c"
            });
          }}>{this.state.coach_txt}</Button>
        </View>
        <Button title="Register" />
      </View>
    );
  }
}
