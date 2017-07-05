import numpy as np
import pandas as pd
from sklearn import model_selection, preprocessing
import xgboost as xgb

#load files
train = pd.read_csv('train.csv', parse_dates=['timestamp'])
test = pd.read_csv('test.csv', parse_dates=['timestamp'])

id_test = test.id

#clean data
bad_index = train[train.life_sq > train.full_sq].index
train.loc[bad_index, "life_sq"] = np.NaN
equal_index = [601,1896,2791]
test.loc[equal_index, "life_sq"] = test.loc[equal_index, "full_sq"]
bad_index = test[test.life_sq > test.full_sq].index
test.loc[bad_index, "life_sq"] = np.NaN
bad_index = train[train.life_sq < 5].index
train.loc[bad_index, "life_sq"] = np.NaN
bad_index = test[test.life_sq < 5].index
test.loc[bad_index, "life_sq"] = np.NaN
bad_index = train[train.full_sq < 5].index
train.loc[bad_index, "full_sq"] = np.NaN
bad_index = test[test.full_sq < 5].index
test.loc[bad_index, "full_sq"] = np.NaN
kitch_is_build_year = [13117]
train.loc[kitch_is_build_year, "build_year"] = train.loc[kitch_is_build_year, "kitch_sq"]
bad_index = train[train.kitch_sq >= train.life_sq].index
train.loc[bad_index, "kitch_sq"] = np.NaN
bad_index = test[test.kitch_sq >= test.life_sq].index
test.loc[bad_index, "kitch_sq"] = np.NaN
bad_index = train[(train.kitch_sq == 0).values + (train.kitch_sq == 1).values].index
train.loc[bad_index, "kitch_sq"] = np.NaN
bad_index = test[(test.kitch_sq == 0).values + (test.kitch_sq == 1).values].index
test.loc[bad_index, "kitch_sq"] = np.NaN
bad_index = train[(train.full_sq > 210) & (train.life_sq / train.full_sq < 0.3)].index
train.loc[bad_index, "full_sq"] = np.NaN
bad_index = test[(test.full_sq > 150) & (test.life_sq / test.full_sq < 0.3)].index
test.loc[bad_index, "full_sq"] = np.NaN
bad_index = train[train.life_sq > 300].index
train.loc[bad_index, ["life_sq", "full_sq"]] = np.NaN
bad_index = test[test.life_sq > 200].index
test.loc[bad_index, ["life_sq", "full_sq"]] = np.NaN
train.product_type.value_counts(normalize= True)
test.product_type.value_counts(normalize= True)
bad_index = train[train.build_year < 1500].index
train.loc[bad_index, "build_year"] = np.NaN
bad_index = test[test.build_year < 1500].index
test.loc[bad_index, "build_year"] = np.NaN
bad_index = train[train.num_room == 0].index
train.loc[bad_index, "num_room"] = np.NaN
bad_index = test[test.num_room == 0].index
test.loc[bad_index, "num_room"] = np.NaN
bad_index = [10076, 11621, 17764, 19390, 24007, 26713, 29172]
train.loc[bad_index, "num_room"] = np.NaN
bad_index = [3174, 7313]
test.loc[bad_index, "num_room"] = np.NaN
bad_index = train[(train.floor == 0).values * (train.max_floor == 0).values].index
train.loc[bad_index, ["max_floor", "floor"]] = np.NaN
bad_index = train[train.floor == 0].index
train.loc[bad_index, "floor"] = np.NaN
bad_index = train[train.max_floor == 0].index
train.loc[bad_index, "max_floor"] = np.NaN
bad_index = test[test.max_floor == 0].index
test.loc[bad_index, "max_floor"] = np.NaN
bad_index = train[train.floor > train.max_floor].index
train.loc[bad_index, "max_floor"] = np.NaN
bad_index = test[test.floor > test.max_floor].index
test.loc[bad_index, "max_floor"] = np.NaN
train.floor.describe(percentiles= [0.9999])
bad_index = [23584]
train.loc[bad_index, "floor"] = np.NaN
train.material.value_counts()
test.material.value_counts()
train.state.value_counts()
bad_index = train[train.state == 33].index
train.loc[bad_index, "state"] = np.NaN
test.state.value_counts()

# brings error down a lot by removing extreme price per sqm
train.loc[train.full_sq == 0, 'full_sq'] = 50
train = train[train.price_doc/train.full_sq <= 600000]
train = train[train.price_doc/train.full_sq >= 10000]

# Add month-year
month_year = (train.timestamp.dt.month + train.timestamp.dt.year * 100)
month_year_cnt_map = month_year.value_counts().to_dict()
train['month_year_cnt'] = month_year.map(month_year_cnt_map)

month_year = (test.timestamp.dt.month + test.timestamp.dt.year * 100)
month_year_cnt_map = month_year.value_counts().to_dict()
test['month_year_cnt'] = month_year.map(month_year_cnt_map)

# Add week-year count
week_year = (train.timestamp.dt.weekofyear + train.timestamp.dt.year * 100)
week_year_cnt_map = week_year.value_counts().to_dict()
train['week_year_cnt'] = week_year.map(week_year_cnt_map)

week_year = (test.timestamp.dt.weekofyear + test.timestamp.dt.year * 100)
week_year_cnt_map = week_year.value_counts().to_dict()
test['week_year_cnt'] = week_year.map(week_year_cnt_map)

# Add month and day-of-week
train['month'] = train.timestamp.dt.month
train['dow'] = train.timestamp.dt.dayofweek

test['month'] = test.timestamp.dt.month
test['dow'] = test.timestamp.dt.dayofweek

# Other feature engineering
train['rel_floor'] = train['floor'] / train['max_floor'].astype(float)
train['rel_kitch_sq'] = train['kitch_sq'] / train['full_sq'].astype(float)

test['rel_floor'] = test['floor'] / test['max_floor'].astype(float)
test['rel_kitch_sq'] = test['kitch_sq'] / test['full_sq'].astype(float)

train.apartment_name=train.sub_area + train['metro_km_avto'].astype(str)
test.apartment_name=test.sub_area + train['metro_km_avto'].astype(str)

train['room_size'] = train['life_sq'] / train['num_room'].astype(float)
test['room_size'] = test['life_sq'] / test['num_room'].astype(float)

# Aggreagte house price data derived from 
# http://www.globalpropertyguide.com/real-estate-house-prices/R#russia
# by luckyzhou
# See https://www.kaggle.com/luckyzhou/lzhou-test/comments

# rate_2015_q2 = 1
# rate_2015_q1 = rate_2015_q2 / .9932
# rate_2014_q4 = rate_2015_q1 / 1.0112
# rate_2014_q3 = rate_2014_q4 / 1.0169
# rate_2014_q2 = rate_2014_q3 / 1.0086
# rate_2014_q1 = rate_2014_q2 / 1.0126
# rate_2013_q4 = rate_2014_q1 / 0.9902
# rate_2013_q3 = rate_2013_q4 / 1.0041
# rate_2013_q2 = rate_2013_q3 / 1.0044
# rate_2013_q1 = rate_2013_q2 / 1.0104  # This is 1.002 (relative to mult), close to 1:
# rate_2012_q4 = rate_2013_q1 / 0.9832  #     maybe use 2013q1 as a base quarter and get rid of mult?
# rate_2012_q3 = rate_2012_q4 / 1.0277
# rate_2012_q2 = rate_2012_q3 / 1.0279
# rate_2012_q1 = rate_2012_q2 / 1.0279
# rate_2011_q4 = rate_2012_q1 / 1.076
# rate_2011_q3 = rate_2011_q4 / 1.0236
# rate_2011_q2 = rate_2011_q3 / 1
# rate_2011_q1 = rate_2011_q2 / 1.011


# train 2015
# train['average_q_price'] = 1

# train_2015_q2_index = train.loc[train['timestamp'].dt.year == 2015].loc[train['timestamp'].dt.month >= 4].loc[train['timestamp'].dt.month < 7].index
# train.loc[train_2015_q2_index, 'average_q_price'] = rate_2015_q2

# train_2015_q1_index = train.loc[train['timestamp'].dt.year == 2015].loc[train['timestamp'].dt.month >= 1].loc[train['timestamp'].dt.month < 4].index
# train.loc[train_2015_q1_index, 'average_q_price'] = rate_2015_q1


# # train 2014
# train_2014_q4_index = train.loc[train['timestamp'].dt.year == 2014].loc[train['timestamp'].dt.month >= 10].loc[train['timestamp'].dt.month <= 12].index
# train.loc[train_2014_q4_index, 'average_q_price'] = rate_2014_q4

# train_2014_q3_index = train.loc[train['timestamp'].dt.year == 2014].loc[train['timestamp'].dt.month >= 7].loc[train['timestamp'].dt.month < 10].index
# train.loc[train_2014_q3_index, 'average_q_price'] = rate_2014_q3

# train_2014_q2_index = train.loc[train['timestamp'].dt.year == 2014].loc[train['timestamp'].dt.month >= 4].loc[train['timestamp'].dt.month < 7].index
# train.loc[train_2014_q2_index, 'average_q_price'] = rate_2014_q2

# train_2014_q1_index = train.loc[train['timestamp'].dt.year == 2014].loc[train['timestamp'].dt.month >= 1].loc[train['timestamp'].dt.month < 4].index
# train.loc[train_2014_q1_index, 'average_q_price'] = rate_2014_q1


# # train 2013
# train_2013_q4_index = train.loc[train['timestamp'].dt.year == 2013].loc[train['timestamp'].dt.month >= 10].loc[train['timestamp'].dt.month <= 12].index
# train.loc[train_2013_q4_index, 'average_q_price'] = rate_2013_q4

# train_2013_q3_index = train.loc[train['timestamp'].dt.year == 2013].loc[train['timestamp'].dt.month >= 7].loc[train['timestamp'].dt.month < 10].index
# train.loc[train_2013_q3_index, 'average_q_price'] = rate_2013_q3

# train_2013_q2_index = train.loc[train['timestamp'].dt.year == 2013].loc[train['timestamp'].dt.month >= 4].loc[train['timestamp'].dt.month < 7].index
# train.loc[train_2013_q2_index, 'average_q_price'] = rate_2013_q2

# train_2013_q1_index = train.loc[train['timestamp'].dt.year == 2013].loc[train['timestamp'].dt.month >= 1].loc[train['timestamp'].dt.month < 4].index
# train.loc[train_2013_q1_index, 'average_q_price'] = rate_2013_q1


# # train 2012
# train_2012_q4_index = train.loc[train['timestamp'].dt.year == 2012].loc[train['timestamp'].dt.month >= 10].loc[train['timestamp'].dt.month <= 12].index
# train.loc[train_2012_q4_index, 'average_q_price'] = rate_2012_q4

# train_2012_q3_index = train.loc[train['timestamp'].dt.year == 2012].loc[train['timestamp'].dt.month >= 7].loc[train['timestamp'].dt.month < 10].index
# train.loc[train_2012_q3_index, 'average_q_price'] = rate_2012_q3

# train_2012_q2_index = train.loc[train['timestamp'].dt.year == 2012].loc[train['timestamp'].dt.month >= 4].loc[train['timestamp'].dt.month < 7].index
# train.loc[train_2012_q2_index, 'average_q_price'] = rate_2012_q2

# train_2012_q1_index = train.loc[train['timestamp'].dt.year == 2012].loc[train['timestamp'].dt.month >= 1].loc[train['timestamp'].dt.month < 4].index
# train.loc[train_2012_q1_index, 'average_q_price'] = rate_2012_q1


# # train 2011
# train_2011_q4_index = train.loc[train['timestamp'].dt.year == 2011].loc[train['timestamp'].dt.month >= 10].loc[train['timestamp'].dt.month <= 12].index
# train.loc[train_2011_q4_index, 'average_q_price'] = rate_2011_q4

# train_2011_q3_index = train.loc[train['timestamp'].dt.year == 2011].loc[train['timestamp'].dt.month >= 7].loc[train['timestamp'].dt.month < 10].index
# train.loc[train_2011_q3_index, 'average_q_price'] = rate_2011_q3

# train_2011_q2_index = train.loc[train['timestamp'].dt.year == 2011].loc[train['timestamp'].dt.month >= 4].loc[train['timestamp'].dt.month < 7].index
# train.loc[train_2011_q2_index, 'average_q_price'] = rate_2011_q2

# train_2011_q1_index = train.loc[train['timestamp'].dt.year == 2011].loc[train['timestamp'].dt.month >= 1].loc[train['timestamp'].dt.month < 4].index
# train.loc[train_2011_q1_index, 'average_q_price'] = rate_2011_q1

# train['price_doc'] = train['price_doc'] * train['average_q_price']

# mult = 1.054
# train['price_doc'] = train['price_doc'] * mult
y_train = np.log(train["price_doc"])

x_train = train.drop(["id", "timestamp", "price_doc"], axis=1)
#x_test = test.drop(["id", "timestamp", "average_q_price"], axis=1)
x_test = test.drop(["id", "timestamp"], axis=1)

num_train = len(x_train)
x_all = pd.concat([x_train, x_test])

for c in x_all.columns:
    if x_all[c].dtype == 'object':
        lbl = preprocessing.LabelEncoder()
        lbl.fit(list(x_all[c].values))
        x_all[c] = lbl.transform(list(x_all[c].values))

x_train = x_all[:num_train]
x_test = x_all[num_train:]


xgb_params = {
    'eta': 0.05,
    'max_depth': 6,
    'subsample': 0.6,
    'colsample_bytree': 1,
    'objective': 'reg:linear',
    'eval_metric': 'rmse',
    'silent': 1
}

dtrain = xgb.DMatrix(x_train, y_train)
dtest = xgb.DMatrix(x_test)


num_boost_rounds = 422
model = xgb.train(dict(xgb_params, silent=0), dtrain, num_boost_round=num_boost_rounds)


y_predict = model.predict(dtest)
gunja_output = pd.DataFrame({'id': id_test, 'price_doc': y_predict})

train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

id_test = test.id

mult = .969

y_train = np.log(train["price_doc"] * mult + 10)
x_train = train.drop(["id", "timestamp", "price_doc"], axis=1)
x_test = test.drop(["id", "timestamp"], axis=1)

for c in x_train.columns:
    if x_train[c].dtype == 'object':
        lbl = preprocessing.LabelEncoder()
        lbl.fit(list(x_train[c].values))
        x_train[c] = lbl.transform(list(x_train[c].values))

for c in x_test.columns:
    if x_test[c].dtype == 'object':
        lbl = preprocessing.LabelEncoder()
        lbl.fit(list(x_test[c].values))
        x_test[c] = lbl.transform(list(x_test[c].values))

xgb_params = {
    'eta': 0.05,
    'max_depth': 5,
    'subsample': 0.7,
    'colsample_bytree': 0.7,
    'objective': 'reg:linear',
    'eval_metric': 'rmse',
    'silent': 1
}

dtrain = xgb.DMatrix(x_train, y_train)
dtest = xgb.DMatrix(x_test)

num_boost_rounds = 385  # This was the CV output, as earlier version shows
model = xgb.train(dict(xgb_params, silent=0), dtrain, num_boost_round= num_boost_rounds)

y_predict = model.predict(dtest)
output = pd.DataFrame({'id': id_test, 'price_doc': y_predict})

df_train = pd.read_csv("train.csv", parse_dates=['timestamp'])
df_test = pd.read_csv("test.csv", parse_dates=['timestamp'])
df_macro = pd.read_csv("macro.csv", parse_dates=['timestamp'])


df_train.drop(df_train[df_train["life_sq"] > 7000].index, inplace=True)

y_train = np.log(df_train['price_doc'].values)
id_test = df_test['id']

df_train.drop(['id', 'price_doc'], axis=1, inplace=True)
df_test.drop(['id'], axis=1, inplace=True)

test_2015 = df_test[df_test.timestamp.dt.year == 2015].index
test_2016 = df_test[df_test.timestamp.dt.year == 2016].index

test_2015_7_0 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 7) & (df_test.timestamp.dt.day <= 15)].index
test_2015_7_1 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 7) & (df_test.timestamp.dt.day > 15)].index
test_2015_7 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 7)].index

test_2015_8_0 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 8) & (df_test.timestamp.dt.day <= 15)].index
test_2015_8_1 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 8) & (df_test.timestamp.dt.day > 15)].index
test_2015_8 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 8)].index

test_2015_9_0 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 9) & (df_test.timestamp.dt.day <= 15)].index
test_2015_9_1 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 9) & (df_test.timestamp.dt.day > 15)].index
test_2015_9 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 9)].index

test_2015_10_0 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 10) & (df_test.timestamp.dt.day <= 15)].index
test_2015_10_1 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 10) & (df_test.timestamp.dt.day > 15)].index
test_2015_10 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 10)].index

test_2015_11_0 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 11) & (df_test.timestamp.dt.day <= 15)].index
test_2015_11_1 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 11) & (df_test.timestamp.dt.day > 15)].index
test_2015_11 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 11)].index

test_2015_12_0 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 12) & (df_test.timestamp.dt.day <= 15)].index
test_2015_12_1 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 12) & (df_test.timestamp.dt.day > 15)].index
test_2015_12 = df_test[(df_test.timestamp.dt.year == 2015) & (df_test.timestamp.dt.month == 12)].index

test_2016_1_0 = df_test[(df_test.timestamp.dt.year == 2016) & (df_test.timestamp.dt.month == 1) & (df_test.timestamp.dt.day <= 15)].index
test_2016_1_1 = df_test[(df_test.timestamp.dt.year == 2016) & (df_test.timestamp.dt.month == 1) & (df_test.timestamp.dt.day > 15)].index
test_2016_1 = df_test[(df_test.timestamp.dt.year == 2016) & (df_test.timestamp.dt.month == 1)].index

test_2016_2_0 = df_test[(df_test.timestamp.dt.year == 2016) & (df_test.timestamp.dt.month == 2) & (df_test.timestamp.dt.day <= 15)].index
test_2016_2_1 = df_test[(df_test.timestamp.dt.year == 2016) & (df_test.timestamp.dt.month == 2) & (df_test.timestamp.dt.day > 15)].index
test_2016_2 = df_test[(df_test.timestamp.dt.year == 2016) & (df_test.timestamp.dt.month == 2)].index
test_2016_3 = df_test[(df_test.timestamp.dt.year == 2016) & (df_test.timestamp.dt.month == 3)].index
test_2016_4 = df_test[(df_test.timestamp.dt.year == 2016) & (df_test.timestamp.dt.month == 4)].index
test_2016_5 = df_test[(df_test.timestamp.dt.year == 2016) & (df_test.timestamp.dt.month == 5)].index

num_train = len(df_train)
df_all = pd.concat([df_train, df_test])
# Next line just adds a lot of NA columns (becuase "join" only works on indexes)
# but somewhow it seems to affect the result
df_all = df_all.join(df_macro, on='timestamp', rsuffix='_macro')
print(df_all.shape)

# Add month-year
month_year = (df_all.timestamp.dt.month + df_all.timestamp.dt.year * 100)
month_year_cnt_map = month_year.value_counts().to_dict()
df_all['month_year_cnt'] = month_year.map(month_year_cnt_map)

# Add week-year count
week_year = (df_all.timestamp.dt.weekofyear + df_all.timestamp.dt.year * 100)
week_year_cnt_map = week_year.value_counts().to_dict()
df_all['week_year_cnt'] = week_year.map(week_year_cnt_map)

# Add month and day-of-week
df_all['month'] = df_all.timestamp.dt.month
df_all['dow'] = df_all.timestamp.dt.dayofweek

# Other feature engineering
df_all['rel_floor'] = df_all['floor'] / df_all['max_floor'].astype(float)
df_all['rel_kitch_sq'] = df_all['kitch_sq'] / df_all['full_sq'].astype(float)

train['building_name'] = pd.factorize(train.sub_area + train['metro_km_avto'].astype(str))[0]
test['building_name'] = pd.factorize(test.sub_area + test['metro_km_avto'].astype(str))[0]

def add_time_features(col):
   col_month_year = pd.Series(pd.factorize(train[col].astype(str) + month_year.astype(str))[0])
   train[col + '_month_year_cnt'] = col_month_year.map(col_month_year.value_counts())

   col_week_year = pd.Series(pd.factorize(train[col].astype(str) + week_year.astype(str))[0])
   train[col + '_week_year_cnt'] = col_week_year.map(col_week_year.value_counts())

add_time_features('building_name')
add_time_features('sub_area')

def add_time_features(col):
   col_month_year = pd.Series(pd.factorize(test[col].astype(str) + month_year.astype(str))[0])
   test[col + '_month_year_cnt'] = col_month_year.map(col_month_year.value_counts())

   col_week_year = pd.Series(pd.factorize(test[col].astype(str) + week_year.astype(str))[0])
   test[col + '_week_year_cnt'] = col_week_year.map(col_week_year.value_counts())

add_time_features('building_name')
add_time_features('sub_area')


# Remove timestamp column (may overfit the model in train)
df_all.drop(['timestamp', 'timestamp_macro'], axis=1, inplace=True)


factorize = lambda t: pd.factorize(t[1])[0]

df_obj = df_all.select_dtypes(include=['object'])

X_all = np.c_[
    df_all.select_dtypes(exclude=['object']).values,
    np.array(list(map(factorize, df_obj.iteritems()))).T
]
print(X_all.shape)

X_train = X_all[:num_train]
X_test = X_all[num_train:]


# Deal with categorical values
df_numeric = df_all.select_dtypes(exclude=['object'])
df_obj = df_all.select_dtypes(include=['object']).copy()

for c in df_obj:
    df_obj[c] = pd.factorize(df_obj[c])[0]

df_values = pd.concat([df_numeric, df_obj], axis=1)


# Convert to numpy values
X_all = df_values.values
print(X_all.shape)

X_train = X_all[:num_train]
X_test = X_all[num_train:]

df_columns = df_values.columns


xgb_params = {
    'eta': 0.05,
    'max_depth': 5,
    'subsample': 0.7,
    'colsample_bytree': 0.7,
    'objective': 'reg:linear',
    'eval_metric': 'rmse',
    'silent': 1
}

dtrain = xgb.DMatrix(X_train, y_train, feature_names=df_columns)
dtest = xgb.DMatrix(X_test, feature_names=df_columns)

num_boost_rounds = 420  # From Bruno's original CV, I think
model = xgb.train(dict(xgb_params, silent=0), dtrain, num_boost_round=num_boost_rounds)

y_pred = model.predict(dtest)

df_sub = pd.DataFrame({'id': id_test, 'price_doc': y_pred})

first_result = output.merge(df_sub, on="id", suffixes=['_louis','_bruno'])
first_result["price_doc"] =  0.714 * np.exp(first_result.price_doc_louis) + 0.286 * np.exp(first_result.price_doc_bruno)  
result = first_result.merge(gunja_output, on="id", suffixes=['_follow','_gunja'])

result["price_doc"] =  0.78 * result.price_doc_follow + 0.22 * np.exp(result.price_doc_gunja) 

# result.loc[test_2015, 'price_doc'] = result.loc[test_2015, 'price_doc'] * 0.968
# result.loc[test_2016, 'price_doc'] = result.loc[test_2016, 'price_doc'] * 1.01

# result.loc[test_2015_7_0, 'price_doc'] = result.loc[test_2015_7_0, 'price_doc'] * 0.978
# result.loc[test_2015_7_1, 'price_doc'] = result.loc[test_2015_7_1, 'price_doc'] * 0.972
result.loc[test_2015_7, 'price_doc'] = result.loc[test_2015_7, 'price_doc'] * 0.975

# result.loc[test_2015_8_0, 'price_doc'] = result.loc[test_2015_8_0, 'price_doc'] * 0.965
# result.loc[test_2015_8_1, 'price_doc'] = result.loc[test_2015_8_1, 'price_doc'] * 0.975
result.loc[test_2015_8, 'price_doc'] = result.loc[test_2015_8, 'price_doc'] * 0.97

# result.loc[test_2015_9_0, 'price_doc'] = result.loc[test_2015_9_0, 'price_doc'] * 0.961
# result.loc[test_2015_9_1, 'price_doc'] = result.loc[test_2015_9_1, 'price_doc'] * 0.954
result.loc[test_2015_9, 'price_doc'] = result.loc[test_2015_9, 'price_doc'] * 0.958

# result.loc[test_2015_10_0, 'price_doc'] = result.loc[test_2015_10_0, 'price_doc'] * 0.968
# result.loc[test_2015_10_1, 'price_doc'] = result.loc[test_2015_10_1, 'price_doc'] * 0.963
result.loc[test_2015_10, 'price_doc'] = result.loc[test_2015_10, 'price_doc'] * 0.966

# result.loc[test_2015_11_0, 'price_doc'] = result.loc[test_2015_11_0, 'price_doc'] * 0.978
# result.loc[test_2015_11_1, 'price_doc'] = result.loc[test_2015_11_1, 'price_doc'] * 0.974
result.loc[test_2015_11, 'price_doc'] = result.loc[test_2015_11, 'price_doc'] * 0.976

# result.loc[test_2015_12_0, 'price_doc'] = result.loc[test_2015_12_0, 'price_doc'] * 0.96
# result.loc[test_2015_12_1, 'price_doc'] = result.loc[test_2015_12_1, 'price_doc'] * 0.97
result.loc[test_2015_12, 'price_doc'] = result.loc[test_2015_12, 'price_doc'] * 0.965

# result.loc[test_2016_1_0, 'price_doc'] = result.loc[test_2016_1_0, 'price_doc'] * 0.988
# result.loc[test_2016_1_1, 'price_doc'] = result.loc[test_2016_1_1, 'price_doc'] * 0.996
result.loc[test_2016_1, 'price_doc'] = result.loc[test_2016_1, 'price_doc'] * 0.99

# result.loc[test_2016_2_0, 'price_doc'] = result.loc[test_2016_2_0, 'price_doc'] * 1.003
# result.loc[test_2016_2_1, 'price_doc'] = result.loc[test_2016_2_1, 'price_doc'] * 0.998
result.loc[test_2016_2, 'price_doc'] = result.loc[test_2016_2, 'price_doc'] * 1.001

result.loc[test_2016_3, 'price_doc'] = result.loc[test_2016_3, 'price_doc'] * 1.024
result.loc[test_2016_4, 'price_doc'] = result.loc[test_2016_4, 'price_doc'] * 1.015
result.loc[test_2016_5, 'price_doc'] = result.loc[test_2016_5, 'price_doc'] * 1.015
                              
# result["price_doc"] = result["price_doc"] *0.991        
result.drop(["price_doc_louis","price_doc_bruno","price_doc_follow","price_doc_gunja"],axis=1,inplace=True)
result.head()
result.to_csv('same_result.csv', index=False)