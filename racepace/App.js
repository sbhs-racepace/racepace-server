import React from "react";
import {Button} from "react-native";
import { createStackNavigator, createAppContainer, createBottomTabNavigator } from "react-navigation";
import LoginScreen from "./screens/LoginScreen";
import AppScreen from "./screens/AppScreen";
import "./global.js"

const LoginNavigator = createStackNavigator({
  Login: {screen: LoginScreen},
  App: {screen: AppScreen,
  navigationOptions: {
    header: null
  }}
})

const AppContainer = createAppContainer(LoginNavigator);

export default class App extends React.Component {
  render() {
    return <AppContainer />;
  } 
}
