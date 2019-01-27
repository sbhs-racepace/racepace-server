import React from "react";
import { View, Text, TextInput, } from "react-native";
import { TextInput } from "react-native-gesture-handler";

export default class RouteScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      fromto:"",
      length:0
    }
  }
  render() {
    return (
      <TextInput
      ref= {el => {this.fromto = el}}
      onChangeText = {(from_to)=> {this.setState({fromto:from_to})}}
      returnKeyType="go"
      placeholder="From/To"
      placeholderTextColor="rgba(225,225,225,0.8)"
      ></TextInput>
      <TextInput
      ref= {el => {this.length = el}}
      onChangeText = {(run_length)=> {this.setState({length:run_length})}}
      returnKeyType="go"
      placeholder="Run Length"
      placeholderTextColor="rgba(225,225,225,0.8)"
      ></TextInput>
    );
  }
}
