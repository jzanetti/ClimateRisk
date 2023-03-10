
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
from numpy import max as numpy_max
from numpy import mean as numpy_mean

from matplotlib.pyplot import savefig, close
from os.path import join
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from climada.engine.impact import Impact as Impact_type
import matplotlib.pyplot as plt
from climada.entity.exposures.base import Exposures
from geopandas import GeoDataFrame
import cartopy.crs as ccrs
import climada.util.plot as u_plot
import matplotlib.cm as cm_mp
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
import climada.util.coordinates as u_coord
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.pyplot import title
from scipy.interpolate import griddata


def plot_tc(workdir: str, tc_obj: TCTracks_type, only_nz: bool = True) -> Impact_type:
    """Plot LitPop

    Args:
        workdir (str): Working directory
        tc_obj (TCTracks_type): TC object
    """
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

    if only_nz:
        extent = (160.0, 180.0, -50.0, -30.0)
    else:
        extent = tc_obj.get_extent(deg_buffer=1)

    mid_lon = 0.5 * (extent[1] + extent[0])

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
            continue
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

        if "extent" in kwargs:
            extent = kwargs["extent"]
            del kwargs["extent"]
        
        if extent is None:
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



def plot_landslide(workdir: str, landslide_obj: Exposures, basemap: GeoDataFrame or None):
    """Plot landslide

    Args:
        workdir (str): _description_
        landslide_obj (Exposures): _description_
        basemap (GeoDataFrameorNone): _description_
    """
    base_ax = None
    if basemap is not None:
        base_ax = basemap.plot(color='white', edgecolor='black', figsize=(15, 10))

    landslide_obj._set_coords_centroids()
    landslide_coord = landslide_obj.centroids.coord
    landslide_value = landslide_obj.intensity.toarray()
    landslide_value = numpy_mean(landslide_value, 0)
    # landslide_date = landslide_obj.date.values

    data_len = len(landslide_value)

    lats = []
    lons = []
    values = []
    for i in range(data_len):
        proc_value = landslide_value[i]
        if proc_value > 0.0:
            lats.append(landslide_coord[i][0])
            lons.append(landslide_coord[i][1])
            values.append(proc_value)
    
    base_ax.scatter(lons, lats, cmap="jet", edgecolors="k")

    title("Landslide")

    savefig(
        join(workdir, "landslide.png"),
        bbox_inches='tight',
        dpi=200)
    close()



def plot_flood(workdir, flood_obj, event_id, extent=None, smooth=True, axis=None, adapt_fontsize=True, xy_res=250, **kwargs):

    def _geo_im_from_array(
        array_sub, coord, var_name, title,
        proj=None, smooth=True, axes=None, extent=None, figsize=(9, 13), adapt_fontsize=True,
        **kwargs):

        # Generate array of values used in each subplot
        num_im, list_arr = _get_collection_arrays(array_sub)
        list_tit = to_list(num_im, title, 'title')
        list_name = to_list(num_im, var_name, 'var_name')
        list_coord = to_list(num_im, coord, 'geo_coord')


        is_reg, height, width = u_coord.grid_is_regular(coord)
        if extent is None:
            extent = _get_borders(coord, proj_limits=(-360, 360, -90, 90))

        mid_lon = 0
        if not proj:
            mid_lon = 0.5 * sum(extent[:2])
            proj = ccrs.PlateCarree(central_longitude=mid_lon)
        if 'vmin' not in kwargs:
            kwargs['vmin'] = np.nanmin(array_sub)
        if 'vmax' not in kwargs:
            kwargs['vmax'] = np.nanmax(array_sub)
        if axes is None:
            if isinstance(proj, ccrs.PlateCarree):
                # use different projections for plot and data to shift the central lon in the plot
                xmin, xmax = u_coord.lon_bounds(np.concatenate([c[:, 1] for c in list_coord]))
                proj_plot = ccrs.PlateCarree(central_longitude=0.5 * (xmin + xmax))
            _, axes, fontsize = make_map(num_im, proj=proj_plot, figsize=figsize,
                                        adapt_fontsize=adapt_fontsize)
        else:
            fontsize = None
        axes_iter = axes
        if not isinstance(axes, np.ndarray):
            axes_iter = np.array([[axes]])

        if 'cmap' not in kwargs:
            kwargs['cmap'] = "jet"

        # Generate each subplot
        for array_im, axis, tit, name in zip(list_arr, axes_iter.flatten(), list_tit, list_name):
            if coord.shape[0] != array_im.size:
                raise ValueError("Size mismatch in input array: %s != %s." %
                                (coord.shape[0], array_im.size))
            if smooth or not is_reg:
                # Create regular grid where to interpolate the array
                grid_x, grid_y = np.mgrid[
                    extent[0]: extent[1]: complex(0, xy_res),
                    extent[2]: extent[3]: complex(0, xy_res)]
                grid_im = griddata((coord[:, 1], coord[:, 0]), array_im,
                                (grid_x, grid_y))
            else:
                grid_x = coord[:, 1].reshape((width, height)).transpose()
                grid_y = coord[:, 0].reshape((width, height)).transpose()
                grid_im = np.array(array_im.reshape((width, height)).transpose())
                if grid_y[0, 0] > grid_y[0, -1]:
                    grid_y = np.flip(grid_y)
                    grid_im = np.flip(grid_im, 1)
                grid_im = np.resize(grid_im, (height, width, 1))
            axis.set_extent((extent[0] - mid_lon, extent[1] - mid_lon,
                            extent[2], extent[3]), crs=proj)

            # Add coastline to axis
            add_shapes(axis)
            # Create colormesh, colorbar and labels in axis
            cbax = make_axes_locatable(axis).append_axes('right', size="6.5%",
                                                        pad=0.1, axes_class=plt.Axes)
            img = axis.pcolormesh(grid_x - mid_lon, grid_y, np.squeeze(grid_im),
                                transform=proj, **kwargs)
            cbar = plt.colorbar(img, cax=cbax, orientation='vertical')
            cbar.set_label(name)
            axis.set_title("\n".join(wrap(tit)))
            if fontsize:
                cbar.ax.tick_params(labelsize=fontsize)
                cbar.ax.yaxis.get_offset_text().set_fontsize(fontsize)
                for item in [axis.title, cbar.ax.xaxis.label, cbar.ax.yaxis.label]:
                    item.set_fontsize(fontsize)

        plt.tight_layout()

    def _event_plot(event_id, mat_var, col_name, smooth, crs_espg, axis=None,
                    figsize=(9, 13), extent=None, adapt_fontsize=True, **kwargs):

        if not isinstance(event_id, np.ndarray):
            event_id = np.array([event_id])
        array_val = list()
        l_title = list()
        for ev_id in event_id:
            if ev_id > 0:
                try:
                    event_pos = np.where(flood_obj.event_id == ev_id)[0][0]
                except IndexError as err:
                    raise ValueError(f'Wrong event id: {ev_id}.') from err
                im_val = mat_var[event_pos, :].toarray().transpose()
                title = 'Event ID %s: %s' % (str(flood_obj.event_id[event_pos]),
                                             flood_obj.event_name[event_pos])
            elif ev_id < 0:
                max_inten = np.asarray(np.sum(mat_var, axis=1)).reshape(-1)
                event_pos = np.argpartition(max_inten, ev_id)[ev_id:]
                event_pos = event_pos[np.argsort(max_inten[event_pos])][0]
                im_val = mat_var[event_pos, :].toarray().transpose()
                title = '%s-largest Event. ID %s: %s' % (np.abs(ev_id),
                                                         str(flood_obj.event_id[event_pos]),
                                                         flood_obj.event_name[event_pos])
            else:
                im_val = np.max(mat_var, axis=0).toarray().transpose()
                title = '%s max intensity at each point' % flood_obj.tag.haz_type

            array_val.append(im_val)
            l_title.append(title)

        _geo_im_from_array(
            array_val, flood_obj.centroids.coord, col_name,
            l_title, smooth=smooth, axes=axis, figsize=figsize,
            proj=crs_espg, adapt_fontsize=adapt_fontsize, extent=extent, **kwargs)

        return


    if isinstance(extent, str):
        extent = eval(extent)

    flood_obj._set_coords_centroids()
    col_label = 'Intensity (%s)' % flood_obj.units
    crs_epsg, _ = u_plot.get_transformation(flood_obj.centroids.geometry.crs)

    _event_plot(event_id, flood_obj.intensity, col_label, smooth, crs_epsg, axis, adapt_fontsize=adapt_fontsize, extent=extent, **kwargs)

    savefig(
        join(workdir, "flood.png"),
        bbox_inches='tight',
        dpi=200)
    close()