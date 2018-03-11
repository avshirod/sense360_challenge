#!/usr/bin/env python
#
# Returns Home location for a number of visits based on following criteria:
# - Time spent at the location between 8pm and 8am
# - Must have spent minimum of 30 hours at this location between 8pm and 8am
#
# Created on:   03/11/2018      Aditya Shirode
# Modified on:  03/11/2018      Aditya Shirode
#

import logging
import datetime

import pandas as pd


DATEFORMAT = "%m/%d/%Y %H:%M:%S"


class Visit:
    """
    A "visit" is any place a user travels to

    latitude: float (e.g. 45.12345)
    longitude: float (e.g. -118.12345)
    arrival_time_local: datetime (e.g. 5/30/2015 10:12:35)
    departure_time_local: datetime (e.g. 5/30/2015 18:12:35)
    """

    def __init__(self, lat, lon, arrival_time, departure_time):
        # self.id = next(new_visit_id)
        self.lat = lat
        self.lon = lon
        self.arrival_time = self.parse_time(arrival_time)
        self.departure_time = self.parse_time(departure_time)
        self.time_spent = self.departure_time - self.arrival_time

    def parse_time(self, t):
        if type(t) is datetime.datetime:
            return t
        else:
            try:
                return datetime.datetime.strptime(t, DATEFORMAT)
            except ValueError:
                # Try other possible formats, generic parsing, etc.
                return None

    def get_time_spent(self):
        return self.time_spent.seconds / 3600

    def is_visit_within_valid_period(self):
        """ Check if given visit overlaps with a time period between 8pm and 8am """
        date_visit_start = self.arrival_time.date()
        valid_period_start = datetime.datetime.combine(date_visit_start, datetime.time(8))
        valid_period_end = valid_period_start + datetime.timedelta(hours=12)
        return not (valid_period_start <= self.arrival_time < self.departure_time <= valid_period_end)

    def __repr__(self):
        return "Was at ({lat}, {lon}) between [{start} -- {end}]".format(
            lat=self.lat, lon=self.lon, start=self.arrival_time, end=self.departure_time
        )


def identify_home(visits):
    """ Takes in a list of "visits" and returns the possible home location
    :type visits: list of Visit objects
    :rtype: (lat, lon) for predicted home location
    """
    # Get visits within our period in question (8pm -- 8am)
    valid_visits = [vars(v) for v in visits if v.is_visit_within_valid_period()]

    # Convert to a dataframe for easy calculations
    df = pd.DataFrame(valid_visits)

    # Calculate the time spent for visit in seconds
    df['time_spent_seconds'] = df['time_spent'].apply(lambda d: d.total_seconds())

    # Consider precise location co-ordinates up to 3 decimal points
    df[['lat', 'lon']] = df[['lat', 'lon']].applymap(lambda x: '{:.3f}'.format(x))

    # Group visits by location and calculate total time spent
    time_spent_by_location = df.groupby(['lat', 'lon'])[['time_spent_seconds']].sum()

    # The threshold is set to 30 hours; visits by location above this threshold should be considered
    time_spent_threshold = 30 * 60 * 60  # seconds

    # Get locations that cross the threshold
    possible_locations = time_spent_by_location[time_spent_by_location['time_spent_seconds'] > time_spent_threshold]

    # If no location with more than 30 hours spent during the requisite period, return -1
    if possible_locations.empty:
        logging.info("No possible home location found")
        return (-1, -1)

    # Get the location most time was spent at
    possible_home_location = possible_locations.nlargest(1, 'time_spent_seconds')

    return possible_home_location.index.tolist()[0]


def example_run():
    """ Modify this function to test out 'identify_home()' function """
    # Update this list with actual values
    visit_data = [
        ('lat', 'lon', 'arrival', 'departure'),
    ]

    # Create Objects for each Visit
    parsed_visit_data = [Visit(*v) for v in visit_data]

    # Get results
    identify_home(parsed_visit_data)


if __name__ == '__main__':
    print('Refer to Jupyter notebook for execution details')
