import React from "react";
import {BackHandler} from "react-native";
import { createAppContainer, createBottomTabNavigator } from "react-navigation";
import DetailScreen from "./DetailScreen";
import MapScreen from "./MapScreen";
import ProfileScreen from "./ProfileScreen";
import "../global.js"

const TabNavigator = createBottomTabNavigator({
    Details: DetailScreen,
    Map: MapScreen,
    Profile:ProfileScreen
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
