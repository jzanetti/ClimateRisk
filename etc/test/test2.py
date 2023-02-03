from pandas import read_hdf

tc_data = "/Users/zhans/climada/data/hazard/tropical_cyclone/tropical_cyclone_10synth_tracks_150arcsec_NZL_1980_2020/v2/tropical_cyclone_10synth_tracks_150arcsec_NZL_1980_2020.hdf5"

# data = read_hdf(tc_data)

import h5py

fid = h5py.File(tc_data, "r")

print(fid.keys())

print(fid["centroids"])

data = list(fid["centroids"])

fid.close()
