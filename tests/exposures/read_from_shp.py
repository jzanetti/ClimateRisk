


import numpy as np
import geopandas as gpd
from climada.entity import Exposures
import matplotlib.pyplot as plt

world = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))
exp_gpd = Exposures(world)
exp_gpd.gdf['value'] = np.arange(world.shape[0])
exp_gpd.set_lat_lon()
exp_gpd.gdf['impf_TC'] = np.ones(world.shape[0], int)
axs = exp_gpd.plot_hexbin()
plt.savefig("test.png")
plt.close()
print("sdf")
