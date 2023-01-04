
# conda activate climada_env
from climada_petals.hazard.river_flood import RiverFlood
from climada_petals.util.constants import HAZ_DEMO_FLDDPH, HAZ_DEMO_FLDFRC
import matplotlib.pyplot as plt
import pickle
from numpy import array

dph_path = "/Users/zhans/Downloads/flddph_150arcsec_clm40_gswp3_0.nc"
frc_path = "/Users/zhans/Downloads/fldfrc_150arcsec_clm40_gswp3_0.nc"

years = array(range(1979, 2010, 1)).tolist()
# years = None
# rf = RiverFlood.from_raster("etc/data/riverflood/riverflood_data.shp", haz_type="Flood")
rf = RiverFlood.from_nc(countries = ["NZL"], years=years, dph_path=dph_path, frc_path=frc_path)
# rf.write_raster("etc/data/riverflood/riverflood_data.shp", intensity=True)
pickle.dump(rf, open( "etc/data/riverflood/riverflood_data.pickle", "wb" ) )
# self.centroids.coord
# cmap = plt.cm.jet
# cmap.set_under("white") 
# rf.plot_intensity(event=0, smooth = False, adapt_fontsize=False, cmap=cmap, vmin=1.0, figsize=(15, 10))
# plt.savefig("/tmp/test.png", bbox_inches='tight',dpi=200)
# plt.close()
print("done")