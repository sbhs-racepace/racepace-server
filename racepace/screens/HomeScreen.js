import React from "react";
import { Platform, View, Text, Button } from "react-native";


export default class HomeScreen extends React.Component {
  render() {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <Text>Home Screen</Text>
        <Button
          title="Go to Details Screen"
          onPress={() => this.props.navigation.navigate('Details')}
        />
        <Button
          title="Go to Map Screen"
          onPress={() => this.props.navigation.navigate('Map')}
        />
        <Button
          title="Go to Login Screen"
          onPress={() => this.props.navigation.navigate('Login')}
        />
        <Button
          title="Go to Profile Screen"
          onPress={() => this.props.navigation.navigate('Profile')}
        />
        <Button
          title="Go to Route Screen"
          onPress={() => this.props.navigation.navigate('Route')}
        />
        <Button
          title="Go to Add Route Screen"
          onPress={() => this.props.navigation.navigate('AddRoute')}
        />
      </View>

    );
  }
}
