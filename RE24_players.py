import pybaseball
import pandas as pd
import numpy as np
import pickle

wOBA_to_RE = {}
df = pd.read_csv('2021-2023mod_mlb_statcast.csv')
    
wOBA = pybaseball.batting_stats(2023, qual=350)
wOBA['key_mlbam'] = pybaseball.playerid_reverse_lookup(wOBA['IDfg'], key_type='fangraphs')['key_mlbam']
df_specific = df[df['batter'].isin(wOBA['key_mlbam'])]

def generate_count(x):
    # uses balls and strikes
    return str(x.iloc[0]) + str(x.iloc[1])

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
iteration = 0
for players in df_specific['batter'].unique():
    df_player = df_specific.loc[df_specific['batter'] == players]
    df_player = df_player.reset_index()
    p_outs = [0,1,2]
    p_bases = ['XXX', 'OXX', 'XOX', 'OOX', 'XXO', 'OXO', 'XOO', 'OOO']
    
    df_player['inning_code'] = df_player[['game_pk', 'inning', 'inning_topbot']].apply(generate_inning_code, axis = 1)
    inning_codes = df_player['inning_code'].unique()
        
    runs_to_score = {}
    for inning_code in inning_codes:
        df_inn = df.loc[df['inning_code'] == inning_code]
        champ = df_inn.sort_values(by = 'at_bat_number', ascending = False).iloc[0]['post_bat_score']
        runs_to_score[inning_code] = champ
    df_player['post_inn_score'] = df_player['inning_code'].apply(lambda x: runs_to_score[x])
    df_player['runs_to_score'] = df_player['post_inn_score'] - df_player['bat_score']
    
    
    for c in ['on_1b', 'on_2b', 'on_3b']:
        df_player[c] = df_player[c].fillna(0)
    df_player['rofirst'] = df_player['on_1b'].apply(lambda x: x > 0)
    df_player['rosecond'] = df_player['on_2b'].apply(lambda x: x > 0)
    df_player['rothird'] = df_player['on_3b'].apply(lambda x: x > 0)
    df_player['situation_identifier'] = df_player[['outs_when_up', 'rofirst', 'rosecond', 'rothird']].apply(
        situation_to_identifier, axis = 1)
    
    
    re24 = pd.DataFrame(columns=p_outs, index=p_bases)
    for outs in p_outs:
        for bases in p_bases:
            key = str(outs) + bases
            view = df_player.loc[df_player['situation_identifier'] == key]
            value = view['runs_to_score'].mean()
            re24.loc[bases].at[outs] = value
    
    re24 = re24.fillna(0)
    df_player['key_fangraphs'] = pybaseball.playerid_reverse_lookup([players])['key_fangraphs']
    df_player['wOBA'] = np.nan
    
    for j in range(len(wOBA['wOBA'])):
        if  df_player.loc[0].at['key_fangraphs'] == wOBA.loc[j].at['IDfg']:
            df_player['wOBA'] = wOBA.loc[j].at['wOBA']
            df_player['wOBA'] = df_player['wOBA'].round(2)
    
    if df_player.iloc[0].at['wOBA'] in wOBA_to_RE:
        wOBA_to_RE[df_player.iloc[0].at['wOBA']].append(re24)
    else: 
        wOBA_to_RE[df_player.iloc[0].at['wOBA']] = [re24]
    iteration += 1
    print('Player ', iteration, ' / ', len(df_specific['batter'].unique()))

for groups in wOBA_to_RE:
    avg_re24 = pd.DataFrame(0, columns=p_outs, index=p_bases)
    for i in range(len(wOBA_to_RE[groups])):
        avg_re24 = avg_re24.add(wOBA_to_RE[groups][i])
    avg_re24 = avg_re24.div(len(wOBA_to_RE[groups]))
    wOBA_to_RE[groups] = avg_re24
           
print(wOBA_to_RE)

with open('21-23_re24_wOBA.pkl', 'wb') as fp:
    pickle.dump(wOBA_to_RE, fp)
    print('dictionary saved successfully to file')
    
with open('21-23_re24_wOBA.pkl', 'rb') as fp:
    re24dict = pickle.load(fp)
    print(re24dict)



