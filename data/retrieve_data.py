import datetime
from urllib import request, parse, error as urlError
from os import environ, path
import pathlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Data Retrieval")


def get_file_path(file_name):
    return path.join(pathlib.Path(__file__).parents[0].absolute(), file_name)


def get_data_from_url(url, url_root):
    full_url = parse.urljoin(url_root, url)
    logger.info(f"Getting data from {full_url}")
    response = request.urlopen(full_url)
    data = response.read()
    text = data.decode('utf-8').replace("\r", "")
    return text


def write_file_to_disk(data, file_name, pathed_filename=False):
    file_path = file_name if pathed_filename else get_file_path(file_name)
    with open(file_path, 'w', encoding="utf-8") as f:
        f.write(data)


if __name__ == "__main__":
    # CSSE COVID-19 Data
    # csse_covid_19_daily_reports
    start_date = datetime.date(2020, 1, 22)
    current_date = datetime.date.today()
    url = "csse_covid_19_data/csse_covid_19_daily_reports/01-22-2020.csv"
    # csse_covid_19_time_series
    time_series_confirmed_url = "csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
    time_series_deaths_url = "csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
    time_series_recovered_url = "csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"
    # who_covid_19_sit_rep_time_series
    who_set_rep_url = "who_covid_19_situation_reports/who_covid_19_sit_rep_time_series/who_covid_19_sit_rep_time_series.csv"

    csse_covid19_base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
    write_file_to_disk(get_data_from_url(time_series_confirmed_url, csse_covid19_base_url),
                       'covid_confirmed.csv')
    write_file_to_disk(get_data_from_url(time_series_deaths_url, csse_covid19_base_url),
                       'covid_deaths.csv')
    write_file_to_disk(get_data_from_url(time_series_recovered_url, csse_covid19_base_url),
                       'covid_recovered.csv')
    write_file_to_disk(get_data_from_url(who_set_rep_url, csse_covid19_base_url),
                       'who_sit_rep.csv')

    target_date = start_date
    while target_date <= current_date:
        formatted_target_date = target_date.strftime("%m-%d-%Y")
        target_url = f"csse_covid_19_data/csse_covid_19_daily_reports/{formatted_target_date}.csv"

        file_path = get_file_path(f"csse_daily_{formatted_target_date}.csv")
        if not path.exists(file_path):
            try:
                file_data = get_data_from_url(
                    target_url, csse_covid19_base_url)
            except urlError.HTTPError:
                break
            write_file_to_disk(file_data, file_path, True)

        target_date += datetime.timedelta(days=1)

    # GeoJSON boundary points for countries
    # geojson_datasets_base_url = "https://raw.githubusercontent.com/datasets/geo-countries/master/"
    # country_boundary_points_url = "data/countries.geojson"

    # write_file_to_disk(get_data_from_url(country_boundary_points_url, geojson_datasets_base_url),
    #                    'country_boundary_points.geojson')
