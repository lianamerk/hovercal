import pandas as pd
import numpy as np

import holoviews as hv
from holoviews import opts

import datetime
import calendar
from dateutil.relativedelta import relativedelta

import bokeh
import bokeh.io

import panel as pn

hv.extension('bokeh')

def joint_colorbar(cmap_max, cmap_height, cmap_color):
    """
    Creates a holoviews colorbar that can be added to a multi-plot layout.
    Also helpful for single plots because you have more control over where it
    is placed in comparison to a bokeh colorbar
    Parameters
    ----------
    cmap_max : integer
        Largest value that will be presented on the plots, colorbar maximum.
    cmap_height : integer
        This will scale with number of plots. It is computed by multi_year_heatmap.
    cmap_color: color palette
        The color palette used for this instance of multi_year_heatmap.
    Returns
    -------
    output : holoviews object
        A standalone color bar that can then be added to plots
    """
    hm = hv.HeatMap([(0, 0, 1.0), (0, 1, cmap_max)]).opts(colorbar=True, 
               clim=(1.0, cmap_max),
               alpha=0,
               show_frame=False,
               frame_height=cmap_height,
                frame_width=0,
               colorbar_position='right', 
               toolbar=None,
               # margin=(0, -740),
               cmap=cmap_color,
            padding=(0, 0),
             xaxis=None,
             yaxis=None)
    
    return hm

def single_year_heatmap(sub_df,
                 year,
                 month_separation_width = 2,
                 month_separation_color = 'lightgrey',
                 month_separation_alpha = 1,
                 cmap_color = 'Blues',
                 outline_color = 'black',
                 outline_alpha = 1,
                 outline_width = 2,
                 month_label = 'Short',
                 day_label = 'Letter',
                 box_separation_width = 4,
                 box_separation_color = 'white',
                 box_separation_alpha = 1,
                 fig_height=160,
                 show_toolbar = True,
                 hover_columns = [],
                 value_column = 'value',
                 empty_color = '#D3D3D3'):
    
    """
    Creates a panel layout with holoviews heatmaps and a custom colorbar, based on the
    global maximum among all years passed in. Each year plot is made by calling the
    funtion single_year_heatmap.
    Parameters
    ----------
    sub_df : DataFrame
        Should have columns for date, day, month, year, and value. Can be sparse (i.e. only
        populated with dates that have nonzero values).
    year_list : list of integers (years)
        Even if using 1 year, should pass in as a list. Ensure years are present in dataframe
        with at least one nonzero value.
    month_separation_width: integer
        Line width for the month separators.
    month_separation_color: HTML color value or hex code
        Color for the month separators.
    month_separation_alpha: Integer between 0 and 1.
        Line transparency for the month separators. Note that month separators are drawn over
        each other. If you have a low alpha, the spots where month separators are not drawn over
        each other will appear more transparent than overlaps.
    outline_separation_width: integer
        Line width for the outline (border).
    outline_separation_color: HTML color value or hex code
        Color for the outline (border).
    outline_separation_alpha: Integer between 0 and 1.
        Line transparency for the outline (border).
    box_separation_separation_width: integer
        Line width for the box separators, which is the space between individual days.
    box_separation_separation_color: HTML color value or hex code
        Color for the box separators, which is the space between individual days.
    box_separation_separation_alpha: Integer between 0 and 1.
        Line transparency for the box separators, which is the space between individual days.
    month_label: String
        String, either "Short" or "Letter", for the month labels along the x-axis. Short will
        display abbreviations (Jan, Feb...). Letter will display first letter of each month.
        Note it is not yet possible to print the full month, due to spacing issues.
    day_label: String
        String, must be "Short, "Letter", or "Full", for the day names along the y-axis. Short
        will display abbreviations (Mon, Tues...). Letter will display first letter of each day.
        Full will display whole day name.
    show_toolbar: Bool
        If True, a toolbar will be displayed on the top of the layout. This will include scroll,
        hover, zoom, navigate, reset, and save. Note save will save plots individually, without
        colorbars. Saving the full layout must happen with panel tools, not directly from the plot.
    hover_columns: list of Strings
        List of columns that should be included in the hover information. A given hover column
        should be a string, since different days will likely have information of different lengths,
        which is not yet possible to display.
    value_column: String
        Name of the column that contains the value to be displayed on the heatmap (i.e. minutes played,
        fruit servings per day).
    empty_color: HTML color value or hex code
        The color of plot when no values exist (NaN values).
        
    Returns
    -------
    layout : holoviews object
        A holoviews layout object with a single year heatmap.
    """

    # Fill in missing days
    idx_daily = pd.date_range(start=f'1/1/{year}', end=f'12/31/{year}')
    sub_df = sub_df.set_index('date').reindex(idx_daily).reset_index().rename(columns={'index': 'date'})

    # Create new columns for year, month, and day
    sub_df.date = pd.to_datetime(sub_df.date)
    sub_df['year'] = sub_df['date'].dt.year
    sub_df['month'] = sub_df['date'].dt.month
    sub_df['day'] = sub_df['date'].dt.day
    
    # Get the count of the weeks, 0-52 (may be up to 54 if leap year)
    sub_df['weekcount'] = sub_df['date'].dt.isocalendar().week
        
    # From calplot: https://github.com/tomkwok/calplot
    # "There may be some days assigned to previous year's last week or
    # next year's first week. We create new week numbers for them so
    # the ordering stays intact and week/day pairs unique."
    sub_df.loc[(sub_df.month == 1) & (sub_df.weekcount > 50), 'weekcount'] = 0
    sub_df.loc[(sub_df.month == 12) & (sub_df.weekcount < 10), 'weekcount'] = sub_df.weekcount.max() + 1
    
    # Set the first week of the year back to 0, if it isn't there already
    # If this isn't done, the plot will be shifted 1 column to the right
    if sub_df.weekcount.min() == 1:
        sub_df.weekcount -= 1
    
    # Flip the axes so Monday is on top (6) and Sunday is at the bottom (0)
    # This makes the plot more intuitive
    sub_df['day_of_week'] = 6 - sub_df['date'].dt.weekday
    sub_df['weekday_name'] = sub_df['date'].dt.day_name()

    # Show 0 minutes if we had an empty day, instead of NaN
    sub_df.fillna(0)

    # Make the base heatmap, with weekcount along the xaxis and weekday along the yaxis
    # Pass in vdims, that will be used for hovertools.
    p = hv.HeatMap(data=sub_df,
                   kdims=['weekcount', 'day_of_week'],
                    vdims=[value_column, 'date', *hover_columns])
        
    # Month Outline directly from https://github.com/rougier/calendar-heatmap/blob/master/github-activity.py, with
    # 0.5 shift because holoviews axes ticks are in the center.
    start = datetime.datetime(year, 1, 1).weekday()
    overlay_list = []
    xticks = []
    monthlist = []
    
    # For each month, draw a Polygon to delineate the days in the month
    # Loop through 1-13 because datetime is 1 indexed
    for month in range(1, 13):
        first = datetime.datetime(year, month, 1)
        last = first + relativedelta(months=1, days=-1)
        y0 = 7 - first.weekday()
        y1 = 7 - last.weekday()
        x0 = (int(first.strftime('%j'))+start-1)//7
        x1 = (int(last.strftime('%j'))+start-1)//7
        P = [(x0-0.5, y0-0.5),
             (x0+1-0.5, y0-0.5),
             (x0+1-0.5, 7-0.5),
             (x1+1-0.5, 7-0.5),
             (x1+1-0.5, y1-1-0.5),
             (x1-0.5, y1-1-0.5),
             (x1-0.5, 0-0.5),
             (x0-0.5, 0-0.5) ]
        
        # Find where the month tick should go
        xloc = x0-0.5 + (x1-x0+1-0.5)/2
        
        # Add the month tick to the list
        if month_label.lower() == 'letter':
            monthlist.append((xloc, calendar.month_abbr[month][:1]))
        else:
            monthlist.append((xloc, calendar.month_abbr[month]))

        # Add the polygon with vertices P to the list of Polygons to be overlaid
        overlay_list.append(hv.Polygons(P))
            
    # Create the overlay with original heatmap p and 12 polygons
    overlay = hv.Overlay([p] + overlay_list)
    
    def hook(plot, element):
        # Turn off the black x and y axis lines
        plot.handles['xaxis'].axis_line_alpha = 0
        plot.handles['yaxis'].axis_line_alpha = 0

        # Add back outline to the plot of user's input
        plot.handles['plot'].outline_line_width = outline_width
        plot.handles['plot'].outline_line_alpha = outline_alpha
        plot.handles['plot'].outline_line_color = outline_color

        # Turn off all tickmarks
        plot.handles['xaxis'].major_tick_line_color = None
        plot.handles['xaxis'].minor_tick_line_color = None
        plot.handles['yaxis'].major_tick_line_color = None
        plot.handles['yaxis'].minor_tick_line_color = None
        
        # Turn off the x axis label (else it says "weekcount")
        plot.handles['xaxis'].axis_label_text_font_size = '0pt'

        # Bring the year closer, bigger, and not italics
        plot.handles['yaxis'].axis_label_text_font_size = '25pt'
        plot.handles['yaxis'].axis_label_text_font_style = 'normal'
        plot.handles['yaxis'].axis_label_standoff = 10

        # Bring the days of week closer and bigger
        plot.handles['yaxis'].major_label_text_font_size = "12pt"
        plot.handles['yaxis'].major_label_standoff = 1

        # Bring the months closer and bigger
        plot.handles['xaxis'].major_label_text_font_size = "12pt"
        plot.handles['xaxis'].major_label_standoff = 0


    if day_label.lower() == 'full':
        yticks = [(6, 'Monday'), (5, 'Tuesday'),(4, 'Wednesday'),
                  (3, 'Thursday'), (2, 'Friday'), (1, 'Saturday'), (0, 'Sunday')]
        
    elif day_label.lower() == 'letter':
        yticks = [(6, 'M'), (5, 'T'),(4, 'W'), (3, 'Th'), (2, 'F'), (1, 'Sa'), (0, 'Su')]
        
    else:
        yticks = [(6, 'Mon'), (5, 'Tues'),(4, 'Wed'),
                  (3, 'Thurs'), (2, 'Fri'), (1, 'Sat'), (0, 'Sun')]
        
    # Customize both plots.
    overlay.opts(
        opts.Polygons(alpha = 0,
                      line_alpha = month_separation_alpha, 
                      line_width = month_separation_width,
                      line_color = month_separation_color,
                     hooks = [hook]),
        opts.HeatMap(tools = ['hover'],
                     colorbar=False,
                     width=1000,
                     line_width = box_separation_width,
                     line_color = box_separation_color,
                     line_alpha = box_separation_alpha,
                     height = fig_height,
                     cmap = cmap_color,
                     yticks = yticks,
                     xticks=monthlist,
                     ylabel = f'{year}',
                     hooks=[hook],
                     # toolbar = toolbar_status,
                     bgcolor="lightgray",
                     padding = 0.001,
                     clipping_colors = {'NaN': empty_color}
                    ))
    
    
    return overlay

def year_heatmap(df,
                 year_list,
                 fig_height = 170,
                 cmap_color = 'Blues',
                 month_separation_width = 2,
                 month_separation_color = 'lightgrey',
                 month_separation_alpha = 1,
                 outline_color = 'black',
                 outline_alpha = 1,
                 outline_width = 2,
                 month_label = 'Short',
                 day_label = 'Letter',
                 box_separation_width = 4,
                 box_separation_color = 'white',
                 box_separation_alpha = 1,
                 show_toolbar = True,
                 hover_columns = [],
                 value_column = 'value',
                 empty_color = '#D3D3D3'):
    """
    Creates a panel layout with holoviews heatmaps and a custom colorbar, based on the
    global maximum among all years passed in. Each year plot is made by calling the
    funtion single_year_heatmap.
    Parameters
    ----------
    df : DataFrame
        Should have columns for date, day, month, year, and value. Can be sparse (i.e. only
        populated with dates that have nonzero values).
    year_list : list of integers (years)
        Even if using 1 year, should pass in as a list. Ensure years are present in dataframe
        with at least one nonzero value.
    month_separation_width: integer
        Line width for the month separators.
    month_separation_color: HTML color value or hex code
        Color for the month separators.
    month_separation_alpha: Integer between 0 and 1.
        Line transparency for the month separators. Note that month separators are drawn over
        each other. If you have a low alpha, the spots where month separators are not drawn over
        each other will appear more transparent than overlaps.
    outline_separation_width: integer
        Line width for the outline (border).
    outline_separation_color: HTML color value or hex code
        Color for the outline (border).
    outline_separation_alpha: Integer between 0 and 1.
        Line transparency for the outline (border).
    box_separation_separation_width: integer
        Line width for the box separators, which is the space between individual days.
    box_separation_separation_color: HTML color value or hex code
        Color for the box separators, which is the space between individual days.
    box_separation_separation_alpha: Integer between 0 and 1.
        Line transparency for the box separators, which is the space between individual days.
    month_label: String
        String, either "Short" or "Letter", for the month labels along the x-axis. Short will
        display abbreviations (Jan, Feb...). Letter will display first letter of each month.
        Note it is not yet possible to print the full month, due to spacing issues.
    day_label: String
        String, must be "Short, "Letter", or "Full", for the day names along the y-axis. Short
        will display abbreviations (Mon, Tues...). Letter will display first letter of each day.
        Full will display whole day name.
    show_toolbar: Bool
        If True, a toolbar will be displayed on the top of the layout. This will include scroll,
        hover, zoom, navigate, reset, and save. Note save will save plots individually, without
        colorbars. Saving the full layout must happen with panel tools, not directly from the plot.
    hover_columns: list of Strings
        List of columns that should be included in the hover information. A given hover column
        should be a string, since different days will likely have information of different lengths,
        which is not yet possible to display.
    value_column: String
        Name of the column that contains the value to be displayed on the heatmap (i.e. minutes played,
        fruit servings per day).
    empty_color: HTML color value or hex code
        The color of plot when no values exist (NaN values).
        
    Returns
    -------
    full_layout : panel object
        A panel with heatmps on left and colorbar on right.
    """
    # Will be populated with 1 plot per year
    plot_list = []
    
    # The df may contain years that we are not going to plot
    # Pull out the current years and find the max
    curr_df = df.loc[df.year.isin(year_list)]
    # We need this for the stand-alone colorbar
    cmap_max = curr_df[value_column].max()
    
    for year in year_list:
        # Pull out the year we are interested in
        sub_df = df.loc[df.year == year]
    
        # Call single_year_heatmap with all the neccesary info
        plot_list.append(single_year_heatmap(sub_df=sub_df,
                                             year=year,
                                             month_separation_width = month_separation_width,
                                             month_separation_color = month_separation_color,
                                             month_separation_alpha = month_separation_alpha,
                                             cmap_color = cmap_color,
                                             outline_color = outline_color,
                                             outline_alpha = outline_alpha,
                                             outline_width = outline_width,
                                             month_label = month_label,
                                             day_label = day_label,
                                             box_separation_width = box_separation_width,
                                             box_separation_color = box_separation_color,
                                             box_separation_alpha = box_separation_alpha,
                                             fig_height=fig_height,
                                             show_toolbar = show_toolbar,
                                             hover_columns = hover_columns,
                                             value_column = value_column,
                                             empty_color = empty_color))

    # Find out how tall the heatmap should be
    cmap_height = fig_height * len(year_list)
    # Create the colorbar using helper
    cbar = joint_colorbar(cmap_max=cmap_max, cmap_height = cmap_height, cmap_color = cmap_color)

    # Layout all the years first 
    layout = hv.Layout(plot_list).cols(1)
    
    # Figure out if we need the toolbar or not
    if show_toolbar == True:
        # Above is the least annoying place to put it
        toolbar_status = 'above'
        layout.opts(toolbar = toolbar_status)
         # Give a little room on top because the hover tool sometimes is cut off
        full_layout = pn.Column(pn.Spacer(height = 20), 
                            pn.Row(pn.Column(layout), cbar, sizing_mode="scale_width"))
        
    else:
        toolbar_status = None
        layout.opts(toolbar = toolbar_status)

        # For this one, also add a little space above the plots now that 
        # the toolbar is gone. This makes the colorbar more level with the plots
        full_layout = pn.Column(pn.Spacer(height = 20), 
                            pn.Row(pn.Column(pn.Spacer(height = 10), layout), cbar, sizing_mode="scale_width"))
    
    return full_layout