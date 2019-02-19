import * as React from 'react';
import { Text, View, StyleSheet, Image, TouchableOpacity } from 'react-native';
import Button from "./Button"

export default class PickTwo extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      tick1: "✓ ",
      tick2: ""
    };
  }
  click1() {
    this.setState({
      tick1: "✓",
      tick2: " "
    });
    this.props._this.setState({acc_type: this.props.abbrev[0]});
  }
  click2() {
    this.setState({
      tick1: " ",
      tick2: "✓"
    });
    this.props._this.setState({acc_type: this.props.abbrev[1]});
  }

  render() {
    let styles = {
      view: {flexDirection: 'row',
        bottomMargin: 10,
        height: 25
      },
      button: {
      },
      text: {

      }
    };
    if (this.props.view_style) styles.view = Object.assign(styles.view,this.props.view_style);
    if (this.props.btn_style) styles.button = Object.assign(styles.button,this.props.btn_style);
    if (this.props.text_style) styles.text = Object.assign(styles.text, this.props.text_style);
    styles = StyleSheet.create(styles);

    return (
      <View style={styles.view}>
        <Button style={styles.button} text_style={styles.text}
        onPress={this.click1.bind(this)}
        text={this.state.tick1+" "+this.props.options[0]} />
        <Button style={styles.button} text_style={styles.text}
        onPress={this.click2.bind(this)}
        text={this.props.options[1]+" "+this.state.tick2} />
      </View>
    );
  }
}