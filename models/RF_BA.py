#A simple Random Forest model which analyzes 
#bid and ask prices separately
#Generates the first ask and bid which is copied
#across the all the upcoming bid and ask
#as prediction
import pandas as pd
import numpy as np
from sklearn import ensemble

import pickle

#Read the data
print "Loading data..."
train_table = pd.DataFrame.from_csv('../data/subset_train_OHE.csv')
test_table = pd.DataFrame.from_csv('../data/subset_test_OHE.csv')

bidPredictionColumns = []
for i in range(52, 101):
	for column in train_table.columns.values:
		if column.endswith(str(i)) and column.startswith('bid'):
			bidPredictionColumns.append(column)

askPredictionColumns = []
for i in range(52, 101):
	for column in train_table.columns.values:
		if column.endswith(str(i)) and column.startswith('ask'):
			askPredictionColumns.append(column)

predictionColumns = bidPredictionColumns + askPredictionColumns

featureColumns = []
columnsToIgnore = []
for column in train_table.columns.values:
	if ((column not in predictionColumns) and (column not in columnsToIgnore) and (not column.startswith('time'))):
		featureColumns.append(column)

trainX = np.zeros((train_table.shape[0], len(featureColumns)))

trainY_ask = np.zeros((train_table.shape[0]))
trainY_bid = np.zeros((train_table.shape[0]))

testX = np.zeros((test_table.shape[0], len(featureColumns)))


print "Creating Predictors..."
index = 0
for ix, row in train_table.iterrows():
	X = (np.array(row[featureColumns])).flatten('F')
	Y_bid = row[bidPredictionColumns[0]]
	Y_ask = row[askPredictionColumns[0]]

	trainX[index, :] = X
	trainY_ask[index] = Y_ask
	trainY_bid[index] = Y_bid

	index = index+1

index = 0
for ix, row in test_table.iterrows():
	X = (np.array(row[featureColumns])).flatten('F')
	testX[index, :] = X

	index = index+1


print "Training..."
RF_model_ask = ensemble.RandomForestRegressor(n_estimators=200,
	criterion='mse',
	max_depth=None,
	min_samples_split=2, 
	min_samples_leaf=1, 
	min_weight_fraction_leaf=0.0, 
	max_features='auto', 
	max_leaf_nodes=None, 
	min_impurity_split=1e-07, 
	bootstrap=True, 
	oob_score=False, 
	n_jobs=-1, 
	random_state=None, 
	verbose=1, 
	warm_start=False)
RF_model_ask.fit(trainX, trainY_ask)

RF_model_bid = ensemble.RandomForestRegressor(n_estimators=200,
	criterion='mse',
	max_depth=None,
	min_samples_split=2, 
	min_samples_leaf=1, 
	min_weight_fraction_leaf=0.0, 
	max_features='auto', 
	max_leaf_nodes=None, 
	min_impurity_split=1e-07, 
	bootstrap=True, 
	oob_score=False, 
	n_jobs=-1, 
	random_state=None, 
	verbose=1, 
	warm_start=False)
RF_model_bid.fit(trainX, trainY_bid)

models = {'bid': RF_model_bid, 'ask': RF_model_ask}

with open('../run_models/RF_BA.model', 'wb') as output:
	pickle.dump(models, output, -1)


print "Predicting..."
testY_ask = RF_model_ask.predict(testX)
testY_bid = RF_model_bid.predict(testX)

prediction = pd.DataFrame.from_csv('../predictions/template_prediction.csv')

i = 0
for ix, row in test_table.iterrows():
	row_id = row['row_id']

	index_in_pred = prediction[prediction['row_id'] == row_id].index.tolist()[0]

	bid = testY_bid[i]
	ask = testY_ask[i]
	i = i+1

	for column in predictionColumns:
		if column.startswith('bid'):
			prediction.set_value(index_in_pred, column, bid)
		else:
			prediction.set_value(index_in_pred, column, ask)

prediction.to_csv('../predictions/RF_BA.csv')

print "Done!"