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
from process import INVALID_KEY
from climada.hazard import Hazard

def get_hazard(hazard_cfg: dict, future_hazard_para: dict or None or str = INVALID_KEY, task_type: str = "impact", tc_data_cfg: dict = TC_DATA) -> dict:
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

        if proc_hazard_name == "TC":
            
            if task_type == "impact":
                hazards[proc_hazard_name] = get_tc(tc_type="track", future_hazard_para=future_hazard_para, tc_data_cfg=tc_data_cfg)
            elif task_type == "cost_benefit":
                hazards[proc_hazard_name] = get_tc(tc_type="wind", future_hazard_para=future_hazard_para, tc_data_cfg=tc_data_cfg)
            elif task_type == "supplychain":
                hazards[proc_hazard_name] = get_tc(tc_type="track2", future_hazard_para=future_hazard_para, tc_data_cfg=tc_data_cfg)

        elif proc_hazard_name == "landslide":

            hazards[proc_hazard_name] = get_landslide()

        elif proc_hazard_name == "flood":

            hazards[proc_hazard_name] = get_riverflood()

        else:
            raise Exception(f"Hazard type {proc_hazard_name} is not supported yet")

    return hazards


def get_tc(tc_type: str, future_hazard_para: dict or None = None, smooth_factor: float = 0.5, tc_data_cfg: dict = TC_DATA) -> dict:
    """Get TC from a certain provider

    Returns:
        _type_: _description_
    """

    if tc_type == "track":

        hazard_hist = TCTracks.from_ibtracs_netcdf(
            provider=tc_data_cfg["track"]["provider"], 
            year_range=str2list_for_year(tc_data_cfg["track"]["year_range"]), 
            estimate_missing=True)

        hazard_hist.equal_timestep(smooth_factor)

        hazard_hist.calc_perturbed_trajectories(
            nb_synth_tracks=tc_data_cfg["track"]["pert_tracks"])

        hazard_future = None

    elif tc_type == "track2":

        client = Client()

        hazard_hist = Hazard.concat(
            [client.get_hazard(
                "tropical_cyclone",
                properties={
                    "country_name": country,
                    "climate_scenario": "historical",
                    "nb_synth_tracks": "10"}) for country in tc_data_cfg["countries"]])

        hazard_future = None

    elif tc_type == "wind":

        client = Client()

        hazard_hist = client.get_hazard(
            "tropical_cyclone",
            properties={
                "country_name": RISK_COUNTRY,
                "climate_scenario": "historical",
                "nb_synth_tracks": str(tc_data_cfg["wind"]["pert_tracks"])
            }
        )

        if future_hazard_para is INVALID_KEY:
            hazard_future = None
        else:
            hazard_future = client.get_hazard(
                "tropical_cyclone",
                properties={
                    "country_name": RISK_COUNTRY,
                    "climate_scenario": "rcp45",
                    "ref_year": str(FUTURE_YEARS),
                    "nb_synth_tracks": str(TC_DATA["wind"]["pert_tracks"])})
            if future_hazard_para is not None:
                hazard_future.intensity = hazard_hist.intensity * (1.0 + future_hazard_para)

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



    

    