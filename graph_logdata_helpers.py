"""
AIRWISE V2 - Graphing data (helpers)

Purpose:
    Helper functions for graphing data

Required Libraries:
    -matplotlib
    -seaborn
    -numpy
    -pandas
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import seaborn as sns
import numpy as np
import pandas as pd
import process_logdata_old as process

def show_graphs():
    plt.show()

def graph_individual_line(df, x_col, y_col, title, description, x_title,
                          y_title, col_data_ok):
    """
    Graphs a single lineplot
    :param df: DataFrame, container of data
    :param x_col: String, name of column for the x-axis in the dataframe
    :param y_col: String, name of column for the y-axis in the dataframe
    :param title: String, title of graph
    :param description: String, description of which data set this is about
    :param x_title: String, title of x-axis
    :param y_title: String, title of y-axis
    :return: outputs a graph
    """

    graph = sns.relplot(data=df, x=x_col, y=y_col, kind="line")
    graph.fig.suptitle(title + " " + description)
    graph.set_xlabels(x_title)
    graph.set_ylabels(y_title)

def graph_individual_plot(df, x_col, y_col, title, description, x_title,
                          y_title):
    """
    Graphs a single scatterplot
    :param df: DataFrame, container of data
    :param x_col: String, name of column for the x-axis in the dataframe
    :param y_col: String, name of column for the y-axis in the dataframe
    :param title: String, title of graph
    :param description: String, description of which data set this is about
    :param x_title: String, title of x-axis
    :param y_title: String, title of y-axis
    :return: outputs a graph
    """

    graph_siv = sns.relplot(data=df, x=x_col, y=y_col)
    graph_siv.fig.suptitle(title + " " + description)
    graph_siv.set_xlabels(x_title)
    graph_siv.set_ylabels(y_title)

def graph_subplots_line(df, num_rows, num_cols, x_col, y_cols, x_label,
                        y_labels, titles_ind, title, description, col_data_ok):
    """
    Graphs subplots as lineplots
    :param df: DataFrame, container of data
    :param num_rows: Integer, number of rows for the subplots
    :param num_cols: Integer, number of columns for the subplots
    :param x_col: String, name of column for the x-axis of each plot
    :param y_cols: list, contains strings for the names of columns for the
        y-axis of each plot
    :param x_label: String, name of label for the x_axis of each plot
    :param y_labels: list, contains strings for the labels for the y-axis
        of each plot
    :param titles_ind: list, contains strings for the names of titles for
        each plot
    :param title: String, name of the title for the set of subplots
    :param description: String, describes what data set is being graphed
    :return: outputs subplots
    """

    # set up a subplot
    fig, axes = plt.subplots(num_rows, num_cols)
    x_data_ok = df.columns.get_loc(col_data_ok)

    # loop through each row of the subplots
    for i in range(0, num_rows):
            # loop through each column of the subplots
            for j in range(0, num_cols):
                # get index of where we are in the lists of information
                k = i * num_cols + j
                y_col = y_cols[k]
                title_ind = titles_ind[k]
                y_label = y_labels[k]

            # graph subplots for when there is only one row
            if num_rows == 1:
                # fill make lists for x, y when there is valid data
                list_x = []
                list_y = []
                x_x = df.columns.get_loc(x_col)
                x_y = df.columns.get_loc(y_col)

                for y in range(0, len(df)):
                    if df.iat[y, x_data_ok] == True:
                        x_value = df.iat[y, x_x]
                        y_value = df.iat[y, x_y]
                        list_x.append(x_value)
                        list_y.append(y_value)

                sns.lineplot(data=df, x=x_col, y=y_col, ax=axes[i])
                axes[j].set_title(title_ind)
                axes[j].set_xlabel(x_label)
                axes[j].set_ylabel(y_label)

            # graph subplots for when there is more than one row
            elif num_rows > 1:
                sns.lineplot(data=df, x=x_col, y=y_col, ax=axes[i, j])
                axes[i, j].set_title(title_ind)
                axes[i, j].set_xlabel(x_label)
                axes[i, j].set_ylabel(y_label)

    # formatting
    plt.tight_layout()
    plt.suptitle(title + " " + description)

def graph_hued_data(dfs, columns, titles_axes, titles_graph, description, name_col_data_ok):
    """
    Graphs hued line graphs
    :param dfs: list, dataframes with relevant data
    :param columns: list, list of strings and tuples with names of columns
        that are relevant for each dataframe
    :param titles_axes: list, titles for the each of the axes, starting with
        the x-axis title, then the title for what to hue by and then listing
        all of the different y-axis titles
    :param titles_graph: list, titles for each of the graphs
    :param description: String, describes which data sets this is of
    :param x_data_ok: String,
    :return: outputs a hued line graph
    """

    # create lists to hold data
    x_axes = [] # info for x-axis of graph (i.e. time)
    hues = [] # what to hue by (i.e. location or sensor)
    data_one = [] # empty lists to hold data to graph (i.e. temp/RH)
    data_two = []
    data_three = []

    # create a list of lists to hold data
    master_list = [x_axes, hues]

    # add the desired number of lists of data to the master list
    num_sets = len(titles_graph)
    if num_sets >= 1:
        master_list.append(data_one)
        if num_sets >= 2:
            master_list.append(data_two)
            if num_sets >= 3:
                master_list.append(data_three)

    # loop through each dataframe
    for i_graph in range(0, len(dfs)):
        df = dfs[i_graph]
        x_data_ok = df.columns.get_loc(name_col_data_ok)

        # loop through each row of the dataframe
        for y in range(0, len(df)):
            # make sure the data is relevant
            if df.iat[y, x_data_ok] == True:
                num_data = len(master_list)

                # loop through each relevant data point
                for i_data in range(0, num_data):
                    col = columns[i_graph][i_data]

                    # if col is a tuple, loop through it
                    if type(col) is tuple:
                        for item in col:
                            x = df.columns.get_loc(item)
                            point = df.iat[y, x]
                            master_list[i_data].append(point)

                    # if col isn't a tuple, just add the value
                    else:
                        x = df.columns.get_loc(col)
                        point = df.iat[y, x]
                        master_list[i_data].append(point)

    # loop through the number of specified graphs
    for i in range(0, num_sets):
        # create a new dataframe of relevant data
        data_filtered = pd.DataFrame({titles_axes[0]: master_list[0],
                                      titles_axes[i + 2]: master_list[i + 2],
                                      titles_axes[1]: master_list[1]})

        # graph data
        plot = sns.relplot(data=data_filtered, x=titles_axes[0], y=titles_axes[i + 2],
                           hue=titles_axes[1], kind="line")
        plot.fig.suptitle(titles_graph[i] + " " + description)

def colored_line(vars, c, ax=None, **lc_kwargs):
    """
    Documentation from
    https://matplotlib.org/stable/gallery/lines_bars_and_markers/multicolored_line.html

    Plot a line with a color specified along the line by a third value.

    It does this by creating a collection of line segments. Each line segment is
    made up of two straight lines each connecting the current (x, y) point to the
    midpoints of the lines connecting the current point with its two neighbors.
    This creates a smooth line with no gaps between the line segments.

    Parameters
    ----------
    x, y : array-like
        The horizontal and vertical coordinates of the data points.
    c : array-like
        The color values, which should be the same size as x and y.
    ax : matplotlib.axes.Axes, optional
        The axes to plot on. If not provided, the current axes will be used.
    **lc_kwargs
        Any additional arguments to pass to matplotlib.collections.LineCollection
        constructor. This should not include the array keyword argument because
        that is set to the color argument. If provided, it will be overridden.

    Returns
    -------
    matplotlib.collections.LineCollection
        The generated line collection representing the colored line.
    """

    # get x, y from variables (don't account for z yet)
    x = vars[0]
    y = vars[1]

    # declare a list to contain points to base line segments off of
    # will be of form [[(midpoint_previous_x_i, midpoint_previous_y_i),
    #                   (x_i, y_i), (midpoint_next_x_i, midpoint_next_y_i)]]
    # for endpoints of the data, non-existant midpoints will be (x_i, y_i)
    segments = []

    # loop through each entry
    for i in range(0, len(x)):
        # set default values for relevant points to be the ith point
        midpoint_previous = [x[i], y[i]]
        entry = [x[i], y[i]]
        midpoint_next = [x[i], y[i]]

        # for 3D, add z
        if len(vars) == 3:
            midpoint_previous.append(vars[2][i])
            entry.append(vars[2][i])
            midpoint_next.append(vars[2][i])

        # calculate and update midpoint_previous if it is not the 0th entry
        if i > 0:
            midpoint_previous_x = (x[i] + x[i - 1]) / 2
            midpoint_previous_y = (y[i] + y[i - 1]) / 2
            midpoint_previous = [midpoint_previous_x, midpoint_previous_y]

            # for 3D, add z
            if len(vars) == 3:
                midpoint_previous_z = (vars[2][i] + vars[2][i - 1]) / 2
                midpoint_previous.append(midpoint_previous_z)

        # calculate and update midpoint_next if it is not the last entry
        if i < len(x) - 1:
            midpoint_next_x = (x[i] + x[i + 1]) / 2
            midpoint_next_y = (y[i] + y[i + 1]) / 2
            midpoint_next = [midpoint_next_x, midpoint_next_y]

            # for 3D, add z
            if len(vars) == 3:
                midpoint_next_z = (vars[2][i] + vars[2][i + 1]) / 2
                midpoint_next.append(midpoint_next_z)

        # make a list of the tuples and add to segments
        points = [midpoint_previous, entry, midpoint_next]
        segments.append(points)

    # note: here down is directly copied from
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/multicolored_line.html
    lc_kwargs["array"] = c
    lc = 0

    # use LineCollection for 2D
    if len(vars) == 2:
        lc = LineCollection(segments, **lc_kwargs)

    # use Line3DCollection for 3D
    elif len(vars) == 3:
        lc = Line3DCollection(segments, **lc_kwargs)

    # plot the line collection to the axes
    ax = ax or plt.gca()
    ax.add_collection(lc)

    return lc

def graph_position(df, col_name_time, col_name_lat, col_name_lon, description, col_data_ok):
    """
    Graphs latitude and longitude vs time as subplots
    :param df: DataFrame, holds the data
    :param col_name_[variable]: String, name of the time, latitude, or
        longitude column in the dataframe
    :param description: String, describes the data
    :return: outputs subplots of lon and lat vs time
    """
    y_cols_pos = [col_name_lat, col_name_lon]
    y_labels_pos = ["Latitude (degrees)", "Longitude (degrees)"]
    titles_ind_pos = ["Time vs Latitude", "Time vs Longitude"]
    graph_subplots_line(df, 1, 2,
                        col_name_time, y_cols_pos, col_name_time, y_labels_pos,
                        titles_ind_pos, "Time vs Position", description, col_data_ok)

def graph_battery_info(df, col_time, col_ch1_v, col_ch1_ma, col_ch2_v,
                       col_ch2_ma, col_ch3_v, col_ch3_ma, description, col_data_ok):
    """
    Graphs battery info as subplots
    """
    y_cols_bi = [col_ch1_v, col_ch1_ma, col_ch2_v, col_ch2_ma, col_ch3_v,
                 col_ch3_ma]
    titles_ind_bi = ["Time vs CH1_V", "Time vs CH1_mA", "Time vs CH2_V",
                     "Time vs CH2_mA", "Time vs CH3_V", "Time vs CH3_mA"]
    graph_subplots_line(df, 3, 2,
                        col_time, y_cols_bi, col_time, y_cols_bi,
                        titles_ind_bi, "Time vs Battery Info", description, col_data_ok)