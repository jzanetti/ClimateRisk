from pandas import DataFrame
from climada.hazard import Centroids

from climada.hazard.centroids.centr import Centroids as Centroids_type
from climada.entity.impact_funcs import impact_func_set

from yaml import safe_load
from geopandas import read_file as geopandas_read_file
from geopandas.geodataframe import GeoDataFrame
from numpy import NaN, nanmin, nanmax


def create_climada_petal_year_range(year_range_str: str or None) -> tuple:
    """Convert year range from str (e.g., 2011-2012) to a tuple
        (e.g., (2011-01-01, 2012-01-01))

    Args:
        year_range_str (str): year range in a string

    Returns:
        tuple: tuple for year range
    """
    if year_range_str is None:
        return None

    year_start = year_range_str[0:4]
    year_end = year_range_str[5:]

    return (
        f"{year_start}-01-01",
        f"{year_end}-01-01",
    )


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

    return {"haz_type": haz_type, "haz_id": haz_id}


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

    total_true = 0

    for datatype2check in value_adjustment_option:
        if value_adjustment_option[datatype2check]:
            total_true += 1

    if total_true > 1:
        raise Exception(
            "More than 1 value adjustments (fix, litpop, gdp2asset) is set to True"
        )

    return True


def get_exposure_range(
    exp_obj_gdf: GeoDataFrame, min_ratio: float = 0.75, max_ratio: float = 1.2
) -> dict:
    """Get range to be plotted

    Args:
        exp_obj_gdf (GeoDataFrame): _description_
        min_ratio (float, optional): _description_. Defaults to 0.75.
        max_ratio (float, optional): _description_. Defaults to 1.0.

    Returns:
        dict: _description_
    """

    all_values = exp_obj_gdf.value.values
    return {
        "min": min_ratio * nanmin(all_values),
        "max": max_ratio * nanmax(all_values),
    }
