import React from "react";
import { Platform, View, Text, Button, StyleSheet } from "react-native";
import MapView from 'react-native-maps';
import { createStackNavigator, createAppContainer } from "react-navigation";

const instructions = Platform.select({
  ios: 'Press Cmd+R to reload,\n' + 'Cmd+D or shake for dev menu',
  android:
    'Double tap R on your keyboard to reload,\n' +
    'Shake or press menu button for dev menu',
});

class HomeScreen extends React.Component {
  render() {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <Text>Home Screen</Text>
        <Text>{instructions}</Text>
        <Button
          title="Go to Details Screen"
          onPress={() => this.props.navigation.navigate('Details')}
        />
        <Button
          title="Go to Map Screen"
          onPress={() => this.props.navigation.navigate('Map')}
        />
      </View>
    );
  }
}

class MapScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      region: {
        latitude: 37.78825,
        longitude: -122.4324,
        latitudeDelta: 0.0922,
        longitudeDelta: 0.0421,
      },
      position: {
        latitude: 37.78825,
        longitude: -122.4324
      }
    };
  }

  onRegionChange = (region) => {
    position = {
      latitude: region.latitude,
      longitude: region.longitude
    }
    this.setState({ region , position});
  }

  render() {
    const styles = StyleSheet.create({
      container: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        justifyContent: 'flex-end',
        alignItems: 'center',
      },
      map: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
      },
    });

    return (
      <View style={styles.container}>
      <MapView style={styles.map}
        initialRegion={this.state.region}
        onRegionChange={this.onRegionChange}
      />
      </View>
    );
  }
}

class DetailsScreen extends React.Component {
  render() {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <Text>Details Screen</Text>
      </View>
    );
  }
}

const AppNavigator = createStackNavigator(
  {
    Home: HomeScreen,
    Details: DetailsScreen,
    Map: MapScreen,
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
