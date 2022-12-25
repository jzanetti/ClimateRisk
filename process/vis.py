from matplotlib.pyplot import savefig, close
from climada.entity.exposures.base import Exposures
from os.path import join
# from process import DOMAIN
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from climada.engine.impact import Impact as Impact_type
import climada.util.lines_polys_handler as u_lp
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
from process.utils import read_basemap

def plot_wrapper(cfg: dict, workdir: str, exp_objs: dict):


    print("Read basemap for visualization ...")
    basemap = read_basemap(cfg["vis"]["basemap"])

    for proc_vis_name in cfg["vis"]:

        if proc_vis_name == "basemap":
            continue
        
        if not cfg["vis"][proc_vis_name]["enable"]:
            continue

        if proc_vis_name == "impact":
            for hazard_name in exp_objs:
                plot_impact(workdir, hazard_name, basemap, exp_objs[hazard_name]["imp"], exp_objs[hazard_name]["freq"])


def plot_exposure(workdir: str, exposure_obj: Exposures, basemap: GeoDataFrame or None):
    """Plot exposure

    Args:
        workdir (str): Working directory
        litpop_obj (Exposures): Exposures map
    """
    base = None
    if basemap is not None:
        base = basemap.plot(color='white', edgecolor='black')

    ax = exposure_obj.gdf.plot(ax=base, colormap="jet", column=exposure_obj.gdf.value, figsize=(20, 25), markersize=3, legend=True)

    ax.tick_params(axis='x', which='both', labelsize=7.5)
    ax.tick_params(axis='y', which='both', labelsize=7.5)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Exposure")

    savefig(
        join(workdir, "exposure.png"),
        bbox_inches='tight',
        dpi=200)
    close()


def plot_tc(workdir: str, tc_obj: TCTracks_type) -> Impact_type:
    """Plot LitPop

    Args:
        workdir (str): Working directory
        tc_obj (TCTracks_type): TC object
    """
    tc_obj.plot(figsize=(16, 12), adapt_fontsize=False)
    savefig(
        join(workdir, "tc.png"),
        bbox_inches='tight',
        dpi=200)
    close()


def plot_impact(workdir: str, hazard_name: str, basemap, impact_obj: Impact_type, freq_curve_obj, buffer: float = 0.1):
    """Plot LitPop

    Args:
        workdir (str): Working directory
        impact_obj (Impact_type): impact object
    """
    
    basemap.plot(color='white', edgecolor='black')
    impact_obj.plot_scatter_eai_exposure(figsize=(16, 12), adapt_fontsize=False, buffer=buffer)
    savefig(
        join(workdir, f"impact_{hazard_name}.png"),
        bbox_inches='tight',
        dpi=200)
    close()

    freq_curve_obj.plot()
    savefig(
        join(workdir, f"impact_frequemcy_{hazard_name}.png"),
        bbox_inches='tight',
        dpi=200)
    close()