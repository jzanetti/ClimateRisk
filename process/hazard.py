from climada.hazard import TCTracks
from process.vis import plot_tc
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from process.utils import str2list_for_year
from os import remove
from process import LANDSLIDE_DATA, TC_DATA, FLOOD_DATA, RISK_COUNTRY, FUTURE_YEARS
from geopandas import read_file
from process.climada_petals.landslide import Landslide
from pickle import load as pickle_load
from climada.util.api_client import Client

def get_hazard(hazard_cfg: dict) -> dict:
    """Get hazard

    Args:
        hazard_cfg (dict): Hazard configuration

    Raises:
        Exception: _description_

    Returns:
        dict: Hazard information
    """

    hazards = {}

    for proc_hazard_name in hazard_cfg:

        proc_hazard_cfg = hazard_cfg[proc_hazard_name]

        if not proc_hazard_cfg["enable"]:
            continue

        if proc_hazard_name == "TC_track":

            hazards[proc_hazard_name] = get_tc(tc_type="track")

        elif proc_hazard_name == "TC_wind":

            hazards[proc_hazard_name] = get_tc(tc_type="wind")

        elif proc_hazard_name == "landslide":

            hazards[proc_hazard_name] = get_landslide()

        elif proc_hazard_name == "flood":

            hazards[proc_hazard_name] = get_riverflood()

        else:
            raise Exception("fHazard type {proc_hazard_name} is not supported yet")

    return hazards


def get_tc(tc_type: str, smooth_factor: float = 0.5) -> dict:
    """Get TC from a certain provider

    Returns:
        _type_: _description_
    """

    if tc_type == "track":

        hazard_hist = TCTracks.from_ibtracs_netcdf(
            provider=TC_DATA["track"]["provider"], 
            year_range=str2list_for_year(TC_DATA["track"]["year_range"]), 
            estimate_missing=True)

        hazard_hist.equal_timestep(smooth_factor)

        hazard_hist.calc_perturbed_trajectories(
            nb_synth_tracks=TC_DATA["track"]["pert_tracks"])

        hazard_future = None

    elif tc_type == "wind":

        client = Client()

        hazard_hist = client.get_hazard(
            "tropical_cyclone",
            properties={
                "country_name": RISK_COUNTRY,
                "climate_scenario": "historical",
                "nb_synth_tracks": str(TC_DATA["wind"]["pert_tracks"])
            }
        )
        hazard_future = client.get_hazard(
            "tropical_cyclone",
            properties={
                "country_name": RISK_COUNTRY,
                "climate_scenario": "rcp85",
                "ref_year": str(FUTURE_YEARS),
                "nb_synth_tracks": str(TC_DATA["wind"]["pert_tracks"])})

    return {"hist": hazard_hist, "future": hazard_future}


def get_landslide(
    tmp_file: str = "/tmp/ls.shp", 
    domain: tuple = (160.0, -50.0, 180.0, -30.0), 
    res: float = 0.01) -> dict:
    """Get landslide

    Args:
        tmp_file (str, optional): tmp file to be written. Defaults to "/tmp/ls.shp".
        domain (tuple, optional): domain to be used. Defaults to (160.0, -50.0, 180.0, -30.0).

    Raises:
        Exception: _description_
    """

    landslide_gdf_all = read_file(LANDSLIDE_DATA)

    landslide_gdf_all.to_file(tmp_file)

    #from datetime import datetime
    #x = landslide_gdf_all["ev_date"].to_list()
    #x = list(filter(None, x))
    #[datetime.strptime(xx, "%Y-%m-%d") for xx in x]

    landslide = Landslide.from_hist(bbox=domain, input_gdf=tmp_file, res=res)

    remove(tmp_file)

    return {"hist": landslide, "future": None}


def get_riverflood() -> dict:
    """Get river flood

    Returns:
        _type_: _description_
    """
    flood_data = pickle_load(open(FLOOD_DATA, "rb"))


    return {"hist": flood_data, "future": None}



    

    