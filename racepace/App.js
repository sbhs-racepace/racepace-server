import React from "react";
import { createStackNavigator, createAppContainer } from "react-navigation";
import HomeScreen from "./screens/HomeScreen";
import DetailScreen from "./screens/DetailScreen";
import MapScreen from "./screens/MapScreen";
import LoginScreen from "./screens/LoginScreen";

const AppNavigator = createStackNavigator(
  {
    Home: HomeScreen,
    Details: DetailScreen,
    Map: MapScreen,
    Login: LoginScreen,
  },
  {
    initialRouteName: "Home"
  }
);

const AppContainer = createAppContainer(AppNavigator);

export default class App extends React.Component {
  render() {
    return <AppContainer />;
  }
}
