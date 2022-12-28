
# conda activate climada_env
from climada_petals.hazard.river_flood import RiverFlood
from climada_petals.util.constants import HAZ_DEMO_FLDDPH, HAZ_DEMO_FLDFRC
import matplotlib.pyplot as plt
import pickle
from numpy import array

dph_path = "/Users/zhans/Downloads/flddph_150arcsec_clm40_gswp3_0.nc"
frc_path = "/Users/zhans/Downloads/fldfrc_150arcsec_clm40_gswp3_0.nc"

years = array(range(1990, 2001, 1)).tolist()
rf = RiverFlood.from_nc(countries = ["NZL"], years=years, dph_path=dph_path, frc_path=frc_path)
pickle.dump(rf, open( "etc/data/riverflood/riverflood_data.pickle", "wb" ) )
# self.centroids.coord
rf.plot_intensity(event=0, smooth = False)
plt.savefig("/tmp/test.png")
plt.close()