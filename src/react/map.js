import React from "react";
import "./../stylesheets/map.less";

export default class Map extends React.Component {
  state = {
    map: null,
    countries: []
  };

  initializeMap() {
    const map = L.map("mapid").setView([23.633225, 5.606425], 2);
    this.setState({ map });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>',
      maxZoom: 19,
      minZoom: 0
    }).addTo(map);

    const { countries } = this.state;
    countries.forEach(country => {
      if (
        country.boundaries &&
        country.boundaries.length > 0
        // !country.boundaries.any(
        //   boundary => boundary[0] === 0 || boundary[1] === 0
        // ) &&
        // country.name === "Canada"
      ) {
        country.boundaries.forEach(boundary => {
          // console.log("30", country);
          // console.log("31", typeof country);
          // console.log("32", country.name);
          // console.log("33", country.boundaries);
          const country_shape = L.polygon(boundary).addTo(map);
          country_shape.bindPopup(`${country.name}`);
          // console.log(country_shape);
        });
      }
    });
  }

  getGeographicalData() {
    console.log("getting geographical data");
    let countries = [];
    return fetch("http://localhost:3000/api/countries")
      .then(response => response.json())
      .then(countryData => {
        // console.log(countryData);
        countries = countryData;
      })
      .then(() => fetch("http://localhost:3000/api/boundaries"))
      .then(response => response.json())
      .then(boundaryData => {
        console.log(boundaryData);
        Object.keys(boundaryData).forEach(boundaryId => {
          const boundary = boundaryData[boundaryId];
          // console.log(boundary);
          const countryIndex = countries.findIndex(
            country =>
              boundary.type === "country" &&
              boundary.name === country.name &&
              boundary.iso === country.iso
          );
          // console.log(boundary);
          if (
            countryIndex !== undefined &&
            countries[countryIndex] !== undefined
          ) {
            if (countries[countryIndex].boundaries) {
              countries[countryIndex].boundaries.push(boundary.boundaries);
            } else {
              countries[countryIndex].boundaries = [boundary.boundaries];
            }
          } else {
            if (
              countryIndex !== undefined &&
              countries[countryIndex] !== undefined &&
              countries[countryIndex].name !== undefined
            ) {
              console.log(
                `No boundaries for ${countryIndex}:${countries[countryIndex].name}/${boundary.name}`
              );
              console.log(countries[countryIndex]);
              console.log(boundary);
            } else {
              console.log(`No boundaries for ${countryIndex}:${boundary.name}`);
            }
          }
        });
      })
      .then(() => {
        console.log("geographical data gotten", countries);
        this.setState({
          countries
        });
      });
  }

  componentDidMount() {
    console.log("component mounted");
    this.getGeographicalData().then(() => {
      console.log("initializing Map");
      this.initializeMap();
    });
  }

  render() {
    return <div id="mapid"></div>;
  }
}
