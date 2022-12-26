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


def plot_tc(workdir: str, tc_obj: TCTracks_type) -> Impact_type:
    """Plot LitPop

    Args:
        workdir (str): Working directory
        tc_obj (TCTracks_type): TC object
    """
    # tc_obj.plot(figsize=(16, 12), adapt_fontsize=False)
    #savefig(
    #    join(workdir, "tc.png"),
    #    bbox_inches='tight',
    #    dpi=200)
    #close()

    import cartopy.crs as ccrs
    import climada.util.plot as u_plot
    import matplotlib.cm as cm_mp
    import numpy as np
    from matplotlib.colors import BoundaryNorm, ListedColormap
    import climada.util.coordinates as u_coord
    from matplotlib.collections import LineCollection
    from matplotlib.lines import Line2D
    CAT_NAMES = {
        -1: 'Tropical Depression',
        0: 'Tropical Storm',
        1: 'Hurricane Cat. 1',
        2: 'Hurricane Cat. 2',
        3: 'Hurricane Cat. 3',
        4: 'Hurricane Cat. 4',
        5: 'Hurricane Cat. 5',
    }

    legend = True
    SAFFIR_SIM_CAT = [34, 64, 83, 96, 113, 137, 1000]

    CAT_COLORS = cm_mp.rainbow(np.linspace(0, 1, len(SAFFIR_SIM_CAT)))
    extent = (160.0, 180.0, -50.0, -30.0)
    mid_lon = 0.5 * (extent[1] + extent[0])

    kwargs = {}
    kwargs['transform'] = ccrs.PlateCarree()
    figsize = figsize=(16, 12)
    adapt_fontsize = True
    axis = None

    if not axis:
        proj = ccrs.PlateCarree(central_longitude=mid_lon)
        _, axis, _ = u_plot.make_map(proj=proj, figsize=figsize, adapt_fontsize=adapt_fontsize)
    axis.set_extent(extent, crs=kwargs['transform'])
    u_plot.add_shapes(axis)

    synth_flag = False
    cmap = ListedColormap(colors=CAT_COLORS)
    norm = BoundaryNorm([0] + SAFFIR_SIM_CAT, len(SAFFIR_SIM_CAT))
    for track in tc_obj.data:
        lonlat = np.stack([track.lon.values, track.lat.values], axis=-1)
        lonlat[:, 0] = u_coord.lon_normalize(lonlat[:, 0], center=mid_lon)
        segments = np.stack([lonlat[:-1], lonlat[1:]], axis=1)
        # remove segments which cross 180 degree longitude boundary
        segments = segments[segments[:, 0, 0] * segments[:, 1, 0] >= 0, :, :]
        if track.orig_event_flag:
            track_lc = LineCollection(segments, cmap=cmap, norm=norm,
                                        linestyle='solid', **kwargs)
        else:
            synth_flag = True
            track_lc = LineCollection(segments, cmap=cmap, norm=norm,
                                        linestyle=':', **kwargs)
        track_lc.set_array(track.max_sustained_wind.values)
        axis.add_collection(track_lc)

    if legend:
        leg_lines = [Line2D([0], [0], color=CAT_COLORS[i_col], lw=2)
                        for i_col in range(len(SAFFIR_SIM_CAT))]
        leg_names = [CAT_NAMES[i_col] for i_col in sorted(CAT_NAMES.keys())]
        if synth_flag:
            leg_lines.append(Line2D([0], [0], color='grey', lw=2, ls='solid'))
            leg_lines.append(Line2D([0], [0], color='grey', lw=2, ls=':'))
            leg_names.append('Historical')
            leg_names.append('Synthetic')
        axis.legend(leg_lines, leg_names, loc=0)
    plt.tight_layout()
    savefig(
        join(workdir, "tc.png"),
        bbox_inches='tight',
        dpi=200)
    close()


def plot_impact(workdir: str, hazard_name: str, basemap, baseexp, impact_obj: Impact_type, freq_curve_obj, buffer: float = 0.1):
    """Plot LitPop

    Args:
        workdir (str): Working directory
        impact_obj (Impact_type): impact object
    """
    
    basemap.plot(color='white', edgecolor='black')
    baseexp.plot(color="k")

    impact_obj.plot_scatter_eai_exposure(
        figsize=(16, 12), 
        adapt_fontsize=False, 
        buffer=buffer, 
        ignore_zero=True, 
        edgecolors="k")

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