import pybaseball
import pandas as pd
import numpy as np
import os

re24 = pd.read_csv('2023_re24.csv')
re24 = re24.drop(re24.columns[[0]], axis=1)

p_outs = [0,1,2]
stolen_base_delta = pd.DataFrame(columns=p_outs, index=['OXX -> XOX', 'OXO -> XOO'])

for outs in p_outs:
    
    stolen_base_delta.iloc[0].at[outs] = re24.iloc[2].iat[outs] - re24.iloc[1].iat[outs]
    stolen_base_delta.iloc[1].at[outs] = re24.iloc[6].iat[outs] - re24.iloc[5].iat[outs]
    
print(stolen_base_delta)
stolen_base_delta.to_csv('2023_stolen_base_delta.csv')
