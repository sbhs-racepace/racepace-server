import React from 'react';
import { Component } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  Image,
  Alert,
} from 'react-native';
import Button from '../components/Button.js'
import PickTwo from '../components/PickTwo'
import {login} from "../login"
import '../global';

const STYLES = StyleSheet.create({
  input: {
    borderLeftWidth: 2,
    borderBottomWidth: 2,
    marginTop: 5,
    paddingLeft: 3,
    width:"80%",
    left: "10%",
    right: "10%",
  },
  general: {
    marginTop: 5,
    width:"80%",
    left: "10%",
  },
  pickTwo: {
    width:"50%"
  }
})

export default class RegisterScreen extends React.Component {
  static navigationOptions = {
    title: 'Register',
  };
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
  }

  render() {
    return (
      <View>
        <Image style={STYLES.general} source={require('../assets/cat.jpeg')} />
        <TextInput
          autoCorrect={false}
          defaultValue="ccc"
          ref={el => {
            this.name = el;
          }}
          onChangeText={name_ => {
            this.setState({ name: name_ });
          }}
          style={STYLES.input}
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
          style={STYLES.input}
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
          style={STYLES.input}
          returnKeyType="go"
          placeholder="Password"
          secureTextEntry={true}
          placeholderTextColor="rgba(225,225,225,0.8)"
        />
        <PickTwo view_style={STYLES.general} btn_style={STYLES.pickTwo} options={["Standard","Coach"]} abbrev={["s","c"]} _this={this} />
        <Button style={STYLES.general} text="Register" onPress={login.bind(this)} />
      </View>
    );
  }
}
