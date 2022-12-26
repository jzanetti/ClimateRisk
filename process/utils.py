from pandas import DataFrame
from climada.hazard import Centroids

from climada.hazard.centroids.centr import Centroids as Centroids_type
from climada.entity.impact_funcs import impact_func_set

from yaml import safe_load
from geopandas import read_file as geopandas_read_file
from geopandas.geodataframe import GeoDataFrame


def str2list_for_year(str_input: str or None) -> list:
    """Convert str (e.g., 2011-2012) to a list (e.g., [2011, 2012])

    Args:
        str_input (str): year range, e.g., 2011-2012

    Returns:
        list: year range in a list
    """

    if str_input is None:
        return None

    str_input = str_input.split("-")

    return [int(i) for i in str_input]


def read_basemap(base_map_path: str) -> GeoDataFrame:
    """Read basemap

    Returns:
        _type_: _description_
    """
    return geopandas_read_file(base_map_path)


def gdf2centroids(gdf: DataFrame) -> Centroids_type:
    """Return centroids from pandas Datatfame

    Args:
        gdf (DataFrame): pandas Dataframe, e.g., from LitPop

    Returns:
        _type_: _description_
    """
    lat = gdf["latitude"].values
    lon = gdf["longitude"].values
    return Centroids.from_lat_lon(lat, lon)


def get_hazard_info(impf_set: impact_func_set) -> dict:
    """Get hazard information

    Args:
        impf_set (impact_func_set): impact function to be used

    Returns:
        dict: the dict contains hazard types and IDs
    """
    [haz_type] = impf_set.get_hazard_types()
    [haz_id] = impf_set.get_ids()[haz_type]

    return {
        "haz_type": haz_type,
        "haz_id": haz_id
    }


def read_cfg(cfg_path: str) -> dict:
    """Read configuration file

    Args:
        cfg_path (str): configuration path

    Returns:
        dict: dict contains all configurations
    """
    with open(cfg_path, "r") as fid:
        cfg = safe_load(fid)
    
    return cfg

def check_exposure_value(value_adjustment_option: dict) -> bool:
    """Make sure exposure value adjutsment is right

    Args:
        value_adjustment_option (dict): _description_

    Raises:
        Exception: _description_

    Returns:
        bool: _description_
    """
    if value_adjustment_option["fix"] and value_adjustment_option["litpop"]:
        raise Exception("value adjustments (fix, litpop) are both set to True")

    return True



