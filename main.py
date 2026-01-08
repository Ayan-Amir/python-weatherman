import argparse
import csv
from datetime import date
from pathlib import Path
from dataclasses import dataclass
from constants import DATE_KEY, MAX_TEMP_KEY, MIN_TEMP_KEY, MAX_HUMIDITY_KEY

RED = "\033[31m"
BLUE = "\033[34m"
RESET = "\033[0m"

@dataclass
class WeatherReading:
    temp_date: int
    max_temp: int
    min_temp: int
    humidity: int

@dataclass
class YearlyReading:
    year: int
    highest_temp: int
    highest_date: int
    lowest_temp: int
    lowest_date: int
    humidity: int
    humidity_date: int

@dataclass
class MonthlyReading:
    year: int
    month: int
    avg_highest_temp: int
    avg_lowest_temp: int
    avg_humidity: int



def parse_int(value):
    """
    Convert a given value into an integer.

    If the value is an empty string (""), it returns None.
    it handles the exception and also returns None.

    Args:
        value: The input value to be converted. Can be a string, number.

    Returns:
        int: The converted integer value if successful.
        None: If the value is invalid, empty, or cannot be converted.
    """
    try:
        return int(value) if value != "" else None
    except (ValueError, TypeError):
        return None

def parse_weather_file(file_path):
    readings = []

    with file_path.open("r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                date_text = row.get(DATE_KEY)
                if date_text is None:
                    continue

                year, month, day = [parse_int(part) for part in date_text.split("-")]
                if None in (year, month, day):
                    continue

                reading_date = date(year, month, day)

                reading = WeatherReading(
                    temp_date = reading_date,
                    max_temp = parse_int(row.get(MAX_TEMP_KEY)),
                    min_temp = parse_int(row.get(MIN_TEMP_KEY)),
                    humidity = parse_int(row.get(MAX_HUMIDITY_KEY))
                )
                readings.append(reading)
            except Exception as e:
                print(f"Error row: {e}")
                continue
    return readings

def load_readings(report_dir):
    readings = []

    for file_path in report_dir.rglob("*.txt"):
        reading = parse_weather_file(file_path)
        readings.extend(reading)

    return readings

def calculate_yearly_report(readings, year):
    year_readings = [reading for reading in readings if reading.temp_date.year == year]

    if not year_readings:
        raise ValueError(f"No data available for year {year}.")

    highest_temp = max(
        (temp for temp in year_readings if temp.max_temp is not None),
        key=lambda reading: reading.max_temp,
        default=None
    )

    lowest_temp = min(
        (temp for temp in year_readings if temp.min_temp is not None),
        key=lambda reading: reading.min_temp,
        default=None
    )

    humidity = max(
        (temp for temp in year_readings if temp.humidity is not None),
        key=lambda reading: reading.humidity,
        default=None
    )

    if highest_temp is None or lowest_temp is None or humidity is None:
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



def generate_yearly_report(readings, year):
    parsed_year = parse_int(year)

    report = calculate_yearly_report(readings, parsed_year)
    
    highest_line = f"Highest: {report.highest_temp}C on {report.highest_date.strftime('%B %d')}"
    lowest_line = f"Lowest: {report.lowest_temp}C on {report.lowest_date.strftime('%B %d')}"
    humidity_line = f"Humidity: {report.humidity}% on {report.humidity_date.strftime('%B %d')}"
    
    print(f"{highest_line} \n{lowest_line} \n{humidity_line}")

def calculate_monthly_report(readings, year, month):
    month_readings = [reading for reading in readings if reading.temp_date.year == year and reading.temp_date.month == month]

    if not month_readings:
        raise ValueError(f"No data available for year {year}-{month}.")

    valid_highs = [temp.max_temp for temp in month_readings if temp.max_temp is not None]
    valid_lows = [temp.min_temp for temp in month_readings if temp.min_temp is not None]
    valid_humidity = [temp.humidity for temp in month_readings if temp.humidity is not None]

    if not (valid_highs and valid_lows and valid_humidity):
        raise ValueError(f"Incomplete data for {year}-{month}.")

    avg_highest_temp = round(sum(valid_highs) / len(valid_highs))
    avg_lowest_temp = round(sum(valid_lows) / len(valid_lows))
    avg_humidity = round(sum(valid_humidity) / len(valid_humidity))

    return MonthlyReading(
        year = year,
        month = month,
        avg_highest_temp = avg_highest_temp,
        avg_lowest_temp = avg_lowest_temp,
        avg_humidity = avg_humidity,
    )


def generate_monthly_report(readings, year, month):
    parsed_year = parse_int(year)
    parsed_month = parse_int(month)

    report = calculate_monthly_report(readings, parsed_year, parsed_month)
    
    highest_line = f"Highest Average: {report.avg_highest_temp}C"
    lowest_line = f"Lowest Average: {report.avg_lowest_temp}C"
    humidity_line = f"Average Mean Humidity: {report.avg_humidity}%"

    print(f"{highest_line} \n{lowest_line} \n{humidity_line}")

def generate_monthly_chart_report(readings, year, month):
    parsed_year = parse_int(year)
    parsed_month = parse_int(month)

    month_readings = [reading for reading in readings if reading.temp_date.year == parsed_year and reading.temp_date.month == parsed_month]

    if not month_readings:
        raise ValueError(f"No data available for year {parsed_year}-{parsed_month}.")

    month_name = month_readings[0].temp_date.strftime("%B")

    print(f"{month_name} {parsed_year}\n")

    for reading in month_readings:
        day = reading.temp_date.day

        if reading.max_temp is not None:
            max_bar = "+" * abs(reading.max_temp)
            print(f"{day:02d} {RED}{max_bar}{RESET} {reading.max_temp}C")

        if reading.min_temp is not None:
            min_bar = "+" * abs(reading.min_temp)
            print(f"{day:02d} {BLUE}{min_bar}{RESET} {reading.min_temp}C")

def build_arg_parser():
    parser = argparse.ArgumentParser(description = "A program that generate weather report")

    parser.add_argument("report_dir", type = Path)
    parser.add_argument("-e", "--year-reports", dest = "year_reports", type=int)
    parser.add_argument("-a", "--month-report", dest="month_reports")
    parser.add_argument("-c", "--month-chart-report", dest="month_chart_reports")

    return parser

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    readings = load_readings(args.report_dir)

    if args.year_reports:
        generate_yearly_report(readings, args.year_reports)

    if args.month_reports:
        year, month = args.month_reports.split("/")
        generate_monthly_report(readings, year, month)

    if args.month_chart_reports:
        year, month = args.month_chart_reports.split("/")
        generate_monthly_chart_report(readings, year, month)

if __name__ == "__main__":
    main()
