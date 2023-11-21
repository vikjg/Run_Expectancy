import pybaseball
import pandas as pd
import numpy as np
import os

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


def generate_count(x):
    # uses balls and strikes
    return str(x.iloc[0]) + str(x.iloc[1])

def generate_inning_code(x):
    # uses game_pk, inning, inning_topbot
    return str(x.iloc[0]) + str(x.iloc[1]) + str(x.iloc[2])

def situation_to_identifier(x):
    """uses outs, bases"""
    first = x.iloc[1]
    second = x.iloc[2]
    third = x.iloc[3]
    output = str(x.iloc[0]) + x.iloc[4]
    for c in [first, second, third]:
        if c:
            output += 'O'
        else:
            output += 'X'
    return output

def RE288(df):
    p_outs = [0,1,2]
    p_bases = ['XXX', 'OXX', 'XOX', 'OOX', 'XXO', 'OXO', 'XOO', 'OOO']
    p_counts = ['00', '01', '02', '10', '11', '12', '20', '21', '22', '30', '31', '32']
    
    
    df['count'] = df[['balls', 'strikes']].apply(generate_count, axis = 1)
    
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
    df['situation_identifier'] = df[['outs_when_up', 'rofirst', 'rosecond', 'rothird', 'count']].apply(
        situation_to_identifier, axis = 1)
            
    re288_0out = pd.DataFrame(columns=p_counts, index=p_bases)
    for counts in p_counts:
        for bases in p_bases:
            key = '0' + counts + bases
            view = df.loc[df['situation_identifier'] == key]
            value = view['runs_to_score'].mean()
            re288_0out.loc[bases].at[counts] = value
            
    re288_1out = pd.DataFrame(columns=p_counts, index=p_bases)
    for counts in p_counts:
        for bases in p_bases:
            key = '1' + counts + bases
            view = df.loc[df['situation_identifier'] == key]
            value = view['runs_to_score'].mean()
            re288_1out.loc[bases].at[counts] = value
            
    re288_2out = pd.DataFrame(columns=p_counts, index=p_bases)
    for counts in p_counts:
        for bases in p_bases:
            key = '2' + counts + bases
            view = df.loc[df['situation_identifier'] == key]
            value = view['runs_to_score'].mean()
            re288_2out.loc[bases].at[counts] = value
            
    re288 = pd.concat([re288_0out, re288_1out, re288_2out], keys=['0 out', '1 out', '2 out'])
    re288.to_csv('2023_re288.csv')
    return re288
    
re288 = RE288(df)
print(re288)