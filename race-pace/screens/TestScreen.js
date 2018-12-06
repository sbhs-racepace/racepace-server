import React from 'react';
import { Text } from 'react-native';
export default class TestScreen extends React.Component {
  static navigationOptions = {
    title: 'app.json',
  };

  render() {
    /* Go ahead and delete ExpoConfigView and replace it with your
     * content, we just wanted to give you a quick view of your config */
    return (<Text>Change this text and your app will automatically reload.</Text>)
  }
}
