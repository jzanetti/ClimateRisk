from climada.hazard import TCTracks
from process.vis import plot_tc
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from process.utils import str2list_for_year, create_climada_petal_year_range
from os import remove
from process import LANDSLIDE_DATA, TC_DATA, FLOOD_DATA, RISK_COUNTRY, FUTURE_YEARS
from geopandas import read_file
from process.climada_petals.landslide import Landslide
from pickle import load as pickle_load
from climada.util.api_client import Client
from process import RCP_ADJUSTMENT
from climada.hazard import Hazard
from numpy import ones as numpy_ones

def get_hazard(
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
            
            hazards[proc_hazard_name] = get_tc(get_tc_type(task_type), proc_hazard_cfg["cfg"])

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

    def _create_tc_cfg(climate_scenario: str, years: str) -> dict:
        """Create TC configuration

        Args:
            climate_scenario (str): climate scenario, 
                e.g., rcp26, rcp45, rcp60 or historical
            years (str): years to be processed, e.g.,
                - for historical data: set a range such as "1980_2020"
                - for projection data, set a number within the range (2040, 2060 and 2080)

        Returns:
            dict: TC configuration
        """
        properties = {
            "climate_scenario": climate_scenario,
            "nb_synth_tracks": nb_synth_tracks
        }

        if climate_scenario != "historical":
            properties["ref_year"] = str(years)
        
        return properties

    client = Client()

    if tc_type == "track":

        hazard_hist = Hazard.concat(
            [client.get_hazard(
                dataset_name,
                properties={
                    "country_name": country,
                    "climate_scenario": tc_data_cfg["climate_scenario"],
                    "nb_synth_tracks": nb_synth_tracks}) for country in tc_data_cfg["country_name"]])

    elif tc_type == "wind":

        properties = _create_tc_cfg(
            tc_data_cfg["climate_scenario"],
            tc_data_cfg["years"]
        )

        hazards = []
        for proc_country in tc_data_cfg["country_name"]:
            properties["country_name"] = proc_country
            hazards.append(
                client.get_hazard(
                    dataset_name,
                    properties=properties)
            )
    
        hazard_hist = Hazard.concat(hazards)

        if tc_data_cfg["climate_scenario"] == "historical":
            hazard_hist = hazard_hist.select(
                date=create_climada_petal_year_range(tc_data_cfg["years"]))
        else:
            hazard_hist.intensity *= RCP_ADJUSTMENT["tc_wind"][tc_data_cfg["climate_scenario"]]
    
    if tc_data_cfg["use_total"]:

        if tc_data_cfg["climate_scenario"] != "historical":
            raise Exception("use_total cannot be applied to climate scenario other than historical")

        hazard_hist.frequency = numpy_ones(len(hazard_hist.frequency))

    return hazard_hist


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



    

    