from matplotlib.pyplot import savefig, close
from climada.entity.exposures.base import Exposures
from os.path import join
from cartopy.crs import PlateCarree
from climada.engine.impact import Impact as Impact_type
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
from process.utils import read_basemap, get_exposure_range
from process.climada.plot import plot_tc, plot_scattered_data


def plot_wrapper(cfg: dict, workdir: str, exp_objs: dict, add_basemap: bool = False):
    """Plot wrapper

    Args:
        cfg (dict): _description_
        workdir (str): _description_
        exp_objs (dict): _description_
    """
    print("Read basemap for visualization ...")

    basemap = None
    if add_basemap:
        basemap = read_basemap(cfg["vis"]["basemap"])

    baseexp = read_basemap(cfg["input"]["file"])

    for proc_vis_name in cfg["vis"]:

        if proc_vis_name == "basemap":
            continue
        
        if not cfg["vis"][proc_vis_name]["enable"]:
            continue

        if proc_vis_name == "impact":
            for hazard_name in exp_objs:
                plot_impact(
                    workdir, 
                    hazard_name, 
                    basemap,
                    baseexp,
                    exp_objs[hazard_name]["imp"], 
                    exp_objs[hazard_name]["freq"])

        if proc_vis_name == "hazard":
            for hazard_name in exp_objs:
                if hazard_name == "TC":
                    print("plotting TC ...")
                    plot_tc(workdir, exp_objs[hazard_name]["hazard"])


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


def plot_impact(
    workdir: str, 
    hazard_name: str, 
    basemap, 
    baseexp, 
    impact_obj: Impact_type, 
    freq_curve_obj):
    """Plot LitPop

    Args:
        workdir (str): Working directory
        impact_obj (Impact_type): impact object
    """

    f = plt.figure(figsize=(8, 15))
    ax = f.add_subplot(projection=PlateCarree())
    baseexp.to_crs(4326).plot(
        ax=ax, color="k", edgecolor='black')
    
    if basemap is not None:
        basemap.plot(ax=ax, color='white', edgecolor='black')

    vrange = get_exposure_range(impact_obj._build_exp().gdf)

    plot_scattered_data(
        impact_obj, 
        f"Expected annual impact from {hazard_name}", 
        axes=ax,
        vmin=vrange["min"],
        vmax=vrange["max"],
        ignore_zero=True)

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