import React from "react";
import {BackHandler} from "react-native";
import { createAppContainer, createBottomTabNavigator } from "react-navigation";
import DetailScreen from "./DetailScreen";
import MapScreen from "./MapScreen";
import ProfileScreen from "./ProfileScreen";
import RegisterScreen from "./RegisterScreen";
import "../global"

const TabNavigator = createBottomTabNavigator({
    Details: DetailScreen,
    Map: MapScreen,
    Profile:ProfileScreen,
    //Register: RegisterScreen //Temporarily added here for testing, no link from login page yet
  });
const AppContainer = createAppContainer(TabNavigator);

export default class AppScreen extends React.Component {
  componentWillMount() {
    BackHandler.addEventListener('hardwareBackPress', function () {
      return true
    })
  }
  render() {
    return <AppContainer />;
  } 
}
