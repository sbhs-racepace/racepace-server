import * as React from 'react';
import { Text, View, StyleSheet, Image, TouchableOpacity } from 'react-native';

export default class Button extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    let styles = {
      button: {
        backgroundColor: "skyblue",
        height: 25,
        borderWidth: 2,
      },
      text: {
        textAlign:"center",
        top: "50%"
      }
    };
    if (this.props.style) styles.button = Object.assign(styles.button,this.props.style)
    if (this.props.text_style) styles.text = Object.assign(styles.text, this.props.text_style)
    styles = StyleSheet.create(styles)
    
    return (
      <TouchableOpacity style={styles.button} onPress={this.props.onPress}>
        <Text style={styles.text}>{this.props.text}</Text>
      </TouchableOpacity>
    );
  }
}