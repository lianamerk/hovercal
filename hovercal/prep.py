import pandas as pd
import numpy as np

def df_prepper(df):
    """
    Creates columns for year, month, and day, based on date column
    Parameters
    ----------
    df : DataFrame
        With column 'date' that will be used to create new columns
    Returns
    -------
    df : DataFrame
        Of same length as before, but 3 extra columns. 
    """
    # Make sure its in datetime
    df.date = pd.to_datetime(df.date)
    
    # Create the new cols
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day

    return df

def spotify_cleaner(df, podcast_name):
    """
    Spotify data may have multiple listening records on a given day.
    This aggregates the data and calls df prepper to get the 3 day/month/year
    columns that we need
    Parameters
    ----------
    df : DataFrame
        Can be directly from spotify json's.
    podcast_name: String
        Name of the podcast. For now, must be podcast because it parses based on
        episode_show_name column in the spotify data.
    Returns
    -------
    day_totes_df : DataFrame
        Will most likely be shorter than before, since now we have aggregated all
        listening in a single day.
    """
    # Start by pulling out our podcast
    podcast_df = df[df["episode_show_name"] == podcast_name].copy()
    
    # Convert timestamp to  datetime format.
    podcast_df['date_time'] = list(pd.to_datetime(podcast_df.ts, format="%Y-%m-%dT%H:%M:%SZ"))
    # Pull out the date from newly created datetime column
    podcast_df['date'] = podcast_df['date_time'].dt.date
    # Make those extra cols
    podcast_df = df_prepper(podcast_df)
    # Convert to minutes so it's more intuitive to look at
    podcast_df['mPlayed'] = podcast_df.ms_played / 60000

    # Pull out only the columns I want. Not neccesary, but might shorten processing time depending
    # on how long the dataset is.
    day_totes = podcast_df[['date', 'mPlayed', 'day', 'month', 'year', 'date_time', 'episode_name' ]].copy()
    # Find the number of unique episodes in a given day
    day_totes['unique_episodes'] = day_totes['episode_name']
    # Aggregate: for time, take the sum. For dates, we can just take the first since we are grouping based on date
    # For episode name, take the set first, since spotify data will have same episode listed twice if you listened
    # At different times of the day.
    day_totes_df = day_totes.groupby(['date'], as_index=False).agg({'mPlayed': 'sum',
                                                                    'day': 'first',
                                                                    'month': 'first',
                                                                    'year': 'first',
                                                                    'date_time': 'first',
                                                                   'episode_name': lambda x: str(set(list(x))),
                                                                   'unique_episodes': lambda x: len(set(list(x)))})
    
    return day_totes_df