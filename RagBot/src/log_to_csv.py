import pandas as pd
import glob
import os

log_files = glob.glob(os.path.join('app.log*'))
dataframes = []

for file in log_files:
    df = pd.read_json(file, lines=True)
    dataframes.append(df)

jsonObj = pd.concat(dataframes, ignore_index=True)

jsonObj = jsonObj.drop_duplicates(keep='first')
jsonObj.to_csv('log.csv')
