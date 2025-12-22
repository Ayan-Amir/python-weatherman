import unittest
from datetime import date

import main


class TestCalculateYearlyReport(unittest.TestCase):
    def test_incomplete_when_all_max_temps_none(self):
        readings = [
            main.WeatherReading(date(2001, 1, 1), None, 1, 50),
            main.WeatherReading(date(2001, 1, 2), None, 2, 60),
        ]
        with self.assertRaisesRegex(ValueError, r"Incomplete data for year 2001\."):
            main.calculate_yearly_report(readings, 2001)

    def test_incomplete_when_all_min_temps_none(self):
        readings = [
            main.WeatherReading(date(2001, 1, 1), 10, None, 50),
            main.WeatherReading(date(2001, 1, 2), 12, None, 60),
        ]
        with self.assertRaisesRegex(ValueError, r"Incomplete data for year 2001\."):
            main.calculate_yearly_report(readings, 2001)

    def test_incomplete_when_all_humidity_none(self):
        readings = [
            main.WeatherReading(date(2001, 1, 1), 10, 1, None),
            main.WeatherReading(date(2001, 1, 2), 12, 2, None),
        ]
        with self.assertRaisesRegex(ValueError, r"Incomplete data for year 2001\."):
            main.calculate_yearly_report(readings, 2001)

    def test_no_data_for_year(self):
        readings = [main.WeatherReading(date(2002, 1, 1), 10, 1, 50)]
        with self.assertRaisesRegex(ValueError, r"No data available for year 2001\."):
            main.calculate_yearly_report(readings, 2001)

    def test_happy_path(self):
        readings = [
            main.WeatherReading(date(2001, 1, 1), 10, 1, 50),
            main.WeatherReading(date(2001, 6, 1), 25, 5, 70),
            main.WeatherReading(date(2001, 12, 1), 20, -1, 60),
        ]
        report = main.calculate_yearly_report(readings, 2001)
        self.assertEqual(report.year, 2001)
        self.assertEqual(report.highest_temp, 25)
        self.assertEqual(report.highest_date, date(2001, 6, 1))
        self.assertEqual(report.lowest_temp, -1)
        self.assertEqual(report.lowest_date, date(2001, 12, 1))
        self.assertEqual(report.humidity, 70)
        self.assertEqual(report.humidity_date, date(2001, 6, 1))


if __name__ == "__main__":
    unittest.main()

