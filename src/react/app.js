import React from "react";
import ReactDOM from "react-dom";
import Map from "./map";

class App extends React.Component {
  render() {
    fetch("https://api.github.com/orgs/nodejs")
      .then(response => response.json())
      .then(data => {
        console.log(data);
      })
      .catch(error => console.error(error));
    return (
      <>
        <h1>Hello world!</h1>
        <Map />
      </>
    );
  }
}

ReactDOM.render(<App />, document.getElementById("app"));
