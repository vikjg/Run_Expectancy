import scipy
import pickle
import pandas as pd

with open('21-23_re24_wOBA.pkl', 'rb') as fp:
    re24_wOBA = pickle.load(fp)
    

woba = list(re24_wOBA.keys())
lr_matrix = pd.DataFrame(columns=list(re24_wOBA[woba[0]].columns), index=list(re24_wOBA[woba[0]].index))

for columns in lr_matrix.columns:
    for rows in lr_matrix.index:
        target = []
        for groups in re24_wOBA:
            x = re24_wOBA[groups]
            target.append(x.loc[rows].at[columns])
        lr_matrix.loc[rows].at[columns] = scipy.stats.linregress(woba, target)
    
print(lr_matrix)

def wOBA_RE24(lr_matrix, wOBA):
    for columns in lr_matrix.columns:
        for rows in lr_matrix.index:
            lr_matrix.loc[rows].at[columns] = lr_matrix.loc[rows].at[columns].intercept + lr_matrix.loc[rows].at[columns].slope * wOBA
    return lr_matrix


