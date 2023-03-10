RISK_COUNTRY = "New Zealand"
FUTURE_YEARS = 2080


# ------------------
# track and wind data are used for "get_benefit" and "get_impact"
# track2 is used for "get_supplychain"
# ------------------
TC_DATA = {
    "track": {
        "provider": "wellington",
        "year_range": None,  # # 2010-2012 or None
        "pert_tracks": 0,
    },
    "wind": {"pert_tracks": 10},
    "track2": {
        "countries": ["New Zealand", "Japan", "Australia", "China"],
        "year_range": "2010-2011",  # # 2010-2012 or None
        "pert_tracks": 1,
    },
}

LANDSLIDE_DATA = "etc/data/nasa_global_landslide_catalog_point/nasa_global_landslide_catalog_point.shp"
FLOOD_DATA = "etc/data/riverflood/riverflood_data.pickle"
GDP2ASSET_DATA = "etc/data/get_gdp/gdp2asset_nz.pickle"

INVALID_KEY = "invalid"

EXPOSURE_POINT_RES = 1000


# ------------------
# visualization
# ------------------
CMAP = {"exposure": "jet"}


# ------------------
# RCP assumptions
# ------------------
RCP_CFG = {
    "rcp26": {
        "events_num_incre": 0.01,
        "frequency_incre": 0.01,
        "intensity_incre": 0.015,
    },
    "rcp45": {
        "events_num_incre": 0.03,
        "frequency_incre": 0.03,
        "intensity_incre": 0.03,
    },
    "rcp60": {
        "events_num_incre": 0.05,
        "frequency_incre": 0.04,
        "intensity_incre": 0.05,
    },
}
HAZARD_CHCHE_DIR = "etc/data/cache"
