//SY
import "./global"
import {Alert} from "react-native"
import Expo from "expo"

function check_login(res) {
    if (res === undefined || res === null) {
      Alert.alert('Error connecting to server');
      console.log(false);
      return false;
    }
    res = res.json()
    if (res.success) {
      global.login_status = res;
    } else {
      Alert.alert('Error', res.error);
    }
    return res.success;
  }

export function login(register) {
    let data = {
      email: this.state.email,
      password: this.state.pword
    };
    if (register) data.name = this.state.name
    let url = register ? "http://192.168.0.5:8000/api/register" : "http://192.168.0.5:8000/api/login"
    let success;
    try {
      fetch(url, {
        method: 'POST',
        body: JSON.stringify(data),
      })
        .catch(res => {console.log("fail")
          Alert.alert('Error connecting to server', res);
          this.success = false;})
        .then(res => {this.success = this.check_login(res)}, reason => {console.log("reject")
          Alert.alert('Error connecting to server', reason);
          this.success = false;});
    }
    catch (err) {
      Alert.alert("Error",err)
      this.success =false;
    }
    if (this.success) this.props.navigation.navigate('Main');
    else if (this.success === undefined) Alert.alert("Error","An unknown error occured when connecting to the server");
  }

export async function googleLogin() {
  try {
    const result = await Expo.Google.logInAsync({
      androidClientId: global.googleLoginID.android,
      scopes: ["email"]
    })
    if (result.type == "success"){
      console.log(result);
      //NOT IMPLEMENTED (Requires new backend code)
    }
  }
  catch (err) {
    Alert.alert("Google Login Error",err)
  }
}
