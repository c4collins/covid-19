from csv import DictReader
from os import path
import math
import pathlib
import sqlite3
import logging
from enum import Enum

logger = logging.getLogger("data_load")
logging.basicConfig(level=logging.DEBUG)


class data_processes(Enum):
    def TEXT(string): return string if string else None
    def INT(num): return int(math.floor(float(num))) if num else None
    def FLOAT(num): return float(num) if num else None


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
    # print(data)
    processed_data = {}
    for key, value in data.items():
        if mapping[key] is not None:
            logger.debug(value)
            processed_data[mapping[key]['field_name']
                           ] = mapping[key]['process'](value)
    return processed_data


def load_datafile(file_name, data_mapping, path_level=1):
    file_path = get_file_path(file_name, path_level)
    data = []
    with open(file_path, 'r') as f:
        dict_file = DictReader(f, fieldnames=list(data_mapping.keys()))
        next(dict_file)  # skip headers
        for row in dict_file:
            data.append(process_data_with_mapping(row, data_mapping))
    logger.debug(data)
    return data


def process_sql(db_path, sql_string="", sql_data=[]):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.executemany(sql_string, sql_data)
        connection.commit()


def insert_data_into_database(db_path, table_name, data, column_names, sql_data):
    sql_string = f"INSERT OR IGNORE INTO {table_name} ("
    sql_string += ", ".join(column_names)
    sql_string += ") VALUES ("
    sql_string += ", ".join(["?" for x in range(len(column_names))])
    sql_string += ")"
    logger.debug(sql_string)
    process_sql(db_path, sql_string, sql_data)


def update_database_row(db_path, table_name, data, column_names, sql_data):
    sql_string = f"UPDATE OR IGNORE {table_name} SET ("
    sql_string += ", ".join(column_names)
    sql_string += ") = ("
    sql_string += ", ".join(["?" for x in range(len(column_names))])
    sql_string += ")"
    logger.debug(sql_string)
    process_sql(db_path, sql_string, sql_data)


def database(action, db_name, table_name, data, data_mapping):
    column_names = [map['field_name']
                    for map in data_mapping.values() if map is not None]
    sql_data = [[datum[column_name]
                 for column_name in column_names] for datum in data]
    db_path = get_file_path(f"{db_name}.sqlite3")
    if action == 'insert':
        insert_data_into_database(
            db_path, table_name, data, column_names, sql_data)
    if action == 'update':
        insert_data_into_database(
            db_path, table_name, data, column_names, sql_data)
        update_database_row(
            db_path, table_name, data, column_names, sql_data)


def process_datafile(file_name, data_mapping, db_name='geography', table_name="boundary_point", db_action='insert', path_level=2):
    data = load_datafile(file_name, data_mapping)
    # insert_data_into_database(db_name, table_name, data, data_mapping)
    database(db_action, db_name, table_name, data, data_mapping)


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
        db_action="update"
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
        db_action="update"
    )

    # 'google_dataset_publishing_language_center_lat_lng.csv'
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
        db_action="update"
    )


if __name__ == "__main__":
    load_country_data()
