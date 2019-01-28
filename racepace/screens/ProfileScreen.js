import React from "react";
import { View, Text, Button, Image, StyleSheet, ScrollView } from "react-native";
import "../global"
import "../assets/cat.jpeg"

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f00',flex: 1, alignItems: "flex-start", justifyContent: "flex-start"
  },
  white_text: {
    color: 'white',
    fontSize: 20
  },
  profileimage:{ height: 100, borderRadius: 100, width: 100},
  profile_data_box: { flexDirection:'column', justifyContent:'flex-end'},
  profile_box : {
    flexDirection: 'row'
  }
})

class WhiteText extends React.Component {
  render() {
    return (
      <Text style={styles.white_text}>{this.props.text}</Text>
    )
  }
}

export default class ProfileScreen extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      name: 'Jason Yu',
      username: 'jyuuuk',
      age:16,
      email:'jasonyu0100@gmail.com',
      statistics: {
        fastest_100:9.4,
        total_distance_run:100,
        fastest_800:120,
        v02_max:56,
        average_pace:3.40,
      },
      imageurl: "../assets/cat.jpeg",
    }
  }

  render() {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.profile_box}>
          <Image style= {styles.profileimage} source={require(this.state.imageurl)} />
          <View style={styles.profile_data_box}>
            <Text style={styles.white_text}>Name: {this.state.name}</Text>
            <Text style={styles.white_text}>Username: {this.state.username}</Text>
            <Text>Age: {this.state.age}</Text>
            <Text>Email: {this.state.email}</Text>

            <Text>ij{this.state.statistics.total_fastest_100}</Text>
            <Text>ubhu{this.state.statistics.total_distance_run}</Text>
            <Text>ij {this.state.statistics.total_fastest_800}</Text>
            <Text>ij {this.state.statistics.total_v02_max}</Text>
            <Text>ni{this.state.statistics.total_average_pace}</Text>
          </View>
        </View>
         
          <Button title="Logout" onclick={()=> {
            global.login_status = {success:false};
            this.props.navigation.goBack();
          }}/>
      </ScrollView>
    );
  }
}
