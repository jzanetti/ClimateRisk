


import numpy as np
from pandas import DataFrame
from climada.entity import Exposures

exp_df = DataFrame()
n_exp = 9

exp_df['value'] = np.arange(n_exp)
lat, lon = np.mgrid[15 : 35 : complex(0, np.sqrt(n_exp)), 20 : 40 : complex(0, np.sqrt(n_exp))]
exp_df['latitude'] = lat.flatten()
exp_df['longitude'] = lon.flatten()
exp_df['impf_TC'] = np.ones(n_exp, int)

exp = Exposures(exp_df)