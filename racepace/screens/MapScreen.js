import React from "react";
import MapView from 'react-native-maps';
import { Marker, Polyline } from 'react-native-maps';
import { View, Text, StyleSheet, Button } from "react-native";

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

  api_route() {
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

  onRegionChange = (region) => {
    this.setState({
      mapRegion: region,
      lastLat: region.latitude || this.state.lastLat,
      lastLong: region.longitude || this.state.lastLong
    });
  }

  componentDidMount() {
    this.watchID = navigator.geolocation.watchPosition((position) => {
      let region = {
        latitude:       position.coords.latitude,
        longitude:      position.coords.longitude,
        latitudeDelta:  0.00922*1.5,
        longitudeDelta: 0.00421*1.5
      }
      this.onRegionChange(region);
    });
  }

  componentWillUnmount() {
    navigator.geolocation.clearWatch(this.watchID);
  }

  render () {
    return(
      <MapView
        style={{flex: 1}}
        showsUserLocation={true}
        followUserLocation={true}
        initialRegion={this.state.region}
        onRegionChange={this.onRegionChange}
      >
        <Marker
          coordinate={{
            latitude: (this.state.lastLat + 0.00050) || -36.82339,
            longitude: (this.state.lastLong + 0.00050) || -73.03569,
          }}>
          <View>
            <Text style={{color: '#000'}}>
              { this.state.lastLong } / { this.state.lastLat }
            </Text>
          </View>
        </Marker>

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
    );
  }
}
