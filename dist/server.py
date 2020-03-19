from data.load_data import database
import os
import json
from flask import Flask, render_template
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Flask Server")


app = Flask(__name__)


@app.route("/")
def index():
    logger.info('loading / route')
    return render_template('index.html')


@app.route("/api/countries")
def all_countries_data():
    logger.info('retreiving country data')
    field_names = ['name', 'population', 'area', 'center_lat',
                   'center_lng', 'iso', 'global_region', 'land_area', 'water_area']
    sql_data = database('select', 'geography', 'country',
                        data=[], field_names=field_names)
    data = []
    for sql_datum in sql_data:
        data.append({
            field_names[i]: field_data for (i, field_data) in enumerate(sql_datum)
        })
    return json.dumps(data)


@app.route("/api/boundaries")
def all_boundaries_data():
    logger.info('retreiving boundary data')
    field_names = ['id', 'lat', 'lng', 'area_name',
                   'area_iso', 'area_type', 'division']
    sql_data = database('select', 'geography', 'boundary_point',
                        data=[], field_names=field_names)
    raw_data = []
    for sql_datum in sql_data:
        raw_data.append({
            field_names[i]: field_data for (i, field_data) in enumerate(sql_datum)
        })
    data = {}
    for sql_datum in raw_data:
        try:
            data[f"{sql_datum['division']}-{sql_datum['area_iso']}-{sql_datum['area_name']}"]['boundaries'].append(
                (sql_datum['lat'], sql_datum['lng'])
            )
        except KeyError:
            data[f"{sql_datum['division']}-{sql_datum['area_iso']}-{sql_datum['area_name']}"] = {
                'iso': sql_datum['area_iso'],
                'name': sql_datum['area_name'],
                'type': sql_datum['area_type'],
                'division': sql_datum['division'],
                'boundaries': [(sql_datum['lat'], sql_datum['lng'])]
            }
    logger.info(
        data[f"{sql_datum['division']}-{sql_datum['area_iso']}-{sql_datum['area_name']}"])
    return json.dumps(data)


if __name__ == "__main__":
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=os.environ.get('PORT', 3000),
        debug=os.environ.get('FLASK_DEBUG', True),
    )
