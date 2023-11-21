import pybaseball
import pandas as pd
import numpy as np
import os

re24 = pd.read_csv('2023_re24.csv')
re24 = re24.drop(re24.columns[[0]], axis=1)
re24['3'] = np.zeros_like(re24['1'])
p_outs = [0,1,2]
p_bases = ['XXX', 'OXX', 'OXO', 'XXO']
caught_stealing_delta = pd.DataFrame(columns=p_outs, index=['OXX -> XXX', 'OXO -> XXO'])

for outs in p_outs:
    
    caught_stealing_delta.iloc[0].at[outs] = re24.iloc[1].iat[outs] - re24.iloc[0].iat[outs + 1]
    caught_stealing_delta.iloc[1].at[outs] = re24.iloc[5].iat[outs] - re24.iloc[4].iat[outs + 1]
    
print(caught_stealing_delta)
caught_stealing_delta.to_csv('2023_caught_stealing_delta.csv')