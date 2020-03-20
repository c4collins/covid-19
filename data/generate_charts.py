"""Creates graphs from COVID-19 data"""
from collections import OrderedDict
from os import path
from pprint import pformat
import csv
import datetime
import logging
import pathlib
from matplotlib import pyplot as plt


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_file_path(file_name):
    return path.join(pathlib.Path(__file__).parents[0].absolute(), file_name)


def get_daily_data():
    new_daily_data = {}
    start_date = datetime.date(2020, 1, 22)
    current_date = datetime.date.today()
    target_date = start_date
    fieldnames = ['Province/State', 'Country/Region', 'Last Update',
                  'Confirmed', 'Deaths', 'Recovered', 'Latitude', 'Longitude']
    while target_date <= current_date:
        formatted_target_date = target_date.strftime("%m-%d-%Y")
        file_path = get_file_path(f"csse_daily_{formatted_target_date}.csv")
        try:
            with open(file_path, 'r') as datafile:
                reader = csv.DictReader(datafile, fieldnames=fieldnames)
                next(reader)  # skip headers
                for row in reader:
                    target_data = {key: value for key, value in row.items()}
                    country_region = target_data['Country/Region'].strip(' *')
                    province_state = target_data['Province/State'].strip(' *')

                    # Some of this data needs to be helped along
                    if country_region == "Viet Nam":
                        country_region = "Vietnam"
                    elif country_region == "Republic of the Congo" or country_region == "Congo (Brazzaville)" or country_region == "Congo (Kinshasa)":
                        country_region = "Congo"
                    elif country_region == "Czech Republic":
                        country_region = "Czechia"
                    elif country_region == "Hong Kong SAR":
                        country_region = "Hong Kong"
                    elif country_region == "Iran (Islamic Republic of)":
                        country_region = "Iran"
                    elif country_region == "Macao SAR":
                        country_region = "Macau"
                    elif country_region == "Mainland China":
                        country_region = "China"
                    elif country_region == "Republic of Moldova":
                        country_region = "Moldova"
                    elif country_region == "Republic of Ireland":
                        country_region = "Ireland"
                    elif country_region == "Korea, South" or country_region == "Republic of Korea":
                        country_region = "South Korea"
                    elif country_region == "Russian Federation":
                        country_region = "Russia"
                    elif country_region == "Gambia, The":
                        country_region = "The Gambia"
                    elif country_region == "UK":
                        country_region = "United Kingdom"
                    elif country_region == "Holy See":
                        country_region = "Vatican City"
                    elif country_region == "":
                        country_region = "Unknown"

                    if country_region is not None and country_region != '':
                        try:
                            new_daily_data[country_region]
                        except KeyError:
                            new_daily_data[country_region] = {}

                    if province_state is None or province_state == '':
                        province_state = "Entire"

                    try:
                        new_daily_data[country_region][province_state]
                    except KeyError:
                        new_daily_data[country_region][province_state] = OrderedDict(
                        )

                    if province_state is not None and province_state != '':
                        new_daily_data[country_region][province_state][formatted_target_date] = target_data
                    elif country_region is not None and country_region != '':
                        new_daily_data[country_region][formatted_target_date] = target_data
                    else:
                        logger.warning("Data has no location")
                        new_daily_data[formatted_target_date] = target_data

        except FileNotFoundError:
            logger.warning("{formatted_target_date} file not read")
        target_date += datetime.timedelta(days=1)
    return new_daily_data


def create_daily_data_line_chart_for_one_country(country_region, record):
    logger.debug(pformat(record))
    logger.info(f"'{country_region}'")
    logger.debug(type(record))
    for province_state, daily_data in record.items():
        logger.info(f"'{province_state}'")
        _, ax = plt.subplots()
        dates = [
            datetime.datetime.strptime(key, "%m-%d-%Y") for key in daily_data.keys()
        ]
        confirmed = []
        deaths = []
        recovered = []
        for data in daily_data.values():
            # pprint(data)
            if data['Confirmed']:
                confirmed.append(int(data['Confirmed']))
            else:
                confirmed.append(0)
            if data['Deaths']:
                deaths.append(int(data['Deaths']))
            else:
                deaths.append(0)
            if data['Recovered']:
                recovered.append(int(data['Recovered']))
            else:
                recovered.append(0)
        plt.plot(dates, confirmed, color='orange', label="Confirmed")
        plt.plot(dates, deaths, color='red', label="Deaths")
        plt.plot(dates, recovered, color='green', label="Recovered")

        ticks_divisor = 5
        if len(dates) > ticks_divisor:
            ax.xaxis.set_major_locator(
                plt.MaxNLocator(
                    int(
                        len(dates) / ticks_divisor
                    )
                )
            )

        plt.xlabel('Date')
        plt.ylabel('Number')
        date_string = max(dates).strftime("%m-%d-%Y")
        title = f"{country_region}-{province_state} daily COVID-19 status upto {date_string}"
        plt.title(title)
        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.05),
            shadow=True,
            ncol=3,
        )
        # plt.show()
        save_file_path = get_file_path(
            path.join(
                'charts',
                f"{country_region}-{province_state}-{date_string}.png"
            )
        )
        logger.info(f"Saving chart for {title} to {save_file_path}")
        plt.savefig(save_file_path)
        plt.close()


def create_world_chart(data):

    confirmed = {}
    recovered = {}
    deaths = {}
    for country_name, country_report in data.items():
        logger.info(country_name)
        logger.debug(country_report)
    global_data = {
        'confirmed': confirmed,
        'recovered': recovered,
        'deaths': deaths
    }
    # Add data groups by date
    # Generate chart


if __name__ == "__main__":
    pathlib.Path(get_file_path('charts')
                 ).mkdir(parents=True, exist_ok=True)
    daily_data = get_daily_data()
    logger.debug(pformat(daily_data.keys()))
    # for country_name, country_report in daily_data.items():
    #     create_daily_data_line_chart_for_one_country(
    #         country_name, daily_data[country_name])
    create_world_chart(daily_data)
