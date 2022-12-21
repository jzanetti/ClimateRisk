import geopandas as gpd
from climada.entity import Exposures
import numpy as np
road_path = "/Users/zhans/Github/ClimateRisk/exp/hello_world/lds-nz-road-centrelines-topo-150k-SHP/nz-road-centrelines-topo-150k.shp"
wellington_roads = gpd.read_file(road_path)
wellington_roads = wellington_roads.to_crs(epsg=4326)
exp_gpd = Exposures(wellington_roads)
exp_gpd.gdf["impf_WS"] = 1
exp_gpd.gdf["value"] = 1
exp_gpd.gdf.plot('value', cmap='inferno')
