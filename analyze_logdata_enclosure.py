"""
AIRWISE - Plotting Data

Purpose:
    Processes and graphs data from enclosures

Inputs:
    - report-15-20260713113036.csv (7/10-7/13 station data)
    - report-15-20260730124201.csv (7/28-7/30 station data)
    - logdata7-10-26to7-13-26.CSV (7/10-7/13 green case sensor data)
    - 73026whiteneclosuretest.csv (7/28-7/30 white case sensor data)
    - logdata8-17-26to9-11-26.csv (8/17-9/11 long-term deployment data)
    - data_open_enclosure_8.14.csv (8/14 open enclosure sensor data)
    - ucsc_8.14.csv (8/14 PurpleAir station data)

Outputs:
    - Graphs

Required Libraries:
    -pandas
    -numpy
    -datetime
"""

import numpy as np
import pandas as pd
import process_logdata_helpers as process
import graph_logdata_helpers as graph
import datetime

# for viewing all columns of the dataframe
pd.set_option("display.max_columns", None)

def process_data_station(file_csv, unit_time, col_time):
    """
    Gets data from a weather station CSV file
    Converts time to epoch and temperature to C
    :param file_csv" .csv file for weather station (can be either versino)
    :return: dataframe containing all weather station data
    """

    """ order:
        0. "Station"
        1. "Date" (m/dd/yyyy)
        2. "Time" (hhmm)

        # for 7/10-7/13 data:
        3. "Temp (°F)"
        4. "RH (%)" relative humidity

        # for 7/28-7/30 data:
        3. "RH (%)" relative humidity
        4. "Temp (°F)"
    """

    data = pd.read_csv(file_csv)

    # convert time to epoch (num seconds after 00:00, January 1st, 1970)
    # lists to hold data about times
    years = []
    months = []
    days = []
    hours = []
    minutes = []
    times_epoch = []

    # get data from the "Date" column of the data (m(m)/d(d)/yy)
    for item in data["Date"]:
        # extract the month
        index = item.find("/")
        month = item[0:index]
        months.append(month)
        item = item[index + 1:len(item)]

        # extract the day
        index = item.find("/")
        day = item[0:index]
        days.append(day)
        item = item[index + 1:len(item)]

        # extract the year
        year = item
        years.append("20" + year)  # because the year is only last two digits

    # get data from the "Time" column of the data (hhmm)
    for item in data["Time"]:
        # convert item to a string
        item_str = str(item)

        # make sure it is the correct length because leading 0s disappear
        while len(item_str) < 4:
            item_str = f"0{item_str}"

        # extract the hour
        hour = item_str[0:2]
        hours.append(hour)

        # extract the minute
        minute = item_str[2:4]
        minutes.append(minute)

    # convert all units of time from strings to integers
    lists_time = [years, months, days, hours, minutes]
    for y in range(0, len(lists_time)):
        for x in range(0, len(lists_time[y])):
            try:
                lists_time[y][x] = int(lists_time[y][x])
            except:
                lists_time[y][x] = -1

    # make a list of times as datetime objects
    times_datetime = []
    for i in range(0, len(lists_time[0])):
        time_datetime = datetime.datetime(years[i], months[i], days[i],
                                          hours[i], minutes[i])
        times_datetime.append(time_datetime)

    # convert times from datetime objects to epoch (float)
    times_epoch = []
    for time_datetime in times_datetime:
        time_epoch = time_datetime.timestamp()
        times_epoch.append(time_epoch)

    # add the epoch times to the dataframe
    data["Epoch"] = times_epoch

    # convert epoch times into a specified unit of time after start time
    process.convert_epoch(data, "Epoch", unit_time, col_time)

    # add temperatures in C to the dataframe
    temperatures_c = process.convert_temps(data, "Temp (°F)")
    data["Temp (C)"] = temperatures_c

    # add column specifying it is station data
    data = process.add_column(data, "Sensor", "Station")

    # add column specifying that all data is valid
    data["Data_Ok"] = True

    return data

def process_data_purpleair(file, sensor_name, unit_time, col_time):
    """
    Processes data from PurpleAir
    :param file: String, name of .csv file with data
    :param sensor_name: String, name of the station sensor closest to our
        sensor
    :return: DataFrame of processed PurpleAir station data
    """

    """ order:
        0. "time_stamp" (yyyy-mm-dd hh:mm:ss)
        1. "sensor_index" (int)
        2. "humidity" (%, int)
        3. "temperature" (F, int)
        4. "pm2.5_atm" (float)
        5. "latitude" (degrees, float)
        6. "longitude" (degrees, float)
    """

    # make dataframe from the file
    data = pd.read_csv(file)

    # make a new dataframe only with information from the closest sensor
    # initialize lists to hold values
    time_stamps = []
    sensor_indices = []
    humidities = []
    temperatures = []
    pms = []
    sensor_names = []
    latitudes = []
    longitudes = []

    # add data to each list
    for y in range(0, len(data)):
        if data.iat[y, 5] == sensor_name:
            time_stamps.append(data.iat[y, 0])
            sensor_indices.append(data.iat[y, 1])
            humidities.append(data.iat[y, 2])
            temperatures.append(data.iat[y, 3])
            pms.append(data.iat[y, 4])
            sensor_names.append(data.iat[y, 5])
            latitudes.append(data.iat[y, 6])
            longitudes.append(data.iat[y, 7])

    # make an updated data frame from only that sensor's values
    data_updated = pd.DataFrame({"time_stamp": time_stamps,
                                 "sensor_index": sensor_indices,
                                 "humidity": humidities,
                                 "temperature": temperatures,
                                 "pm2.5_atm": pms,
                                 "sensor_name": sensor_names,
                                 "latitude": latitudes,
                                 "longitude": longitudes})

    # add a column to data of times converted to epoch
    data_updated = process.convert_timestamp(data_updated, "time_stamp")

    # convert epoch times into a specified unit of time after start time
    process.convert_epoch(data_updated, "Epoch", unit_time, col_time)

    # add temperatures in C to the dataframe
    temperatures_c = process.convert_temps(data_updated, "temperature")
    data_updated["temperature_c"] = temperatures_c

    # check temperature values
    info = [("temperature_c", -50, 50, "open")]
    data_updated = process.filter_values(data_updated, "remove", info)

    return data_updated

def process_data_sensor_green(unit_time, col_time):
    """
    Processes data from the first set of sensor data CSV to be graphed
    (7/10-7/13, green case, logdata7-10-26to7-13-26.CSV)
    :return: DataFrame of processed sensor data
    """

    """ order:
        0. millis = milliseconds
        1. gps_timestamp = time (yyyy-mm-ddThh:mm:ss)
        2. ch1_v = solar voltage
        3. ch1_ma
        4. ch2_v = battery voltage
        5. ch2_ma
        6. ch3_v
        7. ch3_ma
        8. temp_c = temperature (Celsius)
        9. hum_pct = relative humidity (percentage)
        10. gas_ohm = gas
        11. pm1_0 = num particle matter where d = 1.0 micrometers
        12. pm2_5 = num particle matter where d = 2.5 micrometers
        13. pm10 = num particle matter where d = 10 micrometers
        14. lat = latitude
        15. lon = longitude
        16. siv = num satellites in view
    """

    # make dataframe from logdata7-10-26to7-13-26.csv
    data = pd.read_csv("logdata7-10-26to7-13-26.csv")

    # add a column to determine if each row has a valid time reading
    data["Has_Fix"] = data["gps_timestamp"] != "NO_FIX"

    # add a column to determine if each row has trustworthy gps positions
    # 1. has a timestamp
    candidate_1 = data["Has_Fix"]
    # 2. lon/lat are not 0 (lat=0, lon=0 is default for when no location is read)
    candidate_2 = candidate_1 & (data["lon"] != 0) & (data["lat"] != 0)
    # 3. siv reading is greater than or equal to 4
    candidate_3 = candidate_2 & (data["siv"] >= 4)

    # all must be true for the row to have a trustworthy gps position
    data["GPS_Ok"] = candidate_3

    # add a column to determine if the data is valid for that row
    data["Data_Ok"] = data["GPS_Ok"]
    check = [("temp_c", -50, 50, "open"),
             ("hum_pct", 0, 100, "closed")]
    data = process.check_values(data, check, "Data_Ok")
    x_data_ok = data.columns.get_loc("Data_Ok")

    # add column specifying it is sensor data
    data = process.add_column(data, "Sensor", "Green Case")

    # add column for epoch times
    process.convert_timestamp(data, "gps_timestamp")

    # convert epoch times into a specified unit of time after start time
    process.convert_epoch(data, "Epoch", unit_time, col_time)

    return data

def process_data_sensor_white(unit_time, col_time):
    """
    Gets data from the second set of sensor data CSV
    (7/28-7/30, white case, 73026whiteneclosuretest.csv)
    :return: DataFrame of processed sensor data
    """

    """ order:
        0. "id"
        1. "epoch"
        2. "temp*100"
        3. "humidity*100"
        4. "gas_ohms"
        5. "pressure_pa"
        6. "lat"
        7. "long"
        8. "siv"
        9. "solar_mv*1000"
        10. "solar_ma*1000"
        11. "battery_mv*1000"
        12. "battery_ma*1000"
        13. "radio_mv*1000"
        14. "radio_ma*1000" 
    """

    data = pd.read_csv("73026whiteneclosuretest.csv")

    # cast ints to floats for columns that need to be rescaled
    data = data.astype({"temp*100": float, "humidity*100": float,
                        "lat": float, "long": float,
                        "solar_mv*1000": float, "solar_ma*1000": float,
                        "battery_mv*1000": float, "battery_ma*1000": float,
                        "radio_mv*1000": float, "radio_ma*1000": float})

    # rescale columns
    indices = [(2, 100), (3, 100), (6, 10000000), (7, 10000000), (9, 1000),
               (10, 1000), (11, 1000), (12, 1000), (13, 1000), (14, 1000)]
    process.rescale_columns(data, indices)

    # rename rescaled columns
    data = data.rename(columns={"temp*100": "temp", "humidity*100": "humidity",
                                "solar_mv*1000": "solar_mv", "solar_ma*1000": "solar_ma",
                                "battery_mv*1000": "battery_mv", "battery_ma*1000": "battery_ma",
                                "radio_mv*1000": "radio_mv", "radio_ma*1000": "radio_ma",
                                "epoch": "Epoch"})

    # add a column to determine if each row has a valid time reading
    # (for the 7/28-7/30 data, there is no timestamp that would have a NO_FIX"
    #  value for NaN readings and all the epoch values are valid, so be
    #  careful applying this to different datasets)
    data["Has_Fix"] = data["Epoch"] > 0

    # add a column to determine if each row has trustworthy gps positions
    # 1. has a timestamp
    candidate_1 = data["Has_Fix"]
    # 2. lon/lat are not 0 (lat=0, lon=0 is default for when no location is read)
    candidate_2 = candidate_1 & (data["long"] != 0) & (data["lat"] != 0)
    # 3. siv reading is greater than or equal to 4
    candidate_3 = candidate_2 & (data["siv"] >= 4)

    # all must be true for the row to have a trustworthy gps position
    data["GPS_Ok"] = candidate_3

    # add a column to determine if the data is valid for that row
    data["Data_Ok"] = data["GPS_Ok"]
    check = [("temp", -50, 50, "open"),
             ("humidity", 0, 100, "closed")]
    data = process.check_values(data, check, "Data_Ok")
    x_data_ok = data.columns.get_loc("Data_Ok")

    # add column specifying it is sensor data
    data = process.add_column(data, "Sensor", "White Case")

    # convert epoch times into a specified unit of time after start time
    process.convert_epoch(data, "Epoch", unit_time, col_time)

    # add column specifying that all data is valid
    data["Data_Ok"] = True

    return data

def process_data_sensor_longterm(unit_time, col_time):
    # id,node_id,record_id,sensor_epoch,
    # recorded_at,received_at,
    # solar_mv,solar_ma,batt_mv,batt_ma,radio_mv,radio_ma,
    # temperature,humidity,
    # gas_ohms,pressure_pa,
    # pm1,pm25,pm10,
    # bmv_obs,
    # ch4_conc,ch4_temp,ch4_error,
    # latitude,longitude,siv,
    # meshtastic_from,meshtastic_packet_id,hops_away,rssi,snr,curr_received,curr_missed

    # make dataframe from logdata8-17-26to9-11-26.csv
    data = pd.read_csv("logdata8-17-26to9-11-26.csv")

    # add a column to determine if each row has a valid time reading
    data["Has_Fix"] = data["sensor_epoch"] > 0

    # add a column to determine if each row has trustworthy gps positions
    # 1. has a timestamp
    candidate_1 = data["Has_Fix"]
    # 2. lon/lat are not 0 (lat=0, lon=0 is default for when no location is read)
    candidate_2 = candidate_1 & (data["latitude"] != 0) & (data["longitude"] != 0)
    # 3. siv reading is greater than or equal to 4
    candidate_3 = candidate_2 & (data["siv"] >= 4)

    # all must be true for the row to have a trustworthy gps position
    data["GPS_Ok"] = candidate_3

    # add a column to determine if the data is valid for that row
    data["Data_Ok"] = data["GPS_Ok"]
    check = [("temperature", -50, 50, "open"),
             ("humidity", 0, 100, "closed"),
             ("ch4_temp", -50, 50, "open")]
    # is ch4_conc humidity?
    data = process.check_values(data, check, "Data_Ok")
    x_data_ok = data.columns.get_loc("Data_Ok")

    # add column specifying it is sensor data
    data = process.add_column(data, "Sensor", "Long-Term Enclosure")

    # convert epoch times into a specified unit of time after start time
    process.convert_epoch(data, "sensor_epoch", unit_time, col_time)

    return data

def graph_data_green(unit_time, col_time):
    """
    Graphs data from the first set of data (7/10-7/13, green case)
    :return: outputs graphs
    """

    """ order for station data: (outdated)
        0. "Station"
        1. "Date" (m/dd/yyyy)
        2. "Time" (int, hhmm)
        3. "Temp (°F)" (float)
        4. "RH (%)" relative humidity (int)
        5. "Time (epoch)" (float)
        6. "Temp (C)" (float)
        7. "Sensor" ("Station")
    """

    """ order for sensor data: (outdated)
        0. "millis" (int, milliseconds)
        1. "gps_timestamp" (yyyy-mm-ddT:hh:mm:ss (24 hour clock))
        2. "ch1_v" (float)
        3. "ch1_ma" (float)
        4. "ch2_v" (float)
        5. "ch2_ma" (float)
        6. "ch3_v" (float)
        7. "ch3_ma" (float)
        8. "temp_c" (float)
        9. "hum_pct" (float)
        10. "gas_ohm" (int, volatile organic compounds (VOC))
        11. "pm1_0" (float, particle matter with diameter = 1.0 micrometers (#))
        12. "pm2_5" (float, particle matter with diameter = 2.5 micrometers (#))
        13. "pm10" (float, particle matter with diameter = 10 micrometers (#))
        14. "lat" (float)
        15. "lon" (float)
        16. "siv" (int, satellites in view (#))
        17. "Epoch" (float)
        18. "Sensor" ("Green Case")
    """

    # make dataframes
    data_station = process_data_station("report-15-20260713113036.csv", unit_time, col_time)
    data_sensor = process_data_sensor_green(unit_time, col_time)

    # graph temperature and humidity as hued graphs
    dfs = [data_station, data_sensor]
    columns = [[col_time, "Sensor", "Temp (C)", "RH (%)"],
               [col_time, "Sensor", "temp_c", "hum_pct"]]
    titles_axes = [col_time, "Sensor", "Temp (C)", "RH (%)"]
    titles_graph = ["Time vs Temperature", "Time vs Humidity"]
    description = "(Green Case vs Station Data 7/10-7/13)"
    graph.graph_hued_data(dfs, columns, titles_axes, titles_graph, description, "Data_Ok")

    # plot battery info as subplots
    description_sensor = "(7/10-7/13 Green Case Sensor Data)"
    graph.graph_battery_info(data_sensor, col_time, "ch1_v", "ch1_ma", "ch2_v",
                             "ch2_ma", "ch3_v", "ch3_ma", description_sensor, "Data_Ok")

    # plot particle matter graphs as subplots
    y_cols_pm = ["pm1_0", "pm2_5", "pm10"]
    y_labels_pm = ["Num Particle Matter with Diameter = 1 micrometers",
                   "Num Particle Matter with Diameter = 2.5 micrometers",
                   "Num Particle Matter with Diameter = 10 micrometers"]
    titles_ind_pm = ["Time vs pm1_0", "Time vs pm2_5", "Time vs pm10"]
    graph.graph_subplots_line(data_sensor, 1, 3,
                        col_time, y_cols_pm, col_time, y_labels_pm,
                        titles_ind_pm, "Time vs PM", description_sensor, "Data_Ok")

    # plot longitude and latitude graphs as subplots
    graph.graph_position(data_sensor, col_time, "lat", "lon", description_sensor, "Data_Ok")

    # plot gas_ohm
    graph.graph_individual_line(data_sensor,
                                col_time, "gas_ohm",
                                "Time vs VOC", description_sensor,
                                col_time, "Volitile Organic Compounds", "Data_Ok")

    # plot siv
    graph.graph_individual_line(data_sensor,
                          col_time, "siv",
                          "Time vs SIV", description_sensor,
                          col_time, "Number of Satellites in View", "Data_Ok")

    graph.show_graphs()

def graph_data_white(unit_time, col_time):
    """
    Graphs data from the second set of data (7/28-7/30, white case)
    :return: outputs graphs
    """

    """ order for station data:
        0. "Station"
        1. "Data" (m/dd/yyyy)
        2. "Time" (int, hhmm)
        3. "RH (%)" (int)
        4. "Temp (°F)" (float)
        5. "Time (epoch)" (float)
        6. "Temp (C)" (float)
        7. "Sensor" ("Station")
    """

    """ order for sensor data:
        0. "id" (int)
        1. "epoch" (int)
        2. "temp" (float)
        3. "humidity" (float)
        4. "gas_ohms" (int)
        5. "pressure_pa" (int)
        6. "lat" (float)
        7. "long" (float)
        8. "siv" (int)
        9. "solar_mv" (float)
        10. "solar_ma" (float)
        11. "battery_mv" (float)
        12. "battery_ma" (float)
        13. "radio_mv" (float)
        14. "radio_ma" (float)
        15. "Sensor" ("White Case")
    """

    # make dataframes
    data_station = process_data_station("report-15-20260730124201.csv", unit_time, col_time)
    data_sensor = process_data_sensor_white(unit_time, col_time)

    # graph temperature and humidity as hued graphs
    dfs = [data_station, data_sensor]
    columns = [[col_time, "Sensor", "Temp (C)", "RH (%)"],
              [col_time, "Sensor", "temp", "humidity"]]
    titles_axes = [col_time, "Sensor", "Temp (C)", "RH (%)"]
    titles_graph = ["Time vs Temperature", "Time vs Humidity"]
    description = "(7/28-7/30 White Case vs Station Data)"
    graph.graph_hued_data(dfs, columns, titles_axes, titles_graph, description, "Data_Ok")

    # plot longitude and latitude graphs as subplots
    description = "(7/28-7/30 Station and White Case Sensor Data)"
    graph.graph_position(data_sensor, col_time, "lat", "long", description, "Data_Ok")

    # plot battery info as subplots
    graph.graph_battery_info(data_sensor, col_time, "solar_mv", "solar_ma",
                       "battery_mv", "battery_ma", "radio_mv", "radio_ma",
                       description, "Data_Ok")

    # plot gas and pressure as subplots
    y_cols_gp = ["gas_ohms", "pressure_pa"]
    y_labels_gp = ["Gas (ohms)", "Pressure (pascals)"]
    titles_ind_gp = ["Time vs Gas", "Time vs Pressure"]
    graph.graph_subplots_line(data_sensor, 1, 2,
                        col_time, y_cols_gp, col_time, y_labels_gp,
                        titles_ind_gp, "Time vs Gas/Pressure Info",
                        description, "Data_Ok")

    # plot siv
    graph.graph_individual_line(data_sensor,
                          col_time, "siv",
                          "Time vs SIV", description,
                          col_time, "Number of Satellites in View", "Data_Ok")

    graph.show_graphs()

def graph_data_longterm(unit_time, col_time):

    # make dataframes
    data_sensor = process_data_sensor_longterm(unit_time, col_time)
    data_station = process_data_station("sensordata_8.17-9_11.csv", unit_time, col_time)


    # filter station data so it only has valid values
    data_station_filtered = data_station.iloc[4300:6700]
    # old range: 4174-6571
    # updated range: 4300-6700

    # graph temperature and humidity as hued graphs
    dfs = [data_station_filtered, data_sensor]
    columns = [[col_time, "Sensor", "Temp (C)", "RH (%)"],
              [col_time, "Sensor", "temperature", "humidity"]]
    titles_axes = [col_time, "Sensor", "Temp (C)", "RH (%)"]
    titles_graph = ["Time vs Temperature", "Time vs Humidity"]
    description = "(8/19-9/11 Longterm Collection vs Station Data)"
    graph.graph_hued_data(dfs, columns, titles_axes, titles_graph, description, "Data_Ok")

    """y_cols = ["solar_mv", "solar_ma", "batt_mv", "batt_ma", "radio_mv", "radio_ma"]
    y_labels = ["solar_mv", "solar_ma", "batt_mv", "batt_ma", "radio_mv", "radio_ma"]
    titles_ind = ["", "", "", "", "", ""]
    description = "Long-Term Enclosure"
    graph.graph_subplots_line(data, 3, 2, col_time, y_cols, col_time, y_labels,
                              titles_ind, "Battery Info", description, "Data_Ok")"""

    graph.show_graphs()

def main():
    """
    Test code
    """

    #df_1 = process_data_station("report-15-20260713113036.csv", "days", "Time (Days)")
    #df_2 = process_data_station("report-15-20260730124201.csv", "days", "Time (Days)")
    #df_3 = process_data_sensor_green("days", "Time (Days)")
    #df_4 = process_data_sensor_white("days", "Time (Days)")
    #df_6 = process_data_sensor_longterm("days", "Time (Days)")
    #df_5 = process_data_sensor_standard("data_open_enclosure_8.14.csv", "Open Enclosure", "Time (Days)")
    #print(df_6)
    #print(df_1) # 7/10-7/13 station data, report-15-20260713113036.csv
    #print(df_2) # 7/28-7/30 station data, report-15-20260730124201.csv
    #print(df_3) # 7/10-7/13, green case, logdata7-10-26to7-13-26.CSV
    #print(df_4) # 7/28-7/30, white case, 73026whiteneclosuretest.csv

    graph_data_longterm("days", "Time (Days)")
    #graph_data_longterm("days", "Time (Days)")

if __name__ == '__main__':
    main()