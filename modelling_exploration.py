import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np

# # the data file needs to be in the folder with this script
# data_file = 'Providence_Pokemon.xls'
# df = pd.read_excel(io=data_file)
#
# df_poke_spawn_times = df['Time arriving']
#
# df_time_delta = (df_poke_spawn_times-df_poke_spawn_times.shift()).fillna(0)
#
# time_delta_list = df_time_delta.tolist()
#
# mean, std = norm.fit(time_delta_list)
# print(mean)
# print(std)
#
# plt.hist(time_delta_list, bins=30, normed=True)
# xmin, xmax = plt.xlim()
# x = np.linspace(xmin, xmax, 100)
# y = norm.pdf(x, mean, std)
# plt.plot(x, y)
# plt.show()

weight_file = 'xy_weights.xlsx'
df = pd.read_excel(io=weight_file)


for i, row in df.iterrows():
    print(row.values.argmax())
print(df)
