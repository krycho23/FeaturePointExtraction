# Author: krycho23

# Comparison of robust scaler and min max scaler

# For first 6 matplotlib plots i used constant and linear data with outliers what is visualised in first 2 plots in next 2 plots i used min max scaler and then in last 2 plots i used robust scaler
# in last 2 kde plots i compared scalers for mytest and x data 
# first 3 plots are tested for x data the normal distribution concatenated data and outliers, outliers also are normal distribution
# second 3 plots are tested for the same data mytest as data tested in plots with matplotlib

# Results
# first 6 plots doesnt get me special results, i only visualised that data indeed was scaled
# kde plots for x data shows that robust scaler throw outliers far away
# kde plots for mytest data shows that in this examples robust scaler is not good beacuse doesnt behave the same apperance as before scaling, i think its because it doesnt use mean and in this examples i have constant mean value


import numpy as np
from mlxtend.preprocessing import minmax_scaling
from matplotlib import pyplot as plt
from sklearn.preprocessing import RobustScaler
import pandas as pd
from sklearn import preprocessing
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# TEST 1

nooutliers = 30 *np.ones(1000)

# outliers = 10 *np.random.random_sample((5,)) + 1300
outliers = 200 *np.random.random_sample((10,)) + 600

sum = np.copy(nooutliers)
for out in outliers:
  cord = int(1000 * np.random.random_sample((1,)))
  sum[cord] = out

plt.figure(figsize=(20, 10))
plt.title("constant data with outliers before scaling")
plt.plot(np.arange(1000), sum, 'ro')

################

nooutliers_linear = np.arange(1000)
sum_linear = np.copy(nooutliers_linear)
for out in outliers:
  cord = int(1000 * np.random.random_sample((1,)))
  sum_linear[cord] = out


plt.figure(figsize=(20, 10))
plt.title("linear data with outliers before scaling")
plt.plot(np.arange(1000), sum_linear, 'ro')

result_minmax = minmax_scaling(sum, columns=[0], min_val=0, max_val=1) # problem when we set 0 at min doesnt reach max
result_minmax_linear = minmax_scaling(sum_linear, columns=[0], min_val=0, max_val=1) # problem when we set 0 at min doesnt reach max

#######


# visualize scaler MinMax
plt.figure(figsize=(20, 10))
plt.title("constant data after min max scaling")
plt.plot(np.arange(1000), result_minmax, 'ro')

plt.figure(figsize=(20, 10))
plt.title("linear data after min max scaling")
plt.plot(np.arange(1000), result_minmax_linear, 'ro')


scaler = RobustScaler()

dfTest = pd.DataFrame({'Robust':sum, 'RobustLinear': sum_linear})

dfTest[['Robust', 'RobustLinear']] = scaler.fit_transform(dfTest[['Robust', 'RobustLinear']])

plt.figure(figsize=(20, 10))
plt.title("constant data after robust scaling")
plt.plot(np.arange(1000), dfTest['Robust'], 'ro')

plt.figure(figsize=(20, 10))
plt.title("linear data after robust scaling")
# plt.imshow(self.disparity,'gray')
plt.plot(np.arange(1000), dfTest['RobustLinear'], 'ro')

x = pd.DataFrame({
    # Distribution with lower outliers
    'x1': np.concatenate([np.random.normal(20, 1, 1000), np.random.normal(1, 1, 25)]),
    # Distribution with higher outliers
    'x2': np.concatenate([np.random.normal(30, 1, 1000), np.random.normal(50, 1, 25)]),
})

scaler = preprocessing.RobustScaler()
robust_scaled_df = scaler.fit_transform(x)
robust_scaled_df = pd.DataFrame(robust_scaled_df, columns=['x1', 'x2'])

scaler = preprocessing.MinMaxScaler()
minmax_scaled_df = scaler.fit_transform(x)
minmax_scaled_df = pd.DataFrame(minmax_scaled_df, columns=['x1', 'x2'])

fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(9, 5))
ax1.set_title('Before Scaling')
sns.kdeplot(x['x1'], ax=ax1)
sns.kdeplot(x['x2'], ax=ax1)
ax2.set_title('After Robust Scaling')
sns.kdeplot(robust_scaled_df['x1'], ax=ax2)
sns.kdeplot(robust_scaled_df['x2'], ax=ax2)
ax3.set_title('After Min-Max Scaling')
sns.kdeplot(minmax_scaled_df['x1'], ax=ax3)
sns.kdeplot(minmax_scaled_df['x2'], ax=ax3)
plt.show()


mytest = pd.DataFrame({
    # Distribution with lower outliers
    'x1': np.concatenate([nooutliers, outliers]),
    # Distribution with higher outliers
    'x2': np.concatenate([nooutliers_linear, outliers]),
})

scaler = preprocessing.RobustScaler()
robust_scaled_df = scaler.fit_transform(mytest)
robust_scaled_df = pd.DataFrame(robust_scaled_df, columns=['x1', 'x2'])

scaler = preprocessing.MinMaxScaler()
minmax_scaled_df = scaler.fit_transform(mytest)
minmax_scaled_df = pd.DataFrame(minmax_scaled_df, columns=['x1', 'x2'])

fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(9, 5))
ax1.set_title('Before Scaling')
sns.kdeplot(mytest['x1'], ax=ax1)
sns.kdeplot(mytest['x2'], ax=ax1)
ax2.set_title('After Robust Scaling')
sns.kdeplot(robust_scaled_df['x1'], ax=ax2)
sns.kdeplot(robust_scaled_df['x2'], ax=ax2)
ax3.set_title('After Min-Max Scaling')
sns.kdeplot(minmax_scaled_df['x1'], ax=ax3)
sns.kdeplot(minmax_scaled_df['x2'], ax=ax3)
plt.show()



