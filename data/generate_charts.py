"""Creates graphs from COVID-19 data"""
from collections import OrderedDict
from os import path
from pprint import pformat
import csv
import datetime
import logging
import pathlib
import imageio
from matplotlib import pyplot as plt


logging.basicConfig(level=logging.INFO)
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


def create_daily_data_line_chart_for_one_country(country_region, record, generate_gif=True):
    logger.debug(pformat(record))
    logger.info(f"'{country_region}'")
    logger.debug(type(record))
    for province_state, daily_data in record.items():
        logger.info(f"'{province_state}'")
        image_file_paths = []
        dates = [
            datetime.datetime.strptime(key, "%m-%d-%Y") for key in daily_data.keys()
        ]

        confirmed = []
        deaths = []
        recovered = []
        for data in daily_data.values():
            confirmed.append(get_int_value(data['Confirmed']))
            deaths.append(get_int_value(data['Deaths']))
            recovered.append(get_int_value(data['Recovered']))

        for i in range(len(dates)):
            loop_dates = dates[:i+1]
            date_string = max(loop_dates).strftime("%m-%d-%Y")
            save_file_path = get_file_path(
                path.join(
                    'charts',
                    f"{country_region}-{province_state}-{date_string}.png"
                )
            )
            image_file_paths.append(save_file_path)
            if path.exists(save_file_path):
                logger.warning(f"{save_file_path} already exists")
                continue

            _, ax = plt.subplots()
            plt.plot(loop_dates, confirmed[:i+1],
                     color='orange', label="Confirmed")
            plt.plot(loop_dates, deaths[:i+1], color='red', label="Deaths")
            plt.plot(loop_dates, recovered[:i+1],
                     color='green', label="Recovered")

            ticks_divisor = 5
            if len(loop_dates) > ticks_divisor:
                ax.xaxis.set_major_locator(
                    plt.MaxNLocator(
                        int(
                            len(loop_dates) / ticks_divisor
                        )
                    )
                )

            plt.xlabel('Date')
            plt.ylabel('Number')
            title = f"{country_region}-{province_state} daily COVID-19 status upto {date_string}"
            plt.title(title)
            ax.legend(
                loc='upper center',
                bbox_to_anchor=(0.5, -0.05),
                shadow=True,
                ncol=3,
            )
            # plt.show()
            logger.info(f"Saving chart for {title} to {save_file_path}")
            plt.savefig(save_file_path)
            plt.close()

        if generate_gif:
            gif_path = get_file_path(
                path.join(
                    'charts', f"{country_region}-{province_state}-{date_string}.gif")
            )
            if not path.exists(gif_path):
                imageio.mimsave(
                    gif_path,
                    [
                        imageio.imread(filename) for filename in image_file_paths
                    ]
                )


def get_int_value(input, country_region='unknown', province_state='unknown'):
    try:
        int_val = int(input)
    except ValueError:
        logger.warning(
            f"{country_region}-{province_state} - got `{input}`, saved 0")
        int_val = 0
    return int_val


def create_world_chart(data, generate_gif=True):

    # Add data groups by date
    confirmed = OrderedDict()
    recovered = OrderedDict()
    deaths = OrderedDict()
    dates = []
    cumulative_confirmed = 0
    cumulative_recovered = 0
    cumulative_deaths = 0
    image_file_paths = []
    for country_region, country_report in data.items():
        logger.info(country_region)
        logger.debug(country_report)
        for province_state, province_state_report in country_report.items():
            logger.debug(province_state)
            logger.debug(province_state_report)
            for date_string, daily_data in province_state_report.items():
                logger.debug(date_string)
                logger.debug(daily_data)

                province_state_confirmed = get_int_value(
                    daily_data['Confirmed'])
                province_state_recovered = get_int_value(
                    daily_data['Recovered'])
                province_state_deaths = get_int_value(daily_data['Deaths'])

                try:
                    confirmed[date_string] += province_state_confirmed
                    recovered[date_string] += province_state_recovered
                    deaths[date_string] += province_state_deaths
                except KeyError:
                    confirmed[date_string] = province_state_confirmed
                    recovered[date_string] = province_state_recovered
                    deaths[date_string] = province_state_deaths
                    dates.append(date_string)

                cumulative_confirmed += province_state_confirmed
                cumulative_recovered += province_state_recovered
                cumulative_deaths += province_state_deaths

    global_data = {
        'confirmed': confirmed,
        'recovered': recovered,
        'deaths': deaths,
        'cumulative_confirmed': cumulative_confirmed,
        'cumulative_recovered': cumulative_recovered,
        'cumulative_deaths': cumulative_deaths,
    }
    logger.info(global_data)

    # Generate chart(s)
    date_dates = sorted([datetime.datetime.strptime(
        date_string, "%m-%d-%Y") for date_string in set(dates)])
    for i in range(len(date_dates)):
        loop_dates = date_dates[:i+1]
        logger.debug(loop_dates)
        date_string = max(loop_dates).strftime("%m-%d-%Y")

        save_file_path = get_file_path(
            path.join(
                'charts',
                f"Entire-Planet-{date_string}.png"
            )
        )
        image_file_paths.append(save_file_path)
        if path.exists(save_file_path):
            logger.warning(f"{save_file_path} already exists")
            continue

        _, ax = plt.subplots()

        logger.info(f"{len(loop_dates)} days of data")
        confirmed_values = [
            confirmed[date.strftime("%m-%d-%Y")] for date in loop_dates]
        deaths_values = [deaths[date.strftime(
            "%m-%d-%Y")] for date in loop_dates]
        recovered_values = [
            recovered[date.strftime("%m-%d-%Y")] for date in loop_dates]
        logger.debug(confirmed_values)
        logger.debug(deaths_values)
        logger.debug(recovered_values)

        plt.plot(
            loop_dates, confirmed_values,
            color='orange', label="Confirmed"
        )
        plt.plot(
            loop_dates, deaths_values,
            color='red', label="Deaths"
        )
        plt.plot(
            loop_dates, recovered_values,
            color='green', label="Recovered"
        )

        ticks_divisor = 5
        if len(loop_dates) > ticks_divisor:
            ax.xaxis.set_major_locator(
                plt.MaxNLocator(
                    int(
                        len(loop_dates) / ticks_divisor
                    )
                )
            )
        plt.xlabel('Date')
        plt.ylabel('Number')

        title = f"Entire Planet daily COVID-19 status upto {date_string}"
        logger.info(title)
        plt.title(title)
        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.05),
            shadow=True,
            ncol=3,
        )
        # plt.show()
        logger.info(f"Saving chart for {title} to {save_file_path}")
        plt.savefig(save_file_path)
        plt.close()

    if generate_gif:
        gif_path = get_file_path(
            path.join('charts', f"Entire-Planet-{date_string}.gif"))
        if not path.exists(gif_path):
            imageio.mimsave(
                gif_path,
                [imageio.imread(filename) for filename in image_file_paths]
            )


if __name__ == "__main__":
    pathlib.Path(get_file_path('charts')
                 ).mkdir(parents=True, exist_ok=True)
    daily_data = get_daily_data()
    logger.debug(pformat(daily_data.keys()))
    for country_region, country_report in daily_data.items():
        create_daily_data_line_chart_for_one_country(
            country_region, daily_data[country_region])
    create_world_chart(daily_data)
