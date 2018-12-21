import React from "react";
import Axios from "axios";
import { Platform, View, Text, Button } from "react-native";

const instructions = Platform.select({
  ios: 'Press Cmd+R to reload,\n' + 'Cmd+D or shake for dev menu',
  android:
    'Double tap R on your keyboard to reload,\n' +
    'Shake or press menu button for dev menu',
});

export default class HomeScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      items: []
    };
  }

  componentDidMount() {
    fetch('http://127.0.0.1:8000/')
    .then(res => res.json())
    .then(result => {
      console.log(result.message)
    })
  }

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
