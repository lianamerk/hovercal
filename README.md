# hovercal

hovercal uses [Holoviews](https://holoviews.org/) to create customizable plots from [Pandas](https://pandas.pydata.org/) timeseries data. It draws heavy inspiration from [calplot](https://github.com/tomkwok/calplot). Month delineator code was adapted from [rougier](https://github.com/rougier/calendar-heatmap/blob/master/github-activity.py). This package was built to visualize day-specific data, such as Spotify listening history:

![podVIS](https://github.com/lianamerk/hovercal/blob/6297bc712aed8271715a6e589a6ae77ec8755968/examples/podvis.gif)


The input `dataframe` can have at minimum a column for unique dates (in YYYY-MM-DD format) and values to be plotted. This can be passed through `df_prepper`, which creates a new column for day, month, and year. Alternatively, the best use-case is for [Spotify](www.spotify.com) extended listening history data, which can be requested under Account settings.Raw json files from this request, called `endsong_n.json` can be globbed together, then passed into `spotify_cleaner` along with the podcast of interest. Future editions will include panels to interact and select different artists or music genres. [Panel](https://panel.holoviz.org/) is used to create a global heatmap and arrange the plots. These can then be saved using the command `panel_name.save('file_name.png')`, provided selenium and the relevant driver is installed. 

## Examples
Many plot features are customizable thanks to Holoviews maneuverability. These can be accessed through: `box_separation`, `month_separation`, `outline_color`. Width, color, and alpha can be passed in. Let's take it for a whirl:

``` python
# Let's say we eat a lot of fruit every day
# Create a df with type of fruit (should be unique in the Fruit_type col, so hovertools can work)
fruit_df = pd.DataFrame({
    'date' : [np.random.choice(pd.date_range(datetime.datetime(2020,1,1),datetime.datetime(2022,1,3))) for i in range(24)],
    'Fruit_servings' : np.random.randint(1,5, 24),
    'Fruit_type' : [str(list(set(np.random.choice(['Strawb', 'Papaya', 'Grapefruit', 'Bloob'], size= np.random.randint(1,5))))) for i in range(24)],
})

# Sometimes we get date duplicates. This will throw an error in plotting.
fruit_df = fruit_df.groupby(['date'], as_index=False).agg({'date': 'first',
                                                            'Fruit_servings': 'sum',
                                                            'Fruit_type': lambda x: str(set(list(x)))})

# Use df_prepper to make day, month, year columns
fruit_df_prepped = hovercal.df_prepper(fruit_df)
fruit_df_prepped.head()
```
Now we have a dataframe that might look something like this:

|    | date                |   Fruit_servings | Fruit_type                         |   year |   month |   day |
|---:|:--------------------|-----------------:|:-----------------------------------|-------:|--------:|------:|
|  0 | 2020-02-29 00:00:00 |                2 | ['Papaya']                         |   2020 |       2 |    29 |
|  1 | 2020-08-10 00:00:00 |                1 | ['Strawb', 'Grapefruit', 'Papaya'] |   2020 |       8 |    10 |
|  2 | 2021-10-30 00:00:00 |                3 | ['Strawb', 'Bloob']                |   2021 |      10 |    30 |
|  3 | 2021-10-16 00:00:00 |                2 | ['Grapefruit', 'Papaya']           |   2021 |      10 |    16 |
|  4 | 2021-12-31 00:00:00 |                1 | ['Bloob']                          |   2021 |      12 |    31 |

Let's see what kind of plots we can make!

``` python
# Create a list of what columns we want to show up when we hover
# This is useful if you have a dataframe with a lot of excess columns, but
# Only want some of them to show up.
hov = ['Fruit_type']

# Call year_heatmap with all the customizations
fruit_panel_1 = hovercal.year_heatmap(fruit_df_prepped,
             year_list = [2020, 2021],
             fig_height = 160,
             show_toolbar=False,
             hover_columns = hov,
             value_column = 'Fruit_servings',
             empty_color = '#FAFAFA',
             month_separation_color = 'lightblue',
             month_separation_alpha = 0.3,
             outline_color = 'lightblue',
             box_separation_width = 2)

fruit_panel_1
```

![fruit_example_1](https://github.com/lianamerk/hovercal/blob/6297bc712aed8271715a6e589a6ae77ec8755968/examples/fruit_hovercal_1.png)


With some more tweaking, we can get something a little more.... eyepopping! Note that if we want to view one year, we pass it in as a list: `year_list = [2021]`.

``` python
fruit_panel_2 = hovercal.year_heatmap(fruit_df_prepped,
             year_list = [2021],
             fig_height = 160,
             show_toolbar=False,
             hover_columns = hov,
             cmap_color = 'RdPu',
             value_column = 'Fruit_servings',
             empty_color = 'white',
             month_separation_color = 'white',
             outline_color = 'purple',
             box_separation_color = 'black',
             box_separation_width = 5)

fruit_panel_2
```

![fruit_example_2](https://github.com/lianamerk/hovercal/blob/6297bc712aed8271715a6e589a6ae77ec8755968/examples/fruit_hovercal_2.png)


To remove the month separators, and have the full day name:

``` python
fruit_panel_3 = hovercal.year_heatmap(fruit_df_prepped,
             year_list = [2021],
             fig_height = 160,
             show_toolbar=False,
             hover_columns = hov,
             cmap_color = 'Purples',
             value_column = 'Fruit_servings',
             empty_color = '#FAFAFA',
             month_separation_color = 'grey',
             month_separation_width = 0,
             day_label = 'Full',
             outline_color = 'purple',
             box_separation_color = 'white',
             box_separation_width = 2)

fruit_panel_3
```

![fruit_example_3](https://github.com/lianamerk/hovercal/blob/6297bc712aed8271715a6e589a6ae77ec8755968/examples/fruit_hovercal_3.png)

## Spotify data

First, read in the json files. Note you can use glob to gather the data because there may be more than 1 json file, something like:

```python
file_list = glob.glob('./data/endsong*.json')
df = pd.concat([pd.read_json(file, lines=False) for file in file_list])
```

Or, feel free to practice with the data in `/tests`:

``` python
spotify_df = pd.read_json('endsong_data.json', lines=False)
spotify_df.head()
```

|    | ts                   | username   |   ms_played | conn_country   | user_agent_decrypted   |   master_metadata_track_name |   master_metadata_album_artist_name |   master_metadata_album_album_name |   spotify_track_uri | episode_name                           | episode_show_name            | spotify_episode_uri                    | reason_start   | reason_end                   | shuffle   |   skipped | offline   |   offline_timestamp | incognito_mode   |
|---:|:---------------------|:-----------|------------:|:---------------|:-----------------------|-----------------------------:|------------------------------------:|-----------------------------------:|--------------------:|:---------------------------------------|:-----------------------------|:---------------------------------------|:---------------|:-----------------------------|:----------|----------:|:----------|--------------------:|:-----------------|
|  0 | 2021-03-14T15:25:02Z | lianamerk  |       11145 | US             | unknown                |                          nan |                                 nan |                                nan |                 nan | 94: The Pools of Horus                 | The History of Egypt Podcast | spotify:episode:6rOdi0QxbzjoS9Z682OoXS | appload        | fwdbtn                       | False     |       nan | False     |       1615735489358 | False            |
|  1 | 2021-01-20T20:46:36Z | lianamerk  |           0 | US             | unknown                |                          nan |                                 nan |                                nan |                 nan | 72: The Home Front (Letters to Ahmose) | The History of Egypt Podcast | spotify:episode:4Gu5MQ7GIXqaIun8k2vIE5 | fwdbtn         | logout                       | False     |       nan | False     |       1611080493371 | False            |
|  2 | 2021-08-25T20:38:44Z | lianamerk  |     1958999 | US             | unknown                |                          nan |                                 nan |                                nan |                 nan | 124: Amurrites 2, The Crimes of Aziru  | The History of Egypt Podcast | spotify:episode:5O8Bbg7ycDAp7SKSYonmd6 | clickrow       | trackdone                    | False     |       nan | True      |       1629913981120 | False            |
|  3 | 2021-06-28T15:56:04Z | lianamerk  |     1353584 | US             | unknown                |                          nan |                                 nan |                                nan |                 nan | 116: Adoring Aten                      | The History of Egypt Podcast | spotify:episode:4QC0C1xCUd0YuAXYyhQQqE | appload        | unexpected-exit-while-paused | False     |       nan | False     |       1624840328345 | False            |
|  4 | 2022-02-27T13:31:37Z | lianamerk  |      991664 | SG             | unknown                |                          nan |                                 nan |                                nan |                 nan | 158: What Ay Did                       | The History of Egypt Podcast | spotify:episode:1Ttt4NrGm6g2SJtVKRNocS | trackdone      | trackdone                    | False     |       nan | False     |       1645967697862 | False            |


Now, you can pull out the podcast you are interested in (note that this occurs with the 'episode_show_name' column of the dataset). If you'd like to plot listening history for an artist instead, you may pass in a tidy dataframe with day, month, year, and value columns directly into `year_heatmap`.

``` python
podcast_df = hovercal.spotify_cleaner(spotify_df, 'The History of Egypt Podcast')
podcast_df.head()
```

||    | date       |   mPlayed |   day |   month |   year | date_time           | episode_name                                                                                                            |   unique_episodes |
|---:|:-----------|----------:|------:|--------:|-------:|:--------------------|:------------------------------------------------------------------------------------------------------------------------|------------------:|
|  0 | 2020-06-16 |  78.2158  |    16 |       6 |   2020 | 2020-06-16 03:19:11 | {'Episode 2: Horus Takes Flight', 'Episode 1: The Two Lands'}                                                           |                 2 |
|  1 | 2020-06-17 |  62.4658  |    17 |       6 |   2020 | 2020-06-17 15:21:51 | {'Interlude: Infinite Waters', 'Episode 2: Horus Takes Flight', 'Episode 1: The Two Lands', 'Episode 3: Horus vs Seth'} |                 4 |
|  2 | 2020-06-18 |  38.2889  |    18 |       6 |   2020 | 2020-06-18 03:36:57 | {'Episode 4: The Sacred Ones'}                                                                                          |                 1 |
|  3 | 2020-06-20 |   6.90042 |    20 |       6 |   2020 | 2020-06-20 18:20:34 | {'Episode 4: The Sacred Ones'}                                                                                          |                 1 |
|  4 | 2020-06-25 |   7.69712 |    25 |       6 |   2020 | 2020-06-25 20:36:14 | {'Episode 4: The Sacred Ones'}                                                                                          |                 1 |

Now, let's plot:

```python
# Create the list of what we want to hover over
hov = ['episode_name', 'unique_episodes']

# The big plot!
pod_panel = hovercal.year_heatmap(podcast_df,
             [2020, 2021, 2022],
             fig_height = 160,
             show_toolbar=True,
             hover_columns = hov,
             value_column = 'mPlayed',
             empty_color = '#FAFAFA',
             month_separation_color = 'green',
             month_separation_alpha = 0.3,
             outline_color = 'green',
             box_separation_width = 2,
             cmap_color = 'Greens',
             day_label = 'Short')

pod_panel
```

![pod_example](https://github.com/lianamerk/hovercal/blob/6297bc712aed8271715a6e589a6ae77ec8755968/examples/podcast_hovercal.png)



