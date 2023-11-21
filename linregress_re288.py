import scipy
import pickle
import pandas as pd

with open('21-23_re288_wOBA.pkl', 'rb') as fp:
    re288_wOBA = pickle.load(fp)
    

woba = list(re288_wOBA.keys())
lr_matrix = pd.DataFrame(columns=list(re288_wOBA[woba[0]].columns), index=list(re288_wOBA[woba[0]].index))

for columns in range(len(lr_matrix.columns)):
    for rows in range(len(lr_matrix.index)):
        target = []
        for groups in re288_wOBA:
            x = re288_wOBA[groups]
            target.append(x.iloc[rows].iat[columns])
        lr_matrix.iloc[rows].iat[columns] = scipy.stats.linregress(woba, target)
    
print(lr_matrix)

def wOBA_RE288(lr_matrix, wOBA):
    for columns in range(len(lr_matrix.columns)):
        for rows in range(len(lr_matrix.index)):
            lr_matrix.iloc[rows].iat[columns] = lr_matrix.iloc[rows].iat[columns].intercept + lr_matrix.iloc[rows].iat[columns].slope * wOBA
    return lr_matrix

