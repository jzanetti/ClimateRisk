
import matplotlib.pyplot as plt
from numpy import ones, stack, ndarray, array, concatenate
from climada.util.plot import _get_collection_arrays
from climada.util.plot import make_map
from climada.util.files_handler import to_list
from climada.util.plot import _get_borders, add_populated_places
from climada.util.plot import add_shapes
import cartopy.crs as ccrs
import climada.util.coordinates as u_coord
from mpl_toolkits.axes_grid1 import make_axes_locatable
from textwrap import wrap


from matplotlib.pyplot import savefig, close
from os.path import join
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from climada.engine.impact import Impact as Impact_type
import matplotlib.pyplot as plt
from process.utils import read_basemap, get_exposure_range



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


def plot_scattered_data(impact_obj, title, cmap: str = "jet",
                        pop_name=False, buffer=1.0, extend='neither',
                        shapes=True, axes=None, ignore_zero: bool = False,
                        figsize=(9, 13), adapt_fontsize=True, **kwargs):
    """Plot scatter data

    Args:
        impact_obj (_type_): _description_
        title (_type_): _description_
        cmap (str, optional): _description_. Defaults to "jet".
        pop_name (bool, optional): _description_. Defaults to False.
        buffer (float, optional): _description_. Defaults to 1.0.
        extend (str, optional): _description_. Defaults to 'neither'.
        shapes (bool, optional): _description_. Defaults to True.
        axes (_type_, optional): _description_. Defaults to None.
        ignore_zero (bool, optional): _description_. Defaults to False.
        figsize (tuple, optional): _description_. Defaults to (9, 13).
        adapt_fontsize (bool, optional): _description_. Defaults to True.

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    eai_exp = impact_obj._build_exp()

    proj=ccrs.PlateCarree()

    mask = ones((eai_exp.gdf.shape[0],), dtype=bool)

    cbar_label = 'Value (%s)' % eai_exp.value_unit

    if ignore_zero:
        pos_vals = eai_exp.gdf.value[mask].values > 0
    else:
        pos_vals = ones((eai_exp.gdf.value[mask].values.size,), dtype=bool)

    array_sub = eai_exp.gdf.value[mask][pos_vals].values

    geo_coord = stack(
        [
            eai_exp.gdf.latitude[mask][pos_vals].values,
            eai_exp.gdf.longitude[mask][pos_vals].values
        ], axis=1)

    # Generate array of values used in each subplot
    num_im, list_arr = _get_collection_arrays(array_sub)
    list_tit = to_list(num_im, title, 'title')
    list_name = to_list(num_im, cbar_label, 'var_name')
    list_coord = to_list(num_im, geo_coord, 'geo_coord')

    kwargs['cmap'] = cmap

    if axes is None:
        proj_plot = proj
        if isinstance(proj, ccrs.PlateCarree):
            # use different projections for plot and data to shift the central lon in the plot
            xmin, xmax = u_coord.lon_bounds(concatenate([c[:, 1] for c in list_coord]))
            proj_plot = ccrs.PlateCarree(central_longitude=0.5 * (xmin + xmax))
        _, axes, fontsize = make_map(num_im, proj=proj_plot, figsize=figsize,
                                     adapt_fontsize=adapt_fontsize)
    else:
        fontsize = None
    axes_iter = axes
    if not isinstance(axes, ndarray):
        axes_iter = array([[axes]])

    # Generate each subplot
    for array_im, axis, tit, name, coord in \
    zip(list_arr, axes_iter.flatten(), list_tit, list_name, list_coord):
        if coord.shape[0] != array_im.size:
            raise ValueError("Size mismatch in input array: %s != %s." %
                             (coord.shape[0], array_im.size))

        # Binned image with coastlines
        if isinstance(proj, ccrs.PlateCarree):
            xmin, ymin, xmax, ymax = u_coord.latlon_bounds(coord[:, 0], coord[:, 1], buffer=buffer)
            extent = (xmin, xmax, ymin, ymax)
        else:
            extent = _get_borders(coord, buffer=buffer, proj_limits=proj.x_limits + proj.y_limits)
        axis.set_extent((extent), proj)

        if shapes:
            add_shapes(axis)
        if pop_name:
            add_populated_places(axis, extent, proj, fontsize)

        mappable = axis.scatter(coord[:, 1], coord[:, 0], c=array_im,
                                    transform=proj, **kwargs)

        # Create colorbar in this axis
        cbax = make_axes_locatable(axis).append_axes(
            'right', size="3.0%", pad=-0.7, axes_class=plt.Axes)
        cbar = plt.colorbar(mappable, cax=cbax, orientation='vertical', extend=extend)
        cbar.set_label(name)
        axis.set_title("\n".join(wrap(tit)))
        if fontsize:
            cbar.ax.tick_params(labelsize=fontsize)
            cbar.ax.yaxis.get_offset_text().set_fontsize(fontsize)
            for item in [axis.title, cbar.ax.xaxis.label, cbar.ax.yaxis.label]:
                item.set_fontsize(fontsize)
    plt.tight_layout()

    return axes
