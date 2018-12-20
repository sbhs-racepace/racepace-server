import React from "react";
import MapView from 'react-native-maps';
import { View, Text, StyleSheet } from "react-native";

export default class MapScreen extends React.Component {
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
