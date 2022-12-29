

## GDP2Asset data can be obtained from https://www.isimip.org/, note that the data must be gridded
## For example,
# https://files.isimip.org/ISIMIP2b/InputData/gdp/2005soc/gdp_2005soc_0p5deg_annual_2006-2099.nc4
# https://files.isimip.org/ISIMIP2b/InputData/gdp/2005soc/gdp_2005soc_0p5deg_annual_2100-2299.nc4

# set exposure for damage calculation
from climada_petals.entity.exposures.gdp_asset import GDP2Asset
import pickle
from shapely.geometry import Point

gdpa = GDP2Asset()
gdpa.set_countries(countries = ['NZL'], ref_year = 2020, path="/Users/zhans/Downloads/gdp_2005soc_0p5deg_annual_2006-2099.nc4")
gdpa_gdf = gdpa.gdf
geometry = [Point(xy) for xy in zip(gdpa_gdf["longitude"], gdpa_gdf["latitude"])]
# Coordinate reference system : WGS84
crs = {'init': 'epsg:4326'}
# Creating a Geographic data frame 
gdpa_gdf = gdpa_gdf.set_geometry(geometry, crs)
gdpa.gdf = gdpa_gdf

pickle.dump(gdpa, open( "etc/data/get_gdp/gdp2asset_nz.pickle", "wb" ) )

#from matplotlib import colors, pyplot
#norm=colors.LogNorm(vmin=1.0e2, vmax=1.0e10)
#gdpa.plot_scatter()
#pyplot.savefig("test.png")
#pyplot.close()