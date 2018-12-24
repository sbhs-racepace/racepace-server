import React from "react";
import MapView from 'react-native-maps';
import { Marker } from 'react-native-maps';
import { View, Text, StyleSheet } from "react-native";

export default class MapScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      region: {
        latitude: -33.965832,
        longitude: 151.089029,
        latitudeDelta: 0.0922,
        longitudeDelta: 0.0421,
      },
      position: {
        latitude: -33.965832,
        longitude: 151.089029,
      },
      markers: []
    };
  }

  componentDidMount() {
    data = {
        'size': 1000,
        'start': '-33.965832, 151.089029',
        'end': '-33.964693, 151.090788'
    }
    fetch('http://127.0.0.1:8000/api/route',{
      method: "POST",
      body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
      console.log(result.route)
      result.route.map(marker => {
        this.state.markers.push({
          title:'Hello',
          coordinates: marker
        })})
    })
  }

  onRegionChange = (region) => {
    position = {
      latitude: region.latitude,
      longitude: region.longitude
    }
    this.setState({region , position});
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
      // <View style={styles.container}>
      // <MapView style={styles.map}
      //   initialRegion={this.state.region}
      //   onRegionChange={this.onRegionChange}
      // <Marker coordinate={marker.coordinates[0].coordinate}></Marker>
      // </MapView>
      // </View>


      <View style={styles.container}>
        <MapView style={styles.map}
          initialRegion={this.state.region}
          onRegionChange={this.onRegionChange}>
          {this.state.markers.map(marker => (
            <Marker coordinate={marker.coordinates}>
            </Marker>
          ))}
        </MapView>
      </View>
    );
  }
}
