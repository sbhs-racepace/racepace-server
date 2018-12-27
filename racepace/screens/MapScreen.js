import React from "react";
import MapView from 'react-native-maps';
import { Marker, Polyline } from 'react-native-maps';
import { View, Text, StyleSheet } from "react-native";

export default class MapScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      region: {
        latitude: -33.965832,
        longitude: 151.089029,
        latitudeDelta: 0.0922*1.5,
        longitudeDelta: 0.0421*1.5,
      },
      lastLat: null,
      lastLong: null,
      markers: []
    };
  }

  componentDidMount() {
    data = {
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
          title:'Node',
          coordinate: marker
        })})
    })
  }

  // componentDidMount() {
  //   this.watchID = navigator.geolocation.watchPosition((position) => {
  //     let region = {
  //       latitude:       position.coords.latitude,
  //       longitude:      position.coords.longitude,
  //       latitudeDelta:  0.00922*1.5,
  //       longitudeDelta: 0.00421*1.5
  //     }
  //     this.onRegionChange(region, region.latitude, region.longitude);
  //   };
  // }

  onRegionChange = (region) => {
    this.setState({
      mapRegion: region,
      lastLat: region.latitude || this.state.lastLat,
      lastLong: region.longitude || this.state.lastLong
    });
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
          onRegionChange={this.onRegionChange}>

          <Polyline
            coordinates={this.state.markers.map(marker => {return marker.coordinate})}
            strokeColor="#000" // fallback for when `strokeColors` is not supported by the map-provider
            strokeColors={[
              '#7F0000',
              '#00000000', // no color, creates a "long" gradient between the previous and next coordinate
              '#B24112',
              '#E5845C',
              '#238C23',
              '#7F0000'
            ]}
            strokeWidth={6}>
          </Polyline>


        </MapView>
      </View>
    );
  }
}
