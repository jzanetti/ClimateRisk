from copy import deepcopy
from pickle import load as pickle_load

import climada.util.lines_polys_handler as u_lp
from climada.entity.exposures.base import Exposures
from climada.entity.impact_funcs import impact_func_set
from climada.hazard import TropCyclone
from climada.util.api_client import Client
from geopandas import GeoDataFrame, read_file
from numpy import array as numpy_array
from numpy import ones as numpy_ones
from pandas import Series, concat
from scipy.spatial import cKDTree
from shapely.wkb import dumps as wkb_dumps
from shapely.wkb import loads as wkb_loads

from process import EXPOSURE_POINT_RES, FUTURE_YEARS, GDP2ASSET_DATA, RISK_COUNTRY
from process.utils import check_exposure_value, gdf2centroids, get_hazard_info


def apply_asset_to_exposure(
    exp_obj: GeoDataFrame, litpop_obj: GeoDataFrame
) -> GeoDataFrame:
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
    lippop_nearest = (
        litpop_obj.iloc[idx].drop(columns="geometry").reset_index(drop=True)
    )

    exp_obj = exp_obj.drop(columns=["value", "latitude", "longitude"])
    gdf = concat(
        [exp_obj.reset_index(drop=True), lippop_nearest, Series(dist, name="dist")],
        axis=1,
    )

    return gdf


def get_exposure(
    input_cfg: dict, economy_growth: float or None = None, add_future: bool = False
) -> Exposures:
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
            exp_obj.gdf.value = exp_obj.gdf.geometry_orig.length * (
                input_cfg["value_adjustment_option"]["fix"]["value"]
                / exp_obj.gdf.geometry_orig.length.sum()
            )

        elif input_cfg["value_adjustment_option"]["fix"]["method"] == "individual":
            exp_obj.gdf.value = input_cfg["value_adjustment_option"]["fix"]["value"]

    else:

        print("Applying litpop/gdp values ...")

        exp_obj_latlon = get_exp_obj_latlon(exp_obj)

        if input_cfg["value_adjustment_option"]["litpop"]:
            ref_obj = get_from_litpop(exp_obj_latlon)

        elif input_cfg["value_adjustment_option"]["gdp2asset"]:
            ref_obj = get_from_gdp(exp_obj_latlon)

        exp_obj.gdf = apply_asset_to_exposure(exp_obj.gdf, ref_obj.gdf)

    future_exp_obj = None

    exp_obj.value_unit = "NZD"

    if add_future:
        future_exp_obj = add_future_exp(exp_obj, annual_growth_rate=economy_growth)

    return {"hist": exp_obj, "future": future_exp_obj}


def add_future_exp(
    exp_present: Exposures, annual_growth_rate: float = 0.02
) -> Exposures:
    """_summary_

    Args:
        exp_present (Exposures): _description_
        annual_growth_rate (float, optional): _description_. Defaults to 1.02.

    Returns:
        Exposures: _description_
    """
    exp_future = deepcopy(exp_present)

    exp_future.ref_year = FUTURE_YEARS

    n_years = exp_future.ref_year - exp_present.ref_year + 1

    growth = (1.0 + annual_growth_rate) ** n_years

    exp_future.gdf["value"] = exp_future.gdf["value"] * growth

    return exp_future


def get_exp_obj_latlon(exp_obj: Exposures) -> dict:
    """_summary_"""
    return {
        "lats": [min(exp_obj.gdf["latitude"]), max(exp_obj.gdf["latitude"])],
        "lons": [min(exp_obj.gdf["longitude"]), max(exp_obj.gdf["longitude"])],
    }


def update_exposure(
    exp_obj: Exposures,
    impacts: dict,
    hazards: dict,
    exp_flag: str = "hist",
    task_type: str = "impact",
) -> dict:
    """Combining Exposure with Impact function

    Args:
        exp_obj (Exposures): Exposure object
        impact_func (dict): Impact function in a dict
        use_all_years (bool): the hazard intensity is accumulated. Otherwise it is averaged to a single year.

    Returns:
        dict: Impact function dependant Exposure
    """

    outputs = {}

    for hazard_name in impacts:

        exposure_obj = assign_impact(exp_obj[exp_flag], impacts[hazard_name])

        if hazard_name == "TC":

            if task_type == "impact":
                update_hazard = hazards[hazard_name]
                # update_hazard = TropCyclone.from_tracks(
                #    hazards[hazard_name][exp_flag],
                #    centroids=gdf2centroids(exposure_obj.gdf),
                # )

            elif task_type == "supplychain":
                update_hazard = hazards[hazard_name]
            elif task_type == "cost_benefit":
                update_hazard = hazards[hazard_name]

        elif hazard_name in ["landslide", "flood"]:
            update_hazard = hazards[hazard_name]

        else:
            raise Exception(f"Hazard {hazard_name} is not supported yet ...")

        outputs[hazard_name] = {
            "exposure": exposure_obj,
            "impact": impacts[hazard_name],
            "updated_hazard": update_hazard,
            "hazard": hazards[hazard_name],
        }

    return outputs


def get_from_shp(
    shp_file: str, res: int = EXPOSURE_POINT_RES, crs_target: int or None = 4326
) -> Exposures:
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
        exp_obj,
        res=res,
        to_meters=True,
        disagg_met=u_lp.DisaggMethod.FIX,
        disagg_val=None,
    )

    """
    from shapely.geometry import LineString
    import geopandas as gpd
    ls = LineString( exp_obj.gdf[['longitude','latitude']].to_numpy() )
    line_gdf = gpd.GeoDataFrame( [['101']],crs='epsg:4326', geometry=[ls] )
    geometry = [Point(xy) for xy in zip(df.X, df.Y)]
    exp_obj_gdf = exp_obj.gdf
    exp_obj_gdf_geometry = exp_obj_gdf.geometry
    geo_df = gpd.GeoDataFrame(exp_obj_gdf, geometry=geometry)
    xx2 = exp_obj.gdf.groupby(["geometry_orig"])['geometry'].apply(lambda x: LineString(x.tolist()))
    """

    return exp_obj


def get_from_litpop(
    latlon: dict or None = None, country: str or list = RISK_COUNTRY
) -> Exposures:
    """Get Litpop data

    Returns:
        Exposures: Exposures based on LitPop
    """
    client = Client()

    if isinstance(country, str):
        litpop_obj = client.get_litpop(country=country)

    elif isinstance(country, list):
        all_exps = []
        # for proc_country in cfg["input"]["countries"]:
        for proc_country in country:
            all_exps.append(get_from_litpop(country=proc_country))
        litpop_obj = Exposures.concat(all_exps)

    if latlon is not None:
        gdf = litpop_obj.gdf
        filtered_gdf = gdf[
            (gdf["latitude"] >= latlon["lats"][0])
            & (gdf["latitude"] <= latlon["lats"][1])
            & (gdf["longitude"] >= latlon["lons"][0])
            & (gdf["longitude"] <= latlon["lons"][1])
        ]

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
            (gdf["latitude"] >= latlon["lats"][0])
            & (gdf["latitude"] <= latlon["lats"][1])
            & (gdf["longitude"] >= latlon["lons"][0])
            & (gdf["longitude"] <= latlon["lons"][1])
        ]

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
    exp_obj.gdf.rename(
        columns={"impf_": "impf_" + hazard_info["haz_type"]}, inplace=True
    )
    exp_obj.gdf["impf_" + hazard_info["haz_type"]] = hazard_info["haz_id"]

    return exp_obj
