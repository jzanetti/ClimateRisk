from climada.hazard import TCTracks
from process.vis import plot_tc
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from process.utils import str2list_for_year
from os import remove
from process import LANDSLIDE_DATA, TC_DATA, FLOOD_DATA
from geopandas import read_file
from process.climada_petals.landslide import Landslide
from pickle import load as pickle_load


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

        if proc_hazard_name == "TC":

            hazards[proc_hazard_name] = get_tc()

        elif proc_hazard_name == "landslide":

            hazards[proc_hazard_name] = get_landslide()

        elif proc_hazard_name == "flood":

            hazards[proc_hazard_name] = get_riverflood()

        else:
            raise Exception("fHazard type {proc_hazard_name} is not supported yet")

    return hazards


def get_tc(smooth_factor: float = 0.5) -> TCTracks_type:
    """Get TC from a certain provider

    Returns:
        _type_: _description_
    """

    # Load histrocial tropical cyclone tracks from ibtracs over the North Atlantic basin between 2010-2012
    tc = TCTracks.from_ibtracs_netcdf(
        provider=TC_DATA["provider"], 
        year_range=str2list_for_year(TC_DATA["year_range"]), 
        estimate_missing=True)

    # Interpolation to make the track smooth and to allow applying calc_perturbed_trajectories
    tc.equal_timestep(smooth_factor)

    # Add randomly generated tracks using the calc_perturbed_trajectories method (1 per historical track)
    tc.calc_perturbed_trajectories(
        nb_synth_tracks=TC_DATA["pert_tracks"])

    return tc


def get_landslide(
    tmp_file: str = "/tmp/ls.shp", 
    domain: tuple = (160.0, -50.0, 180.0, -30.0), 
    res: float = 0.01) -> Landslide:
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

    return landslide


def get_riverflood():
    """Get river flood

    Returns:
        _type_: _description_
    """
    return pickle_load(open(FLOOD_DATA, "rb"))



    

    