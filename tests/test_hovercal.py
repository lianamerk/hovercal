import pandas as pd
import numpy as np

import hovercal

import datetime


def test_df_prepper():
    # Let's say we eat a lot of fruit every day
    # Create a df with type of fruit (should be unique in the Fruit_type col, so hovertools can work)
    fruit_df = pd.DataFrame({
        'date' : [np.random.choice(pd.date_range(datetime.datetime(2020,1,1),datetime.datetime(2022,1,3))) for i in range(24)],
        'Fruit_servings' : np.random.randint(1,5, 24),
        'Fruit_type' : [str(list(set(np.random.choice(['Strawb', 'Papaya', 'Grapefruit', 'Bloob'], size= np.random.randint(1,5))))) for i in range(24)],
    })

    # Use df_prepper to make day, month, year columns
    fruit_df_prepped = hovercal.df_prepper(fruit_df)
    # Check it
    assert fruit_df_prepped.shape == (24, 6)

    
def test_bokeh_matplot():
    spotify_df = pd.read_json('./endsong_data.json', lines=False)
    podcast_df = hovercal.spotify_cleaner(spotify_df, 'The History of Egypt Podcast')

    correct_df = pd.read_csv('./podcast_df_correct.csv')
    
    assert podcast_df.shape == correct_df.shape
    

def test_year_heatmap():
    correct_df = pd.read_csv('./podcast_df_correct.csv')

    # Create the list of what we want to hover over
    hov = ['episode_name', 'unique_episodes']

    # The big plot!
    pod_panel = hovercal.year_heatmap(correct_df,
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
    
    y_n = input('Visual inspection ok? ')
    if y_n in ['y', 'Y', '1']:
        return True
    else:
        return False