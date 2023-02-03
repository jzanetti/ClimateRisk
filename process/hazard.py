
from os import remove
from os.path import exists, join
from pickle import dump as pickle_dump
from pickle import load as pickle_load

from climada.hazard import Hazard
from climada.util.api_client import Client
from geopandas import read_file
from numpy import ones as numpy_ones

from process import FLOOD_DATA, HAZARD_CHCHE_DIR, LANDSLIDE_DATA, RISK_COUNTRY
from process.climada_petals.landslide import Landslide
from process.pred import tc_pred
from process.utils import create_climada_petal_year_range


def get_hazard(
    job_name: str,
    hazard_cfg: dict,
    task_type: str = "impact") -> dict:
    """Get hazard for climaterisk

    Args:
        hazard_cfg (dict): Hazard configuration
        task_type (str): task type, e.g., impact etc.

    Raises:
        Exception: hazard is not supported

    Returns:
        dict: Hazard information
    """

    hazards = {}

    for proc_hazard_name in hazard_cfg:

        proc_hazard_cfg = hazard_cfg[proc_hazard_name]

        if not proc_hazard_cfg["enable"]:
            continue

        if proc_hazard_name == "TC":
            
            hazards[proc_hazard_name] = get_tc(job_name, get_tc_type(task_type), proc_hazard_cfg["cfg"])

        elif proc_hazard_name == "landslide":

            hazards[proc_hazard_name] = get_landslide()

        elif proc_hazard_name == "flood":

            hazards[proc_hazard_name] = get_riverflood()

        else:
            raise Exception(f"Hazard type {proc_hazard_name} is not supported yet")

    return hazards


def get_tc_type(task_type: str) -> str:
    """Get TC type based on task

    Args:
        task_type (str): task name, e.g., impact

    Returns:
        str: tc type, e.g., wind and track
    """
    if task_type in ["impact", "cost_benefit"]:
        tc_type = "wind"
    elif task_type == "supplychain":
        tc_type = "track"
    
    return tc_type


def get_tc(
    job_name: str,
    tc_type: str,
    tc_data_cfg: dict, 
    dataset_name: str = "tropical_cyclone",
    nb_synth_tracks: str = "10") -> dict:
    """Get TC from ClimateRisk Petal client
    
    Args:
        tc_type (str): whether it's wind or track
        tc_data_cfg (dict): data configuration, e.g.,
            {
                climate_scenario: historical
                country_name:
                    - New Zealand
                years: 1980_2020
            }

    Returns:
        dict: the dict contains TC winds or tracks
    """

    client = Client()

    if tc_type == "track":

        hazard_all = Hazard.concat(
            [client.get_hazard(
                dataset_name,
                properties={
                    "country_name": country,
                    "climate_scenario": tc_data_cfg["climate_scenario"],
                    "nb_synth_tracks": nb_synth_tracks}) for country in tc_data_cfg["country_name"]])

    elif tc_type == "wind":

        climate_scenario = tc_data_cfg["climate_scenario"]

        hazard_file = join(HAZARD_CHCHE_DIR, f"{tc_type}_{job_name}_{climate_scenario}.p")

        if not exists(hazard_file):

            print(f"not able to find {hazard_file}, creating a new hazard type")

            hazards = []
            for proc_country in tc_data_cfg["country_name"]:
                hazards.append(
                    client.get_hazard(
                        dataset_name,
                        properties={
                            "country_name": proc_country,
                            "climate_scenario": "historical",
                            "nb_synth_tracks": nb_synth_tracks
                        })
                )

            hazard_all = Hazard.concat(hazards)

            if climate_scenario != "historical":
                hazard_pred = tc_pred(hazard_all, range(2021, 2081), climate_scenario)
                hazard_all = Hazard.concat([hazard_all] + hazard_pred)

            pickle_dump({"hazard": hazard_all}, open(hazard_file, "wb"))

        hazard_all = pickle_load(open(hazard_file, "rb"))["hazard"]

        hazard_all = hazard_all.select(
            date=create_climada_petal_year_range(tc_data_cfg["years"]))

    
    if tc_data_cfg["use_total"]:
        hazard_all.frequency = numpy_ones(len(hazard_all.frequency))

    return hazard_all


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



    

    