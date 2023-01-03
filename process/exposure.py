from climada.util.api_client import Client
from process import LITPOP_DOMAIN
from climada.entity.exposures.base import Exposures
from process.utils import get_hazard_info, check_exposure_value
from climada.entity.impact_funcs import impact_func_set
from geopandas import read_file
import climada.util.lines_polys_handler as u_lp
from shapely.wkb import loads as wkb_loads
from shapely.wkb import dumps as wkb_dumps
from numpy import array as numpy_array
from scipy.spatial import cKDTree

from pandas import concat, Series
from geopandas import GeoDataFrame

from climada.hazard import TropCyclone
from process.utils import gdf2centroids

from pickle import load as pickle_load
from process import GDP2ASSET_DATA



def apply_asset_to_exposure(exp_obj: GeoDataFrame, litpop_obj: GeoDataFrame) -> GeoDataFrame:
    """Apply Litpop/gdp2asset value to an exposure

    Args:
        exp_obj (GeoDataFrame): _description_
        litpop_obj (GeoDataFrame): _description_

    Returns:
        _type_: _description_
    """
    if all(exp_obj.has_z):
        _drop_z = lambda exp_obj: wkb_loads(wkb_dumps(exp_obj, output_dimension=2))
        exp_obj.geometry = exp_obj.geometry.transform(_drop_z)

    exp_n = numpy_array(list(exp_obj.geometry.apply(lambda x: (x.x, x.y))))
    litpop_n = numpy_array(list(litpop_obj.geometry.apply(lambda x: (x.x, x.y))))
    litpop_btree = cKDTree(litpop_n)
    dist, idx = litpop_btree.query(exp_n, k=1)
    lippop_nearest = litpop_obj.iloc[idx].drop(columns="geometry").reset_index(drop=True)

    exp_obj = exp_obj.drop(columns=["value", "latitude", "geometry_orig", "longitude"])
    gdf = concat(
            [
                exp_obj.reset_index(drop=True),
                lippop_nearest,
                Series(dist, name='dist')
            ], 
        axis=1)

    return gdf


def get_exposure(input_cfg: dict) -> Exposures:
    """Get exposure object

    Args:
        input_cfg (str): input configuration

    Returns:
        dict: exposure object and type
    """
    if input_cfg["file"].endswith("shp"):
        exp_obj = get_from_shp(input_cfg["file"])

    else:
        raise Exception("input file type is not supported yet")


    print("Updating exposure object value ...")

    check_exposure_value(input_cfg["value_adjustment_option"])

    if input_cfg["value_adjustment_option"]["fix"]:

        print("Applying fixed value ...")

        if input_cfg["value_adjustment_option"]["fix"]["method"] == "total":
            exp_obj.gdf.value  = exp_obj.gdf.geometry_orig.length * (
                input_cfg["value_adjustment_option"]["fix"]["value"] / 
                exp_obj.gdf.geometry_orig.length.sum())

        elif input_cfg["value_adjustment_option"]["fix"]["method"] == "individual":
            exp_obj.gdf.value  = input_cfg["value_adjustment_option"]["fix"]["value"]

    else:

        print("Applying litpop/gdp values ...")

        exp_obj_latlon = get_exp_obj_latlon(exp_obj)

        if input_cfg["value_adjustment_option"]["litpop"]:
            ref_obj = get_from_litpop(exp_obj_latlon)

        elif input_cfg["value_adjustment_option"]["gdp2asset"]:
            ref_obj = get_from_gdp(exp_obj_latlon)

        exp_obj.gdf = apply_asset_to_exposure(exp_obj.gdf, ref_obj.gdf)

    return exp_obj


def get_exp_obj_latlon(exp_obj: Exposures) -> dict:
    """_summary_
    """
    return {
            "lats": [min(exp_obj.gdf["latitude"]), max(exp_obj.gdf["latitude"])],
            "lons": [min(exp_obj.gdf["longitude"]), max(exp_obj.gdf["longitude"])]
        }


def update_exposure(cfg: dict, exp_obj: Exposures, impacts: dict, hazards: dict) -> dict:
    """Combining Exposure with Impact function

    Args:
        cfg (dict): climaterisk configuration
        exp_obj (Exposures): Exposure object
        impact_func (dict): Impact function in a dict

    Returns:
        dict: Impact function dependant Exposure 
    """

    outputs = {}

    # check_exposure_value(cfg["input"]["value_adjustment_option"])

    for hazard_name in impacts:
        
        """
        if cfg["input"]["value_adjustment_option"]["litpop"]:
            litpop_obj = get_from_litpop(
                latlon = {
                    "lats": [min(exp_obj.gdf["latitude"]), max(exp_obj.gdf["latitude"])],
                    "lons": [min(exp_obj.gdf["longitude"]), max(exp_obj.gdf["longitude"])]
                }
            )
            exp_obj.gdf = apply_asset_to_exposure(exp_obj.gdf, litpop_obj.gdf)

        if cfg["input"]["value_adjustment_option"]["gdp2asset"]:
            gdp2asset_obj = pickle_load(open(GDP2ASSET_DATA, "rb"))
            exp_obj.gdf = apply_asset_to_exposure(exp_obj.gdf, gdp2asset_obj.gdf)

        if cfg["input"]["value_adjustment_option"]["fix"]:
            if cfg["input"]["value_adjustment_option"]["fix"]["method"] == "total":
                exp_obj.gdf.value  = exp_obj.gdf.geometry_orig.length * (
                    cfg["input"]["value_adjustment_option"]["fix"]["value"] / exp_obj.gdf.geometry_orig.length.sum())
            elif cfg["input"]["value_adjustment_option"]["fix"]["method"] == "individual":
                exp_obj.gdf.value  = cfg["input"]["value_adjustment_option"]["fix"]["value"]
        """
        exposure_obj = assign_impact(exp_obj, impacts[hazard_name])
        
        exp_centroids = gdf2centroids(exposure_obj.gdf)
        
        if hazard_name == "TC":
            update_hazard = TropCyclone.from_tracks(hazards[hazard_name], centroids=exp_centroids)
        elif hazard_name in ["landslide", "flood"]:
            update_hazard = hazards[hazard_name]
        else:
            raise Exception(f"Hazard {hazard_name} is not supported yet ...")

        outputs[hazard_name] = {
            "exposure": exposure_obj,
            "impact": impacts[hazard_name],
            "updated_hazard": update_hazard,
            "hazard": hazards[hazard_name]
        }

    return outputs


def get_from_shp(shp_file: str, res: int = 1000, crs_target: int or None = 4326) -> Exposures:
    """Get shapefile object

    Args:
        shp_file (str): shapefile to be used
        crs_target (int or None): CRS to be used

    Returns:
        _type_: _description_
    """
    shp_obj = read_file(shp_file)

    if crs_target is not None:
        shp_obj = shp_obj.to_crs(crs_target)

    exp_obj = Exposures(shp_obj)
    exp_obj.gdf["value"] = 1

    exp_obj = u_lp.exp_geom_to_pnt(
         exp_obj, res=res, to_meters=True, disagg_met=u_lp.DisaggMethod.FIX, disagg_val=None
    )

    return exp_obj


def get_from_litpop(latlon: dict or None = None) -> Exposures:
    """Get Litpop data

    Returns:
        Exposures: Exposures based on LitPop
    """
    client = Client()
    litpop_obj = client.get_litpop(country=LITPOP_DOMAIN)

    if latlon is not None:
        gdf = litpop_obj.gdf
        filtered_gdf = gdf[
            (gdf['latitude'] >= latlon["lats"][0]) & 
            (gdf['latitude'] <= latlon["lats"][1]) &
            (gdf['longitude'] >= latlon["lons"][0]) & 
            (gdf['longitude'] <= latlon["lons"][1])]

        litpop_obj.gdf = filtered_gdf

    return litpop_obj


def get_from_gdp(latlon: dict or None = None, gdp_year: int = 2000) -> Exposures:
    """_summary_

    Args:
        latlon (dictorNone, optional): _description_. Defaults to None.

    Returns:
        Exposures: _description_
    """
    gdp2asset_obj = pickle_load(open(GDP2ASSET_DATA, "rb"))

    if latlon is not None:
        gdf = gdp2asset_obj.gdf
        filtered_gdf = gdf[
            (gdf['latitude'] >= latlon["lats"][0]) & 
            (gdf['latitude'] <= latlon["lats"][1]) &
            (gdf['longitude'] >= latlon["lons"][0]) & 
            (gdf['longitude'] <= latlon["lons"][1])]

        gdp2asset_obj.gdf = filtered_gdf

    return gdp2asset_obj


def assign_impact(exp_obj, impact_func: impact_func_set):
    """Assign impact to exposure object

    Args:
        exp_obj (_type_): _description_
        impact_func (impact_func_set): _description_

    Returns:
        _type_: _description_
    """
    hazard_info = get_hazard_info(impact_func)
    exp_obj.gdf.rename(columns={"impf_": "impf_" + hazard_info["haz_type"]}, inplace=True)
    exp_obj.gdf['impf_' + hazard_info["haz_type"]] = hazard_info["haz_id"]

    return exp_obj