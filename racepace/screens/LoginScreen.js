  }
  render() {
    return (

      <View>
        <Text>{global.token}</Text>
        <Text>afsdafds</Text>
        <TextInput
          autoCorrect={false}
          ref={el => {
            this.email = el;
          }}
          onChangeText={(email) => {
            this.setState({'email': email});
          }}
          keyboardType="email-address"
          returnKeyType="go"
          placeholder="Email or Mobile Num"
          placeholderTextColor="rgba(225,225,225,0.8)"
        />
        <TextInput
          autoCorrect={false}
          ref={el => {
            this.pword = el;
          }}
          onChangeText={(pword) => {
            this.setState({ pword });
          }}
          returnKeyType="go"
          placeholder="Password"
          placeholderTextColor="rgba(225,225,225,0.8)"
        />
        <Image source={require('../assets/cat.jpeg')} />
        <Button onPress={this.login} title="Login" />
      </View>
    );
  }
}
