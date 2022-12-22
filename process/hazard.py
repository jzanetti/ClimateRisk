from climada.hazard import TCTracks, TropCyclone, Centroids
from process.vis import plot_tc
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from process.utils import gdf2centroids
from climada.entity.exposures.base import Exposures

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
    exp_centroids = gdf2centroids(exposure_obj.gdf)

    # Using the tracks, compute the windspeed at the location of the centroids
    tc = TropCyclone.from_tracks(ibtracks_na, centroids=exp_centroids)

    return tc