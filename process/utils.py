from pandas import DataFrame
from climada.hazard import Centroids

from climada.hazard.centroids.centr import Centroids as Centroids_type
from climada.entity.impact_funcs import impact_func_set

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
