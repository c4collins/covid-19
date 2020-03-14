from data.load_data import database, load_country_data
import os
import json
from flask import Flask, render_template
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Flask Server")


# load_country_data() # TODO: Integrate this into the normal startup flow

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/countries")
def all_countries_data():
    field_names = ['name', 'population', 'area', 'center_lat',
                   'center_lng', 'iso', 'global_region', 'land_area', 'water_area']
    sql_data = database('select', 'geography', 'country',
                        data=[], field_names=field_names)
    data = []
    for sql_datum in sql_data:
        data.append({
            field_names[i]: field_data for (i, field_data) in enumerate(sql_datum)
        })
    logger.debug(data)
    return json.dumps(data)


if __name__ == "__main__":
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=os.environ.get('PORT', 3000),
        debug=os.environ.get('FLASK_DEBUG', True),
    )
