from urllib.request import Request, urlopen
import json

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import statsmodels.formula.api as sm
#
url_base='https://raider.io/api/v1/mythic-plus/runs?season=season-bfa-3&region=world&dungeon=all&page='
dump_filename='dump_raiderio.json'
#
def main():
    
    #scrap and generate the dataset
    get_stat_data()
    
    # Importing the dataset
    dataset = pd.read_csv(dump_filename)
    X = dataset.iloc[:, [0, 2, 3, 4, 5, 18, 10, 11, 15, 16, 20, 21, 25, 26, 30, 31]].values
    y = dataset.iloc[:, 1].values
    
    # Encoding categorical data
    labelencoder = LabelEncoder()
    X[:, 3] = labelencoder.fit_transform(X[:, 3])   # Instance Name
    X[:, 5] = labelencoder.fit_transform(X[:, 5])   # Faction
    X[:, 6] = labelencoder.fit_transform(X[:, 6])   # Race 1
    X[:, 7] = labelencoder.fit_transform(X[:, 7])   # Class 1
    X[:, 8] = labelencoder.fit_transform(X[:, 8])   # Race 2
    X[:, 9] = labelencoder.fit_transform(X[:, 9])   # Class 2
    X[:, 10] = labelencoder.fit_transform(X[:, 10]) # Race 3
    X[:, 11] = labelencoder.fit_transform(X[:, 11]) # Class 3
    X[:, 12] = labelencoder.fit_transform(X[:, 12]) # Race 4
    X[:, 13] = labelencoder.fit_transform(X[:, 13]) # Class 4
    X[:, 14] = labelencoder.fit_transform(X[:, 14]) # Race 5
    X[:, 15] = labelencoder.fit_transform(X[:, 15]) # Class 5
    onehotencoder = OneHotEncoder(categorical_features = [3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    X = onehotencoder.fit_transform(X).toarray()
    
    # Splitting the dataset into the Training set and Test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)
    
    # Fitting Multiple Linear Regression to the Training set
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)

    # Building the optimal model using Backward Elimination
    X = np.append(arr = np.ones((100, 1)).astype(int), values = X, axis = 1)
    SL = 0.05
    X_opt = X[:,:]   
    X_Modeled = backwardElimination(X_opt, SL)
    
    # Manual model evaluation (Adjusted R-Squared)    
    #X_opt = X[:,:]
    #regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
    #regressor_OLS.summary()
    
    # Predict completion time for each m+ key evaluated.
    y_pred = regressor.predict(X_test)

# Method for Automatic Backward Elimitation
def backwardElimination(x, sl):
    numVars = len(x[0])
    for i in range(0, numVars):
        regressor_OLS = sm.OLS(y, x).fit()
        maxVar = max(regressor_OLS.pvalues).astype(float)
        if maxVar > sl:
            for j in range(0, numVars - i):
                if (regressor_OLS.pvalues[j].astype(float) == maxVar):
                    x = np.delete(x, j, 1)
    regressor_OLS.summary()
    return x

# Get and Parse Raider.IO Data.
def get_stat_data():
    f= open(dump_filename,'wb+')
    #write header record
    f.write(b'rank,clear_time_min,mythic_level,num_chests,dungeon_name,score,weekly_affix,char1_name,char1_faction,char1_race,char1_class,char1_spec,char2_name,char2_faction,char2_race,char2_class,char2_spec,char3_name,char3_faction,char3_race,char3_class,char3_spec,char4_name,char4_faction,char4_race,char4_class,char4_spec,char5_name,char5_faction,char5_race,char5_class,char5_spec\r\n')
    
    for p in range(0, 5):
        url_page = url_base + str(p)    
        print('Retrieving data from:', url_page)
        req = Request(url_page, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req).read()
    
        #Get records data:
        runs = json.loads(response)['rankings']
        for i, r in enumerate(runs , start=0):
            run = str(r['rank']) \
            + ',' + str(f"{r['run']['clear_time_ms']/60000:.0f}") \
            + ',' + str(r['run']['mythic_level']) \
            + ',' + str(r['run']['num_chests']) \
            + ',' + str(r['run']['dungeon']['name'] \
            + ',' + str(f"{r['score']:.2f}"))
      
            affix = get_affixes_data(runs[i]['run']['weekly_modifiers'])
            roster = get_roster_data(runs[i]['run']['roster'])
    
            f.write(str(run + affix + roster).encode() + b'\r\n')
       
    f.close()

# Parse the data for the week affixes
def get_affixes_data(affix_data):
    affix = ''
    for i, a in enumerate(affix_data, start=0):
        if i == 0:
            affix = affix + ',' +  a['name']
        else:
            affix = affix + '-' +  a['name']
    return affix

# Parse the data for roster 
def get_roster_data(roster_data):
    roster = ''
    for i, r in enumerate(roster_data, start=0):
        roster = roster + ',' + r['character']['name'] + ',' + \
        r['character']['faction'] + ',' + \
        r['character']['race']['name'] + ',' + \
        r['character']['class']['name'] + ',' + \
        r['character']['spec']['name']
    return roster


if __name__ == '__main__':
    main()