"""
AIRWISE - Processing data (helpers)

Purpose:
    Helper functions for processing data

Required Libraries:
    -pandas
    -numpy
    -datetime
"""

import numpy as np
import pandas as pd
import datetime

def convert_timestamp(df, col_name_timestamp):
    """
    Convert timestamps to epoch in the format yyyy-mm-ddThh:mm:ss when there
        is valid GPS data
    :param df: DataFrame, container of the data
    :param col_name_time: String, name of the column of the timestamps
    :return: DataFrame with an added column of epoch time
    """

    # lists to hold information about times
    years = []
    months = []
    days = []
    hours = []
    minutes = []
    seconds = []
    times_epoch = []
    x_timestamp = df.columns.get_loc(col_name_timestamp)

    # extract information (yyyy-mm-ddThh:mm:ss)
    for y in range(0, len(df)):
        timestamp = df.iat[y, x_timestamp]
        # check to make sure there is data
        if isinstance(timestamp, str) == True:
            # add each piece of data to its list (at same index each time)
            timestamp = df.iat[y, x_timestamp]
            years.append(timestamp[0:4])
            months.append(timestamp[5:7])
            days.append(timestamp[8:10])
            hours.append(timestamp[11:13])
            minutes.append(timestamp[14:16])
            seconds.append(timestamp[17:19])

        # if there is no data, add nan values to each list
        elif df.iat[y, x_gps_ok] == False:
            years.append(np.nan)
            months.append(np.nan)
            days.append(np.nan)
            hours.append(np.nan)
            minutes.append(np.nan)
            seconds.append(np.nan)

    # convert all units of time from strings to integers
    lists_time = [years, months, days, hours, minutes, seconds]
    for i in range(0, len(lists_time)):
        for j in range(0, len(lists_time[i])):
            try:
                lists_time[i][j] = int(lists_time[i][j])
            except:
                lists_time[i][j] = np.nan

    # convert to upix time
    times_datetimes = []
    for i in range(0, len(lists_time[0])):
        # if there is data, add it
        try:
            time_datetime = datetime.datetime(years[i], months[i], days[i], hours[i], minutes[i], seconds[i])
            times_datetimes.append(time_datetime)
        except:
            times_datetimes.append(np.nan)

    # convert times from datetime objects to epoch (float)
    times_epoch = []
    for time_datetime in times_datetimes:
        try:
            time_epoch = time_datetime.timestamp()
            times_epoch.append(time_epoch)
        except:
            times_epoch.append(np.nan)

    # add the epoch times to the dataframe
    df["Epoch"] = times_epoch

    return df

def convert_epoch(df, col_epoch, unit_time, col_time, y_start=0, y_end=-1):
    """
    Converts epoch times to seconds after the first timestamp.
    :param df: DataFrame, contains the data
    :param unit_time: String, specifies the unit of time to convert to
        for seconds: must equal 's' or contain 'sec'
        for minutes: must equal 'm' or contain 'min'
        for hours:   must equal 'h' or contain 'ho'
        for days:    all else
    :param col_time: String, desired column name of the updated time column
    :param y_start: Integer, row index of the first valid starting time
    :return: DataFrame, with an added column for time in seconds after start
    """

    # get ending index of valid data range
    x_col_epoch = df.columns.get_loc(col_epoch)
    if y_end == -1:
        y_end = len(df) - 1

    # in the valid range, find the smallest value to be the starting time
    # (accounts for unordered data, i.e. station data being reversed)
    times_list = df[col_epoch].tolist()[y_start:y_end]
    while 0 in times_list:
        times_list.remove(0)
    t_0 = np.nanmin(times_list)

    # populate times
    times = []
    for epoch in df[col_epoch]:
        # time in seconds
        time = epoch - t_0

        # get time in minutes if unit isn't seconds
        if unit_time != "s" and "sec" not in unit_time:
            time = time / 60.0

            # get time in hours if unit isn't minutes
            if unit_time != "m" and "min" not in unit_time:
                time = time / 60

                # get time in days if unit isn't hours
                if unit_time != "h" and "ho" not in unit_time:
                    time = time / 24

        # add converted time to times of the appropriate unit
        times.append(time)

    # add column to the dataframe
    df[col_time] = times

    return df

def convert_temps(df, temp_col):
    """
    Converts temperatures from F to C and allows collect_data_station to
    work without making separate functions for 7/10-7/13 and 7/28-7/30 data
    :param df: DataFrame, contains data to be converted
    :param temp_col: String, name of temperature F column
    :return: list, temperatures converted to C
    """

    # store converted temperatures
    temperatures_c = []

    # loop through temperature values in dataframe
    i_temp = df.columns.get_loc(temp_col)
    for i in range(0, len(df[temp_col])):
        temp_c = float((df.iat[i, i_temp] - 32) * (5 / 9))
        temperatures_c.append(temp_c)

    return temperatures_c

def rescale_columns(df, indices):
    """
    Rescales data
    :param df: DataFrame, container of data
    :param indices: list, contains tuples of form (index of the column to
        rescale, factor to divide it by to rescale)
    :return: DataFrame with rescaled data
    """

    # loop through each type of data to be scaled
    for tuple in indices:
        i_col = tuple[0]
        scaling_factor = tuple[1]

        # loop through every row in the dataframe
        for i_row in range(0, len(df)):
            new_value = float(df.iat[i_row, i_col] / scaling_factor)
            df.iat[i_row, i_col] = new_value

    return df

def check_values(df, info, name_col_bool):
    """
    Check if values are in a valid range and updates the "Valid" column to
        False if it isn't
    :param df: DataFrame, container of data
    :param info: list, stores tuples of form (name_col, min, max,
        bracket_type), where name_col is a string and the name of the column
        to check, (min, max) are numbers that form an interval of acceptable
        values, and bracket_type is the type of bracket to use for each value
        (either "open" or "closed")
    :param name_col_bool: string, name of the column that contains boolean
        values that determine if that row is valid or not
    :return: DataFrame, filtered
    """

    # get index of column with boolean values
    i_col_bool = df.columns.get_loc(name_col_bool)

    # initialize total count of rows invalidated as 0
    count_total = 0

    # loop through each tuple
    for tuple in info:
        count_indiv = 0
        name_col = tuple[0]
        min = tuple[1]
        max = tuple[2]
        bracket_type = tuple[3]

        # get position of the column, if it exists
        if name_col in df.columns:
            i_x = df.columns.get_loc(name_col)

            # loop through each row of the dataframe
            len_df = len(df)
            for i_y in range(0, len_df):
                item = df.iat[i_y, i_x]

                # invalidate row if data is out of range
                if bracket_type == "open":
                    if item <= min or item >= max:
                        count_indiv += 1
                        if df.iat[i_y, i_col_bool] == True:
                            df.iat[i_y, i_col_bool] = False
                            count_total += 1

                elif bracket_type == "closed":
                    if item < min or item > max:
                        count_indiv += 1
                        if df.iat[i_y, i_col_bool] == True:
                            df.iat[i_y, i_col_bool] = False
                            count_total += 1

            # print individual number of invalid rows (includes overlapping)
            print("Total invalid rows for ", name_col, ": ", count_indiv, sep='')

    # print total removed
    print("Total rows invalidated:", count_total, "\n")

    return df

def add_column(df, col_name, col_value):
    """
    Add a list of columns of a singular value to a DataFrame (usually adding
    the type of sensor to a dataframe that doesn't already have a column
    specifying that)
    :param df: DataFrame, container of data
    :param col_name: String, the name of the column to add
    :param col_value: any type, the value to fill the column with
    :return: DataFrame with added column
    """

    # make a list of values the length of the dataframe
    values = []
    for i in range(0, len(df)):
        values.append(col_value)

    # add the column to the dataframe
    df[col_name] = values

    return df