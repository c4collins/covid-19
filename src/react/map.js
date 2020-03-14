import React from "react";
import "./../stylesheets/map.less";

export default class Map extends React.Component {
  state = {
    map: null
  };

  initializeMap() {
    const map = L.map("mapid").setView([35.0023, 78.4559], 2);
    this.setState({ map });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>',
      maxZoom: 19,
      minZoom: 0
    }).addTo(map);
  }

  componentDidMount() {
    this.initializeMap();
  }

  render() {
    return <div id="mapid"></div>;
  }
}
