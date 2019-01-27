import React from "react";
import { View, Text, List, ListItem, Button } from "react-native";

export default class RunTimeTable extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      plannedruns:['a','b','c']
    }
  }
  render() {
    return (
      <View>
        <Text>Saved Routes</Text>
        {this.state.plannedruns.map(run => (
          <Text>{run}</Text>
        ))}
        <Text>Add your Run</Text>
        <Button
          title="Add Run from saved (Not Implemented)"
          onPress={null}
        />
        <Button
          title="Add New Run (Not Implemented)"
          onPress={null}
        />
      </View>
    );
  }
}
