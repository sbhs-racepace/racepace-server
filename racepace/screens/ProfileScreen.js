import React from "react";
import { View, Text, Button } from "react-native";
import "../global.js"

export default class ProfileScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      name: 'Jason Yu',
      username: 'jyuuuk',
      age:16,
      email:'jasonyu0100@gmail.com',
      distance_run:10,
    }
  }

  render() {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <Text>Name: {this.state.name}</Text>
        <Text>Username: {this.state.username}</Text>
        <Text>Age: {this.state.age}</Text>
        <Text>Email: {this.state.email}</Text>
        <Text>Distance Run: {this.state.distance_run}</Text>
        <Button title="Logout" onclick={()=> {
          global.login_status = {success:false};
          this.props.navigation.goBack();
        }}/>
      </View>
    );
  }
}
