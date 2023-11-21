import pandas as pd


df = pd.read_csv('2021-2023_mlb_statcast.csv')

def generate_inning_code(x):
    # uses game_pk, inning, inning_topbot
    return str(x.iloc[0]) + str(x.iloc[1]) + str(x.iloc[2])


df['inning_code'] = df[['game_pk', 'inning', 'inning_topbot']].apply(generate_inning_code, axis = 1)
inning_codes = df['inning_code'].unique()
    
df.to_csv('2021-2023mod_mlb_statcast.csv')