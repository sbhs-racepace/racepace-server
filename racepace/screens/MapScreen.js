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
    let start = '-33.9672563,151.1002119'
    let end   = '-33.9619925,151.1059193'
    this.api_route(start, end);
  }

  api_route(start, end) {
    data = {
      'start': start,
      'end': end,
    }
    fetch('http://127.0.0.1:8000/api/route',{
      method: "POST",
      body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
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
        <Polyline
          coordinates={this.state.markers.map(marker => {return marker.coordinate})}
          strokeColor="#9900FF"
          strokeWidth={6}>
        </Polyline>
      </MapView>
    );
  }
}
