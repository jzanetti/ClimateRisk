from climada.hazard import TCTracks, TropCyclone
from process.vis import plot_tc
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from process.utils import gdf2centroids, str2list_for_year
from climada.entity.exposures.base import Exposures
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

            # Load histrocial tropical cyclone tracks from ibtracs over the North Atlantic basin between 2010-2012
            ibtracks_na = TCTracks.from_ibtracs_netcdf(
                provider=TC_DATA["provider"], 
                year_range=str2list_for_year(TC_DATA["year_range"]), 
                estimate_missing=True)

            # Interpolation to make the track smooth and to allow applying calc_perturbed_trajectories
            ibtracks_na.equal_timestep(0.5)

            # Add randomly generated tracks using the calc_perturbed_trajectories method (1 per historical track)
            ibtracks_na.calc_perturbed_trajectories(
                nb_synth_tracks=TC_DATA["pert_tracks"])

            hazards[proc_hazard_name] = ibtracks_na

        elif proc_hazard_name == "landslide":

            hazards[proc_hazard_name] = get_landslide()

        elif proc_hazard_name == "flood":

            hazards[proc_hazard_name] = get_riverflood()

        else:
            raise Exception("fHazard type {proc_hazard_name} is not supported yet")

    return hazards


def get_tc(
    workdir: str, 
    exposure_obj: Exposures, 
    provider: str = "wellington", 
    year_range: None or list = None,
    vis_flag: bool = False) -> TCTracks_type:
    """Get TC from a certain provider

    Args:
        workdir (str): working directory
        exposure_obj (Exposures): exposures object
        year_range (None or list): e.g., [2000, 2001]
        provider (str, optional): TC center. Defaults to "wellington".
        vis_flag (bool, optional): if create visualization. Defaults to False

    Returns:
        _type_: _description_
    """

    # Load histrocial tropical cyclone tracks from ibtracs over the North Atlantic basin between 2010-2012
    ibtracks_na = TCTracks.from_ibtracs_netcdf(provider=provider, year_range=year_range, estimate_missing=True)

    # Interpolation to make the track smooth and to allow applying calc_perturbed_trajectories
    ibtracks_na.equal_timestep(0.5)

    # Add randomly generated tracks using the calc_perturbed_trajectories method (1 per historical track)
    ibtracks_na.calc_perturbed_trajectories(nb_synth_tracks=1)

    # plot TC
    if vis_flag:
        plot_tc(workdir, ibtracks_na)

    # Define the centroids from the exposures position
    exp_centroids = gdf2centroids(exposure_obj["exposure_obj"].gdf)

    # Using the tracks, compute the windspeed at the location of the centroids
    tc = TropCyclone.from_tracks(ibtracks_na, centroids=exp_centroids)

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

    landslide = Landslide.from_hist(bbox=domain, input_gdf=tmp_file, res=res)

    remove(tmp_file)

    return landslide


def get_riverflood():
    """Get river flood

    Returns:
        _type_: _description_
    """
    return pickle_load(open(FLOOD_DATA, "rb"))



    

    