import React from "react";
import { View, Text, List, ListItem } from "react-native";

export default class RouteScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      routes:['a','b','c']
    }
  }
  render() {
    return (
      <View>
        <Text>Saved Routes</Text>
        {this.state.routes.map(i => (
          <Text>{i}</Text>
        ))}
      </View>
    );
  }
}
