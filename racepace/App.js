import React from "react";
import {Button} from "react-native";
import { createStackNavigator, createAppContainer, createBottomTabNavigator } from "react-navigation";
import LoginScreen from "./screens/LoginScreen";
import ProfileScreen from "./screens/ProfileScreen";
import RouteScreen from "./screens/RouteScreen";

const AppNavigator = createStackNavigator(
  {
    Home: HomeScreen,
    Details: DetailScreen,
    Map: MapScreen,
    Login:LoginScreen,
    Profile:ProfileScreen,
    Route: RouteScreen,
    AddRoute: AddRouteScreen
  },
  {
    initialRouteName: "Home"
  }
);

const AppContainer = createAppContainer(LoginNavigator);

export default class App extends React.Component {
  render() {
    return <AppContainer />;
  } 
}
