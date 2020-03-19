from csv import DictReader
from datetime import datetime, timedelta
from enum import Enum
from glob import glob
from math import inf as Infinity
from os import path
import json
import logging
import math
import pathlib
import random
import sqlite3

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Data Loader")


class data_processes(Enum):
    def TEXT(string): return string if string else None
    def INT(num): return int(math.floor(float(num))) if num else None
    def FLOAT(num): return float(num) if num else None
    # def SELECT_GEOGRAPHY_ID(table_name): return database('select_one', 'geography', table_name, [], ['id'])


def get_file_path(file_name, level=1):
    # level=1 will give COVID-19/dist/data
    # level=2 will give COVID-19/data
    base_path = pathlib.Path(__file__).parents[level].absolute()
    logger.debug(base_path)
    logger.debug(file_name)
    file_path = path.join(base_path, 'data', file_name)
    logger.info(f"path for {file_name}: {file_path}")
    return file_path


def process_data_with_mapping(data, mapping):
    processed_data = {}
    for key, value in data.items():
        if mapping[key] is not None:
            processed_data[mapping[key]['field_name']
                           ] = mapping[key]['process'](value)
    return processed_data


def load_csv_datafile(file_name, data_mapping, path_level=1):
    file_path = get_file_path(file_name, path_level)
    data = []
    with open(file_path, 'r') as f:
        dict_file = DictReader(f, fieldnames=list(data_mapping.keys()))
        next(dict_file)  # skip headers
        for row in dict_file:
            data.append(process_data_with_mapping(row, data_mapping))
    return data


def load_geojson_datafile(file_name, data_mapping, area_type='country', path_level=1):
    logger.debug(file_name)
    logger.debug(data_mapping)
    logger.debug(path_level)
    file_path = get_file_path(file_name, path_level)

    # Get data from file
    with open(file_path, 'r') as f:
        json_data = json.loads(f.read())

    # convert data from file to usable form
    raw_data = []
    for feature in json_data['features']:
        processed_data = process_data_with_mapping(
            feature['properties'], data_mapping)
        # logger.debug(feature)
        boundary_points = []
        for a in range(len(feature['geometry']['coordinates'])):
            for b in range(len(feature['geometry']['coordinates'][a])):
                for boundary in feature['geometry']['coordinates'][a][b]:
                    boundary.append(a)  # division
                    boundary_points.append(boundary)
        processed_data['boundary_points'] = boundary_points
        raw_data.append(processed_data)
    # logger.debug(raw_data[0])

    # explode boundary points into suitable sql data
    data = []
    for feature in raw_data:
        for boundary_point in feature['boundary_points']:
            logger.debug(boundary_point)
            data_row = {
                'area_name': feature['area_name'],
                'area_iso': feature['area_iso'],
                'area_type': area_type,
            }
            data_row['lat'] = boundary_point[1]
            data_row['lng'] = boundary_point[0]
            data_row['division'] = boundary_point[2]
            data.append(data_row)
    # logger.debug(data)

    return data


def process_sql(db_path, sql_string="", sql_data=[], fetch_results=False):
    logger.info("Processing SQL data")
    logger.debug(sql_string)
    for datum in sql_data:
        for index, item in enumerate(datum):
            if ((index == 0 or index == 1) and item is not None) or\
                    ((index == 2 or index == 4) and not isinstance(item, int)) or\
                    ((index == 3) and not isinstance(item, str)):
                logger.info(datum)
                logger.info(type(item))
                logger.info(repr(item))
    data = None
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()

        if not isinstance(sql_data, list) or len(sql_data) == 1:

            logger.debug("Processing as one datum")
            cursor.execute(sql_string, sql_data)
        elif len(sql_data) > 0:
            logger.debug("Processing as data")
            cursor.executemany(sql_string, sql_data)
        else:
            logger.debug("Processing with no data")
            cursor.execute(sql_string)
        if fetch_results:
            data = cursor.fetchall()
        logger.debug(cursor)
        # logger.debug(data)
        connection.commit()
    return data


def insert_data_into_database(db_path, table_name, field_names, sql_data):
    sql_string = f"INSERT OR IGNORE INTO {table_name} ("
    sql_string += ", ".join(field_names)
    sql_string += ") VALUES ("
    sql_string += ", ".join(["?" for x in range(len(field_names))])
    sql_string += ")"
    sql_string += ";"
    process_sql(db_path, sql_string, sql_data)


def update_database_row(db_path, table_name, field_names, sql_data):
    sql_string = f"UPDATE OR IGNORE {table_name} SET ("
    sql_string += ", ".join(field_names)
    sql_string += ") = ("
    sql_string += ", ".join(["?" for x in range(len(field_names))])
    sql_string += ")"
    sql_string += ";"
    logger.debug(sql_string)
    process_sql(db_path, sql_string, sql_data)


def select_from_database(db_path, table_name, field_names):
    sql_string = "SELECT "
    sql_string += ", ".join(field_names)
    sql_string += f" FROM {table_name}"
    sql_string += ";"
    return process_sql(db_path, sql_string, None, True)


def select_one_from_database(db_path, table_name, field_names, where_field_names, where_data):
    logger.info(where_field_names)
    sql_string = (" ").join([
        "SELECT",
        ", ".join(field_names),
        f"FROM {table_name}"
    ])
    if len(where_field_names) > 0:
        sql_string = " ".join([
            sql_string,
            "WHERE",
            "AND".join(
                [f"{field_name} = ?" for field_name in where_field_names])
        ])
    sql_string += ";"

    return process_sql(db_path, sql_string, where_data, True)


def database(action, db_name, table_name, data=None, field_names=[], where_field_names=[], where_data=[]):
    if data is not None:
        sql_data = [[datum[field_name]
                     for field_name in field_names] for datum in data]
    db_path = get_file_path(f"{db_name}.sqlite3")
    if action == 'insert':
        insert_data_into_database(
            db_path, table_name, field_names, sql_data)
    elif action == 'update':
        update_database_row(
            db_path, table_name, field_names, sql_data)
    elif action == 'upsert':
        insert_data_into_database(
            db_path, table_name, field_names, sql_data)
        update_database_row(
            db_path, table_name, field_names, sql_data)
    elif action == 'select':
        return select_from_database(db_path, table_name, field_names)
    elif action == 'select_one':
        return select_one_from_database(db_path, table_name, field_names, where_field_names, where_data=where_data)
    else:
        raise KeyError('Invalid database action')


def process_datafile(file_name, data_mapping, db_name='geography', table_name="boundary_point", db_action='insert', field_names=None, area_type='country', path_level=2):
    data = []
    data_file_type = file_name.split('.')[-1]
    logger.info(f"Processing {file_name} as {data_file_type}")
    if data_file_type == "csv":
        data = load_csv_datafile(file_name, data_mapping, path_level)
    elif data_file_type == "geojson":
        data = load_geojson_datafile(
            file_name, data_mapping, area_type, path_level)
    # insert_data_into_database(db_name, table_name, data, data_mapping)
    if field_names is None:
        field_names = [map['field_name']
                       for map in data_mapping.values() if map is not None]
    database(db_action, db_name, table_name, data, field_names)


def load_country_data():
    base_country_data_mapping = {
        'FID': None,
        'COUNTRY': {
            'field_name': 'name',
            'process': data_processes.TEXT,
        },
        'ISO': {
            'field_name': 'iso',
            'process': data_processes.TEXT,
        },
        'COUNTRYAFF': None,
        'AFF_ISO': {
            'field_name': 'affiliation',
            'process': data_processes.TEXT,
        },
        'Shape__Area': {
            'field_name': 'area',
            'process': data_processes.INT,
        },
        'Shape__Length': {
            'field_name': 'perimeter',
            'process': data_processes.INT,
        },
    }
    process_datafile(
        file_name='UIA_World_Countries_Boundaries.csv',
        data_mapping=base_country_data_mapping,
        path_level=1,
        table_name="country",
        db_action="insert"
    )

    country_population_data_mapping = {
        'name': {
            'field_name': 'name',
            'process': data_processes.TEXT,
        },
        'population': {
            'field_name': 'population',
            'process': data_processes.INT,
        },
    }
    process_datafile(
        file_name='wikipedia_populations.csv',
        data_mapping=country_population_data_mapping,
        path_level=1,
        table_name="country",
        db_action="upsert",
    )

    country_area_data_mapping = {
        'country': {
            'field_name': 'name',
            'process': data_processes.TEXT,
        },
        'total_area_sqkm': {
            'field_name': 'area',
            'process': data_processes.INT,
        },
        'land_area_sqkm': {
            'field_name': 'land_area',
            'process': data_processes.INT,
        },
        'water_area_sqkm': {
            'field_name': 'water_area',
            'process': data_processes.INT,
        },
        'water_pct': None,
    }
    process_datafile(
        file_name='wikipedia_areas.csv',
        data_mapping=country_area_data_mapping,
        path_level=1,
        table_name="country",
        db_action="upsert",
    )

    country_center_data_mapping = {
        'country': {
            'field_name': 'iso',
            'process': data_processes.TEXT,
        },
        'latitude': {
            'field_name': 'center_lat',
            'process': data_processes.FLOAT,
        },
        'longitude': {
            'field_name': 'center_lng',
            'process': data_processes.FLOAT,
        },
        'name': {
            'field_name': 'name',
            'process': data_processes.TEXT,
        },
    }
    process_datafile(
        file_name='google_dataset_publishing_language_center_lat_lng.csv',
        data_mapping=country_center_data_mapping,
        path_level=1,
        table_name="country",
        db_action="upsert"
    )


def load_boundary_points():
    country_boundary_data_mapping = {

        'ADMIN': {
            'field_name': 'area_name',
            'process': data_processes.TEXT,
        },

        'ISO_A2': {
            'field_name': 'area_iso',
            'process': data_processes.TEXT,
        },

        'ISO_A3': None
    }
    process_datafile(
        file_name='country_boundary_points.geojson',
        data_mapping=country_boundary_data_mapping,
        db_action='insert',  # Do not upsert/update this cause it's >500k rows
        area_type='country',
        field_names=['area_name', 'area_iso',
                     'area_type', 'lat', 'lng', 'division']
    )


def get_csse_date_range():
    min_year, min_month, min_day = Infinity, Infinity, Infinity
    max_year, max_month, max_day = -Infinity, -Infinity, -Infinity

    daily_files = glob("data/csse_daily_*.csv")
    # random.shuffle(daily_files) # For testing
    for file_path in daily_files:
        month, day, year = [int(x) for x in file_path.split(
            "\\")[-1].split('_')[-1].split('.')[0].split('-')]
        logger.debug(f"{month}, {day}, {year}")
        if year < min_year:
            min_year = year
            min_month = month
            min_day = day
        elif year == min_year and month < min_month:
            min_month = month
            min_day = day
        elif year == min_year and month == min_month and day < min_day:
            min_day = day

        if year > max_year:
            max_year = year
            max_month = month
            max_day = day
        elif year == max_year and month > max_month:
            max_month = month
            max_day = day
        elif year == max_year and month == max_month and day > max_day:
            max_day = day

    start_date = datetime(min_year, min_month, min_day)
    end_date = datetime(max_year, max_month, max_day)

    logger.debug(f"{min_month}, {min_day}, {min_year}")
    logger.info(f"Start Date: {start_date}")
    logger.debug(f"{max_month}, {max_day}, {max_year}")
    logger.info(
        f"End Date: {end_date} (if not today or yesterday, run: retrieve_data.py)")

    return (start_date, end_date)


def load_csse_daily_covid_data():
    confirmed_data_mapping = {
        'Province/State': {
            'field_name': 'division_primary_data',
            'process': data_processes.TEXT,
        },

        'Country/Region': {
            'field_name': 'country_data',
            'process': data_processes.TEXT,
        },

        'Lat': None,
        'Long': None,
    }

    start_date, end_date = get_csse_date_range()
    target_date = start_date
    while target_date <= end_date:
        target_date_text = '{d.month}/{d.day}/{d:%y}'.format(d=target_date)
        confirmed_data_mapping[target_date_text] = {
            'field_name': target_date_text,
            'process': data_processes.INT
        }
        target_date += timedelta(days=1)
    logger.info(confirmed_data_mapping)

    file_data = load_csv_datafile(
        'covid_confirmed.csv', confirmed_data_mapping, path_level=2)
    sql_data = []
    for data_row in file_data:
        logger.debug(data_row)
        country_name = data_row['country_data']
        division_primary_id = None
        # TODO: Some of the country_data are actually country.iso and the primary data is a country name.  gotta clean up the country imports.
        division_secondary_id = None
        if country_name is None:
            continue

        logger.error(country_name)
        country_id = database('select_one', 'geography', 'country', None, [
                              'id'], where_field_names=['name'], where_data=[country_name])
        if country_id is not None and len(country_id) == 1:
            country_id = country_id[0][0]
        else:
            logger.warning(
                f"Looked up {country_name}, but got back {country_id}")
        logger.info(f"Country: {country_id} {country_name}")

        if data_row['division_primary_data'] is not None:
            division_primary_name = data_row['division_primary_data']
            division_primary_id = database('select_one', 'geography', 'division_primary', None, [
                'id'], where_field_names=['name'], where_data=[division_primary_name])
            if division_primary_id is not None and len(division_primary_id) == 1:
                division_primary_id = division_primary_id[0][0]
            else:
                division_primary_id = None

        logger.info(country_id)
        if isinstance(country_id, int):
            target_date = start_date
            while target_date <= end_date:
                target_date_text = '{d.month}/{d.day}/{d:%y}'.format(
                    d=target_date)
                sql_data.append({
                    'division_primary': division_primary_id,
                    'division_secondary': division_secondary_id,
                    'country': country_id,
                    'date': target_date_text,
                    'count': data_row[target_date_text]
                })
                target_date += timedelta(days=1)
    if len(sql_data) > 0:
        database('insert', 'geography', 'covid_confirmed', data=sql_data,
                 field_names=['division_primary', 'division_secondary', 'country', 'date', 'count'])


def load_csse_accumulated_totals_data():
    pass


def load_who_sit_rep():
    pass


if __name__ == "__main__":
    # load_country_data()
    # load_boundary_points()
    load_csse_daily_covid_data()
    load_csse_accumulated_totals_data()
    load_who_sit_rep()
