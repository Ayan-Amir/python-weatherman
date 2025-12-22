import argparse
import csv
from datetime import date
from pathlib import Path

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


def parse_int(value):
   return int(value) if value != '' else None

def parse_weather_file(file_path):
    readings = []

    with file_path.open('r') as file:
        reader = csv.reader(file)
        header = next(reader, None)

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
                reading_date = date(year, month, day)
            except ValueError:
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
        key=lambda reading: reading.max_temp
    )

    lowest_temp = min(
        (temp for temp in year_reading if temp.min_temp is not None),
        key=lambda reading: reading.min_temp
    )

    humidity = max(
        (temp for temp in year_reading if temp.humidity is not None),
        key=lambda reading: reading.humidity
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

def build_arg_parser():
    parser = argparse.ArgumentParser(description = "A program that generate weather report")

    parser.add_argument('report_dir', type = Path)
    parser.add_argument('-e', '--year-reports', dest = 'year_reports', required=True)

    return parser

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    readings = load_readings(args.report_dir)

    if args.year_reports:
        report = calculate_yearly_report(readings, parse_int(args.year_reports))
        print(format_yearly_report(report))

if __name__ == '__main__':
    main()
