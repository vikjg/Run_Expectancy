import pybaseball
import pandas as pd
import numpy as np
import os

pybaseball.cache.enable()
year = '2023'

start_dates = {'2023': '2023-03-30'}
end_dates = {'2023': '2023-10-01'}
filename = year + '_mlb_statcast.csv'
if os.path.isfile(filename):
    df = pd.read_csv(filename)
else:
    df = pybaseball.statcast(start_dt = start_dates[year], end_dt = end_dates[year]).reset_index(
        drop = True)
    df.to_csv(filename)


def generate_inning_code(x):
    # uses game_pk, inning, inning_topbot
    return str(x.iloc[0]) + str(x.iloc[1]) + str(x.iloc[2])

def situation_to_identifier(x):
    # uses outs, bases
    first = x.iloc[1]
    second = x.iloc[2]
    third = x.iloc[3]
    output = str(x.iloc[0])
    for c in [first, second, third]:
        if c:
            output += 'O'
        else:
            output += 'X'
    return output

p_outs = [0,1,2]
p_bases = ['XXX', 'OXX', 'XOX', 'OOX', 'XXO', 'OXO', 'XOO', 'OOO']

df['inning_code'] = df[['game_pk', 'inning', 'inning_topbot']].apply(generate_inning_code, axis = 1)
inning_codes = df['inning_code'].unique()
    
runs_to_score = {}
for inning_code in inning_codes:
    df_inn = df.loc[df['inning_code'] == inning_code]
    champ = df_inn.sort_values(by = 'at_bat_number', ascending = False).iloc[0]['post_bat_score']
    runs_to_score[inning_code] = champ
df['post_inn_score'] = df['inning_code'].apply(lambda x: runs_to_score[x])
df['runs_to_score'] = df['post_inn_score'] - df['bat_score']


for c in ['on_1b', 'on_2b', 'on_3b']:
    df[c] = df[c].fillna(0)
df['rofirst'] = df['on_1b'].apply(lambda x: x > 0)
df['rosecond'] = df['on_2b'].apply(lambda x: x > 0)
df['rothird'] = df['on_3b'].apply(lambda x: x > 0)
df['situation_identifier'] = df[['outs_when_up', 'rofirst', 'rosecond', 'rothird']].apply(
    situation_to_identifier, axis = 1)

re24 = pd.DataFrame(columns=p_outs, index=p_bases)
for outs in p_outs:
    for bases in p_bases:
        key = str(outs) + bases
        view = df.loc[df['situation_identifier'] == key]
        value = view['runs_to_score'].mean()
        re24.loc[bases].at[outs] = value

re24.to_csv('2023_re24.csv')
print(re24)