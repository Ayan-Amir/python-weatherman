import argparse
import csv
from datetime import date
from pathlib import Path

RED = "\033[31m"
BLUE = "\033[34m"
RESET = "\033[0m"

class WeatherReading:
    def __init__(self, temp_date, max_temp, min_temp, humidity):
        self.temp_date = temp_date
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.humidity = humidity

    def __str__(self):
        return (
            f"temp_date: {self.temp_date}, "
            f"max_temp: {self.max_temp}, "
            f"min_temp: {self.min_temp}, "
            f"humidity: {self.humidity}"
        )


class YearlyReading:
    def __init__(self, year, highest_temp, highest_date, lowest_temp, lowest_date, humidity, humidity_date):
        self.year = year
        self.highest_temp = highest_temp
        self.highest_date = highest_date
        self.lowest_temp = lowest_temp
        self.lowest_date = lowest_date
        self.humidity = humidity
        self.humidity_date = humidity_date

    def __str__(self):
        return (
            f"year: {self.year}, "
            f"highest_temp: {self.highest_temp}, "
            f"highest_date: {self.highest_date}, "
            f"lowest_temp: {self.lowest_temp}, "
            f"lowest_date: {self.lowest_date}, "
            f"humidity: {self.humidity}, "
            f"humidity_date: {self.humidity_date}, "
        )


class MonthlyReading:
    def __init__(self, year, month, avg_highest_temp, avg_lowest_temp, avg_humidity):
        self.year = year
        self.month = month
        self.avg_highest_temp = avg_highest_temp
        self.avg_lowest_temp = avg_lowest_temp
        self.avg_humidity = avg_humidity


def parse_int(value):
    return int(value) if value != '' else None

def parse_weather_file(file_path):
    readings = []

    with file_path.open('r') as file:
        reader = csv.reader(file)
        header = next(reader, None)

        if not header:
            return readings

        try:
            date_idx = header.index("PKT")
            max_temp_idx = header.index("Max TemperatureC")
            min_temp_idx = header.index("Min TemperatureC")
            humidity_idx = header.index("Max Humidity")
        except ValueError:
            return readings

        for row in reader:
            date_text = row[date_idx]

            try:
                year, month, day = [parse_int(part) for part in date_text.split("-")]
                if None in (year, month, day):
                    continue
                reading_date = date(year, month, day)
            except (ValueError, TypeError):
                continue

            reading = WeatherReading(
                temp_date = reading_date,
                max_temp = parse_int(row[max_temp_idx]),
                min_temp = parse_int(row[min_temp_idx]),
                humidity = parse_int(row[humidity_idx])
            )
            readings.append(reading)
    return readings

def load_readings(report_dir):
    readings = []

    for file_path in report_dir.rglob('*.txt'):
        reading = parse_weather_file(file_path)
        readings.extend(reading)

    return readings

def calculate_yearly_report(readings, year):
    year_reading = [reading for reading in readings if reading.temp_date.year == year]

    if not year_reading:
        raise ValueError(f"No data available for year {year}.")

    highest_temp = max(
        (temp for temp in year_reading if temp.max_temp is not None),
        key=lambda reading: reading.max_temp,
        default=None
    )

    lowest_temp = min(
        (temp for temp in year_reading if temp.min_temp is not None),
        key=lambda reading: reading.min_temp,
        default=None
    )

    humidity = max(
        (temp for temp in year_reading if temp.humidity is not None),
        key=lambda reading: reading.humidity,
        default=None
    )

    if not (highest_temp and lowest_temp and humidity):
        raise ValueError(f"Incomplete data for year {year}.")

    return YearlyReading(
        year = year,
        highest_temp = highest_temp.max_temp,
        highest_date = highest_temp.temp_date,
        lowest_temp = lowest_temp.min_temp,
        lowest_date=lowest_temp.temp_date,
        humidity = humidity.humidity,
        humidity_date = humidity.temp_date
    )

def format_yearly_report(report):
    highest_line = f'Highest: {report.highest_temp}C on {report.highest_date.strftime("%B %d")}'
    lowest_line = f'Lowest: {report.lowest_temp}C on {report.lowest_date.strftime("%B %d")}'
    humidity_line = f'Humidity: {report.humidity}% on {report.humidity_date.strftime("%B %d")}'

    return f"{highest_line} \n{lowest_line} \n{humidity_line}"

def calculate_monthly_report(readings, year, month):
    month_reading = [reading for reading in readings if reading.temp_date.year == year and reading.temp_date.month == month]

    if not month_reading:
        raise ValueError(f"No data available for year {year}.")

    avg_highest_temp = round(sum(temp.max_temp for temp in month_reading if temp.max_temp is not None) / len(month_reading))

    avg_lowest_temp = round(sum(temp.min_temp for temp in month_reading if temp.min_temp is not None) / len(month_reading))

    avg_humidity = round(sum(temp.humidity for temp in month_reading if temp.humidity is not None) / len(month_reading))

    return MonthlyReading(
        year = year,
        month = month,
        avg_highest_temp = avg_highest_temp,
        avg_lowest_temp = avg_lowest_temp,
        avg_humidity = avg_humidity,
    )


def format_monthly_report(report):
    highest_line = f'Highest Average: {report.avg_highest_temp}C'
    lowest_line = f'Lowest Average: {report.avg_lowest_temp}C'
    humidity_line = f'Average Mean Humidity: {report.avg_humidity}%'

    return f"{highest_line} \n{lowest_line} \n{humidity_line}"

def calculate_monthly_chart_report(readings, year, month):
    month_reading = [reading for reading in readings if reading.temp_date.year == year and reading.temp_date.month == month]

    if not month_reading:
        raise ValueError(f"No data available for year {year}.")

    month = month_reading[0].temp_date.strftime('%B')

    print(f'{month} {year}\n')

    for reading in month_reading:
        day = reading.temp_date.day

        if reading.max_temp is not None:
            max_bar = '+' * reading.max_temp
            print(f'{day} {RED}{max_bar}{RESET} {reading.max_temp}C')

        if reading.min_temp is not None:
            min_bar = '+' * reading.min_temp
            print(f'{day:02d} {BLUE}{min_bar}{RESET} {reading.min_temp}C')

def format_monthly_chart_report(report):
    highest_line = f'Highest Average: {report.avg_highest_temp}C'
    lowest_line = f'Lowest Average: {report.avg_lowest_temp}C'
    humidity_line = f'Average Mean Humidity: {report.avg_humidity}%'

    return f"{highest_line} \n{lowest_line} \n{humidity_line}"

def build_arg_parser():
    parser = argparse.ArgumentParser(description = "A program that generate weather report")

    parser.add_argument('report_dir', type = Path)
    parser.add_argument('-e', '--year-reports', dest = 'year_reports')
    parser.add_argument('-a', '--month-report', dest='month_report')
    parser.add_argument('-c', '--month-chart-report', dest='month_chart_report')

    return parser

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    readings = load_readings(args.report_dir)

    if args.year_reports:
        report = calculate_yearly_report(readings, parse_int(args.year_reports))
        print(format_yearly_report(report))

    if args.month_report:
        year, month = args.month_report.split('/')
        report = calculate_monthly_report(readings, parse_int(year), parse_int(month))
        print(format_monthly_report(report))

    if args.month_chart_report:
        year, month = args.month_chart_report.split('/')
        calculate_monthly_chart_report(readings, parse_int(year), parse_int(month))

if __name__ == '__main__':
    main()
