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
import {login,logout} from "../login"
import Button from '../components/Button.js'
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
    right: "10%",
  },
})

export default class LoginScreen extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      email: 'aaa',
      pword: 'bbb',
      isSigninInProgress: false,
    };
  }

  componentDidUpdate() {
    console.log("update")
  }
 /*  async componentDidMount() {
    GoogleSignin.configure({
      webClientId: CLIENT_ID,
      offlineAccess: false,
    });
  } */

  /* async googleLogin() {
    let userInfo;
    try {
      await GoogleSignin.hasPlayServices();
      userInfo = await GoogleSignin.signIn();
    } catch (error) {
      if (error.code === statusCodes.SIGN_IN_CANCELLED) {
        // sign in was cancelled
        Alert.alert('cancelled');
      } else if (error.code === statusCodes.IN_PROGRESS) {
        // operation in progress already
        Alert.alert('in progress');
      } else if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
        Alert.alert('play services not available or outdated');
      } else {
        Alert.alert('Something went wrong', error.toString());
        this.setState({
          error,
        });
      }
    }
    console.log(userInfo);
  }
  ===
  
  <GoogleSigninButton
    style={{ width: 48, height: 48 }}
    size={GoogleSigninButton.Size.Icon}
    color={GoogleSigninButton.Color.Dark}
    onPress={this._signIn}
    disabled={this.state.isSigninInProgress} />
  */

  render() {
    /* console.log("run")
    console.log(global.login_status) */
    /* if (global.login_status.success) {
      logout().bind(this)
    } */
    return (
      <View>
        <Image style={STYLES.general} source={require('../assets/cat.jpeg')} />
        <TextInput
          autoCorrect={false}
          defaultValue="aaa"
          style = {STYLES.input}
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
          style = {STYLES.input}
          ref={el => {
            this.pword = el;
          }}
          onChangeText={pword => {
            this.setState({ pword });
          }}
          returnKeyType="go"
          secureTextEntry={true}
          placeholder="Password"
          placeholderTextColor="rgba(225,225,225,0.8)"
        />
        <Button style={STYLES.general} onPress={login.bind(this)} text={"Login"} />
        <Button
          style={STYLES.general}
          onPress={() => {
            global.login_status = { success: true };
            this.props.navigation.navigate('Main');
          }}
          text={"Login as guest"}
        />
        <Button style={STYLES.general} onPress = {() => this.props.navigation.navigate('Register')} text="Register" />
      </View>
    );
  }
}
