import React from "react";
import ReactDOM from "react-dom";
import Map from "./map";

class App extends React.Component {
  render() {
    return (
      <>
        <Map />
      </>
    );
  }
}

ReactDOM.render(<App />, document.getElementById("app"));
