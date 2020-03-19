# covid-19

A collection of tools for understanding the global novel Coronavirus pandemic.

## Installation

1. Make sure you have `tkinter` installed if you want to generate graphs
1. `pipenv shell`
1. `pipenv install`
1. `npm install`
1. `python data/retrieve_data.py`
   - I want to be very clear that this isn't my data.
     - It's from https://github.com/CSSEGISandData/COVID-19
       - Which is the source data for https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html
     - Wikipedia
     - UIA
     - Google DataSet Publishing Language
     - GitHub datasets
1. `python dist/data/load_data.py`
1. `python dist/server.py`

## Usage

1. Visit `http://localhost:3000/`
