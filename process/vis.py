from matplotlib.pyplot import savefig, close
from climada.entity.exposures.base import Exposures
from os.path import join
from cartopy.crs import PlateCarree
from climada.engine.impact import Impact as Impact_type
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
from process.utils import read_basemap, get_exposure_range
from process.climada.plot import plot_tc, plot_scattered_data, plot_landslide
from climada.engine.cost_benefit import risk_aai_agg
from numpy import array

def plot_cost_benefit_wrapper(cfg: dict, workdir: str, exp_objs: dict, cost_benefit_objs: dict, discount_rates: dict):

    # costben.plot_waterfall(exp_objs["hist"][hazard_name]["hazard"], adaptation_measure_objs["hist"], exp_objs["future"][hazard_name]["hazard"], adaptation_measure_objs["future"],
    #                           risk_func=risk_aai_agg)

    for hazard_type in cost_benefit_objs["cost_benefit"]:

        # plot event view
        f = plt.figure(figsize=(10, 7))
        ax = f.add_subplot()
        cost_benefit_objs["cost_benefit"][hazard_type].plot_event_view((10, 25, 50, 100), axis=ax)
        ax.set_title("Impact for different adaptation measures")

        colors = {}
        for measure_method in cfg["adaptation"][hazard_type]:
            colors[measure_method] = eval(cfg["adaptation"][hazard_type][measure_method]["color_rgb"])
            labels = list(colors.keys())
            handles = [plt.Rectangle((0,0), 1, 1, color=colors[label]) for label in labels]
            plt.legend(handles, labels)

        savefig(
            join(workdir, f"impact_for_different_adaptations_{hazard_type}.png"),
            bbox_inches="tight")
        close()

        # plot waterfall view
        f = plt.figure(figsize=(10, 7))
        ax = f.add_subplot()
        cost_benefit_objs["cost_benefit"][hazard_type].plot_waterfall(
            exp_objs["hist"][hazard_type]["hazard"], 
            cost_benefit_objs["adaptation_measures"][hazard_type]["hist"], 
            exp_objs["future"][hazard_type]["hazard"], 
            cost_benefit_objs["adaptation_measures"][hazard_type]["future"],
            risk_func=risk_aai_agg,
            axis=ax)
        savefig(
            join(workdir, f"risk_{hazard_type}.png"),
            bbox_inches="tight")
        close()

        # plot cost-benefit
        f = plt.figure(figsize=(10, 7))
        ax = f.add_subplot()
        ax = cost_benefit_objs["cost_benefit"][hazard_type].plot_cost_benefit()
        savefig(
            join(workdir, f"cost_benefit_{hazard_type}.png"),
            bbox_inches="tight")
        close()

        # plot EFC
        efc_present = cost_benefit_objs["cost_benefit"][hazard_type].imp_meas_present['no measure']['efc']
        efc_future = cost_benefit_objs["cost_benefit"][hazard_type].imp_meas_future['no measure']['efc']
        efc_combined_measures = cost_benefit_objs["cost_benefit"][hazard_type].combine_measures(
            list(cfg["adaptation"][hazard_type].keys()),
            "Combine measure",
            new_color = array([0.1, 0.8, 0.9]),
            disc_rates = discount_rates[hazard_type]
        ).imp_meas_future['Combine measure']['efc']

        ax = plt.subplot(1, 1, 1)
        efc_present.plot(axis=ax, color='blue', label='Present')
        efc_future.plot(axis=ax, color='orange', label='Future, unadapted')
        efc_combined_measures.plot(axis=ax, color='green', label='Future, adapted')
        ax.legend()

        plt.xlim([0, 100])
        index = efc_future.return_per.tolist().index(
            min(efc_future.return_per, key=lambda x:abs(x - 100.0))) # return year 100
        plt.ylim([0, efc_future.impact[index] * 1.3])
        savefig(
            join(workdir, f"efc_{hazard_type}.png"),
            bbox_inches="tight")
        close()

def plot_impact_wrapper(cfg: dict, workdir: str, exp_objs: dict, add_basemap: bool = False):
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


        if proc_vis_name == "exposure":
            for proc_exp in exp_objs:
                plot_exposure(workdir, exp_objs[proc_exp]["exposure"], basemap)

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
                if hazard_name == "landslide":
                    print("plotting landslide ...")
                    plot_landslide(workdir, exp_objs[hazard_name]["hazard"], basemap)
                if hazard_name == "flood":
                    print("plotting flood (this may take very long to complete) ...")
                    exp_objs[hazard_name]["hazard"].plot_intensity(event=0)
                    plt.savefig(join(workdir, "flood.png"))
                    plt.close()
    

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
    #ax.set_xlim(174.7, 174.9)
    #ax.set_ylim(-41.35, -41.25)

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

    ax = plot_scattered_data(
        impact_obj, 
        f"Expected annual impact from {hazard_name}", 
        axes=ax,
        vmin=vrange["min"],
        vmax=vrange["max"],
        ignore_zero=False)

    # ax.set_xlim(174.7, 174.9)
    # ax.set_ylim(-41.35, -41.25)

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