from climada.util.api_client import Client
from process import DOMAIN
from climada.entity.exposures.base import Exposures
from process.vis import plot_litpop
from process.utils import get_hazard_info
from climada.entity.impact_funcs import impact_func_set

def get_litpop(workdir: str, impact_func: impact_func_set, vis_flag: bool = False) -> Exposures:
    """Get Litpop data

    Args:
        workdir (str): working directory
        impact_func (impact_func_set): impact functions
        vis_flag (bool): if create LitPop visualization

    Returns:
        Exposures: Exposures based on LitPop
    """
    client = Client()
    litpop_obj = client.get_litpop(country=DOMAIN["country"])
    gdf = litpop_obj.gdf
    filtered_gdf = gdf[
        (gdf['latitude'] >= DOMAIN["lats"][0]) & 
        (gdf['latitude'] <= DOMAIN["lats"][1]) &
        (gdf['longitude'] >= DOMAIN["lons"][0]) & 
        (gdf['longitude'] <= DOMAIN["lons"][1])]

    litpop_obj.gdf = filtered_gdf

    hazard_info = get_hazard_info(impact_func)
    litpop_obj.gdf.rename(columns={"impf_": "impf_" + hazard_info["haz_type"]}, inplace=True)
    litpop_obj.gdf['impf_' + hazard_info["haz_type"]] = hazard_info["haz_id"]

    if vis_flag:
        plot_litpop(workdir, litpop_obj)

    return litpop_obj