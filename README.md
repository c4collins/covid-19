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

### Server

1. `python dist/data/load_data.py`
1. `python dist/server.py`
1. Visit `http://localhost:3000/`

### Charts

1. `python data/generate_charts.py`
1. wait. NOTE: This takes a long time the first time as it generates a chart for each day of data for each country_region in the data and then for the whole world too, but it only creates a new image if the old one doesn't exist - so after you do the first run it's as fast as it was before but you have a bunch of extra charts to play with. Seriously, go walk your dog or something while this runs the first time; it's like 45 seconds per day of charts created on my fairly new gaming desktop.
   1. Since adding animated GIFs this takes even longer!
1. look at images

## To-Do

- finish the map geography (just load the geojson file rather than using the db)
- add date to map
- add sortable data charts to website
- auto-generate charts every day
- show charts on website
- dockerize
- deploy website somewhere public
