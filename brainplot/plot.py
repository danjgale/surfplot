"""Main module containing the Plot class
"""
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from brainspace.mesh.mesh_io import read_surface
from brainspace.plotting.utils import PTuple
from brainspace.mesh.array_operations import get_labeling_border
from brainspace.vtk_interface.wrappers import BSPolyData

from .surf import plot_surf

def _check_surf(surf):
    """Validate surface type and load if a file name"""
    if isinstance(surf, (str, pathlib.PosixPath)):
        return read_surface(str(surf))
    elif isinstance(surf, BSPolyData) or (surf is None):
        return surf
    else:
        raise ValueError('Surface be a path-like string, an instance of '
                         'BSPolyData, or None')


def set_layout(lh, rh, layout, views):
    """Determine hemisphere and view layout based user input

    Parameters
    ----------
    lh, rh : str, BSPolyData, or None
        Left and right hemisphere input
    layout : {'grid', 'row', 'column'}
        Layout style
    views : str or list
        One or more view types: 'medial', 'lateral', 'ventral', 'dorsal', 
        'anterior', or 'posterior'

    Returns
    -------
    list, list
        lists defining view and hemisphere layouts, respectively

    Raises
    ------
    ValueError
        Invalid layout and/or views are provided
    """
    valid_layouts = ['grid', 'row', 'column']
    if layout not in  valid_layouts:
        raise ValueError(f'layout must be one of {valid_layouts}')
    
    if isinstance(views, str):
        views = [views]
    valid_views = ['medial', 'lateral', 'ventral', 'dorsal', 'anterior', 
                   'posterior']
    if not set(views) <= set(valid_views):
        raise ValueError(f'layout must be one of {valid_views}') 

    n_hemi = len([x for x in [lh, rh] if x is not None])
    n_views = len(views)

    # create view (v) and hemisphere (h) matrices for plotting layout
    v, h = np.array([], dtype=object), np.array([], dtype=object)
    if lh is not None:
        v = np.concatenate([v, np.array(views)])
        h = np.concatenate([h, np.array(['left'] * n_views)])
    if rh is not None:
        # flip medial/lateral
        view_key = dict(medial='lateral', lateral='medial', dorsal='dorsal', 
                        ventral='ventral', anterior='anterior', 
                        posterior='posterior')
        rh_views = [view_key[i] for i in views]
        v = np.concatenate([v, np.array(rh_views)])
        h = np.concatenate([h, np.array(['right'] * n_views)])

    if layout == 'grid':
        v = v.reshape(n_hemi, n_views).T
        h = h.reshape(n_hemi, n_views).T    
    elif layout == 'column':
        v = v.reshape(v.shape[0], 1)
        h = h.reshape(h.shape[0], 1)

    # flatten if applicable (nb: grid layout with 1 hemi is a row)
    if ((n_hemi == 1) or (n_views == 1)) and (layout != 'column'):
        v = v.ravel()
        h = h.ravel()

    return v.tolist(), h.tolist()


def _flip_hemispheres(v, h):
    """Flip left and right hemispheres in the horizontal dimension

    Parameters
    ----------
    v : list
        View layout list
    h : list
        Hemisphere layout list

    Returns
    -------
    list, list
        Flipped view and hemisphere layouts 
    """
    v = np.array(v)
    h = np.array(h)
    if (v.ndim == 1) and (v.shape[0] > 1):
        # flip row
        flip_axis = 0
    elif (v.ndim == 2) and (v.shape[1] > 1):
        # flip grid
        flip_axis = 1
    return np.flip(v, flip_axis).tolist(), np.flip(h, flip_axis).tolist()


def _find_color_range(v):
    """Find min and max of both hemispheres"""
    hemis = ['left', 'right']
    vmin = np.min([np.nanmin(v[h]) for h in hemis if h in v])
    vmax = np.max([np.nanmax(v[h]) for h in hemis if h in v])
    return vmin, vmax


def _set_label_positions(location, rotation):
    """Get rotation, horizontal alignment, and vertical alignment, 
    respectively, based on orientation and rotation
    """
    if location in ['top', 'bottom']:
        rotation = 'horizontal' if rotation is None else rotation
        return rotation, 'right', 'center'
    
    elif location in ['left', 'right']:
        rotation = 90 if rotation is None else rotation
        if rotation == 90 or rotation == 0:
            return rotation, 'center', 'bottom'
        else:
            return rotation, 'left', 'center'
    else:
        raise ValueError("`location` must be 'top', 'bottom', 'left' or "
                         "'right'")


def _set_colorbar_labels(cbar, label, location, fontsize=10, rotation=None):
    """Add colorbar labels to drawn colorbar"""

    valid_locations = ['top', 'bottom', 'left', 'right']
    if location not in valid_locations:
        raise ValueError(f"`location` must be one of {valid_locations}")

    rotation, ha, va = _set_label_positions(location, rotation)
    label_args = dict(rotation=rotation, ha=ha, va=va, fontsize=fontsize)
    
    if location in ['top', 'bottom']:
        cbar.ax.set_ylabel(label, **label_args)
    else:
        cbar.ax.set_title(label, pad=10, **label_args)
    return cbar


class Plot(object):
    def __init__(self, surf_lh=None, surf_rh=None, layout='grid', views=None, 
                 flip=False, size=(400, 400), zoom=1, background=(1, 1, 1),
                 label_text=None, brightness=.5):
        """Class to plot brain surfaces with data layers

        Parameters
        ----------
        surf_lh, surf_rh : str or os.PathLike or BSPolyData, optional
            Left and right hemisphere cortical surfaces, either as a file path 
            to a valid surface file (e.g., .gii. .surf) or a pre-loaded 
            surface from brainspace.mesh.mesh_io.read_surface. At least one 
            hemisphere must be provided. By default None
        layout : {'grid', 'column', 'row'}, optional
            Layout in which to plot brain surfaces. 'row' plots brains as a 
            single row ordered from left-to-right hemispheres (if applicable), 
            'column' plots brains as a single column descending from 
            left-to-right hemispheres (if applicable). 'grid' plots surfaces 
            as a views-by-hemisphere (left-right) array; if only one 
            hemipshere is provided, then 'grid' is equivalent to 'row'. By 
            default 'grid'.
        views : {'lateral', 'medial', 'dorsal', 'ventral', 'anterior', 
                 'posterior'}, str or list[str], optional
            Views to plot for each provided hemisphere. Views are plotted in 
            in the order they are provided. If None, then lateral and medial
            views are plotted. By default None
        flip : bool, optional
            Flip the display order of left and right hemispheres in `grid` or 
            `row` layouts, if applicable. Useful when showing only 'anterior` 
            or 'inferior' views. By default False
        size : tuple of int, optional
            The size of the space to plot surfaces, defined by (width, height). 
            Note that this differs from `figsize` in Plot.plot(), which 
            determines the overall figure size for the matplotlib figure. 
            By default (400, 400)
        zoom : int, optional
            Level of zoom to apply, by default 1
        background : tuple, optional
            Background color, by default (1, 1, 1)
        label_text : dict[str, array-like], optional
            Brainspace label text for column/row. Possible keys are 
            {‘left’, ‘right’, ‘top’, ‘bottom’}, which indicate the location. 
            See brainspace.plotting.surface_plotting.plot_surf for more 
            details By default None. 
        brightness : float, optional
            Brightness of plain gray surface. 0 = black, 1 = white. By default 
            .5
        
        Raises
        ------
        ValueError
            Neither `surf_lh` or `surf_rh` are provided
        """
        hemi_inputs = zip(['left', 'right'], [surf_lh, surf_rh])
        self.surfaces = {k: _check_surf(v) 
                         for k, v in hemi_inputs if v is not None}
        
        if len(self.surfaces) == 0:
            raise ValueError('No surfaces are provided')

        if views == None:
            views = ['lateral', 'medial']
        self.plot_layout = set_layout(surf_lh, surf_rh, layout, views)
        self.flip = flip

        # plot_surf args
        self.size = size
        self.zoom = zoom
        self.background = background
        self.label_text = label_text

        # these are updated with each overlay
        self.layers, self.cmaps, self.color_ranges = [], [], []
        self._show_cbar, self.cbar_labels = [], []

        # add gray surface by default
        backdrop = np.ones(sum([v.n_points for v in self.surfaces.values()]))
        backdrop *= brightness
        self.add_layer(backdrop, 'Greys_r', color_range=(0, 1), 
                       show_cbar=False)

    def add_layer(self, data, cmap='viridis', color_range=None,
                  as_outline=False, zero_transparent=True, show_cbar=True, 
                  cbar_label=None):
        """Add plotting layer to surface

        Parameters
        ----------
        data : numpy.ndarray, dict[{'left', 'right'}, numpy.ndarray]
            Vertex data to plot on surfaces. If a numpy array, the length must 
            equal to the total number of vertices in the provided surfaces 
            (e.g., 32k in left surface + 32k in right surface = 64k total). 
            Vertices are assumed to be in order of left-to-right, if 
            applicable. If a dictionary, then vertices can be explicitly 
            passed to each available hemisphere surface using 'left' and/or 
            'right' keys. Here, the length of the numpy array must equal the 
            vertices in the assigned hemisphere. See online examples for more
            detail.
        cmap : matplotlib colormap name or object, optional
            Colormap to use for data, by default 'viridis'
        color_range : tuple[float, float], optional
            Minimum and maximum value for color map. If None, then the minimum
            and maximum values in `data` are used. By default None
        as_outline : bool, optional
            Plot only an outline of contiguous vertices with the same value. 
            Useful if plotting regions of interests, atlases, or discretized 
            data. Not recommended for continous data. By default False
        zero_transparent : bool, optional
            Set vertices with value of 0 to NaN, which will turn them 
            transparent on the surface. Useful when value of 0 has no 
            importance (e.g., thresholded data, an atlas). By default True
        show_cbar : bool, optional
            Show colorbar for layer, by default True
        cbar_label : str, optional
            Label to include with colorbar if shown. Note that this is not 
            required for the colorbar to be drawn. By default None

        Raises
        ------
        ValueError
            `data` keys must be 'left' and/or 'right'
        TypeError
            `data` is neither an instance of numpy.ndarray or dict
        """
        # let the name just be the layer number 
        name = str(len(self.layers))

        if isinstance(data, np.ndarray):
            data = data.astype(float)

            vertices = {}
            if len(self.surfaces.keys()) == 2:
                lh_points = self.surfaces['left'].n_points
                rh_points = self.surfaces['right'].n_points
                vertices['left'] = data[:lh_points] 
                vertices['right'] = data[lh_points:lh_points + rh_points]
            else:
                key = list(self.surfaces.keys())[0]
                vertices[key] = data 
        elif isinstance(data, dict):
            if set(data.keys()) <= set(['left', 'right']):
                vertices = data
            else:
                raise ValueError("Only valid keys for `data` are 'left' "
                                 "and/or 'right'")
        else:
            raise TypeError("`data` must be an instance of numpy.ndarray or "
                            "dict")

        for k, v in self.surfaces.items():
            if as_outline:
                x = get_labeling_border(v, vertices[k]).astype(float)
            else:
                x = vertices[k].astype(float)
            if zero_transparent:
                x[x == 0] = np.nan
            v.append_array(x, name=name, at='p')
        
        self.layers.append(name)
        self.cmaps.append(cmap)
        
        if color_range is None:
            self.color_ranges.append(_find_color_range(vertices))
        else:
            self.color_ranges.append(color_range)

        self._show_cbar.append(show_cbar)
        self.cbar_labels.append(cbar_label)

    def build(self):
        """Generate surface plot with all provided layers

        Returns
        -------
        brainspace.plotting.base.Plotter
            Surface plot 
        """
        view_layout, hemi_layout = self.plot_layout
        dims = np.array(view_layout).shape
                
        if self.flip and len(self.surfaces) == 2:
            view_layout, hemi_layout = _flip_hemispheres(view_layout, 
                                                         hemi_layout)

        # create plot tuples
        layers = PTuple(*self.layers)
        cmaps = PTuple(*self.cmaps)
        crange = PTuple(*self.color_ranges)

        if all(i != 1 for i in dims) and (len(dims) == 2):
            # grid layout
            names = [[layers] * dims[1]] * dims[0]
            cmap = [cmaps] * dims[1]
            color_range = [crange] * dims[1]
        else:
            # column or row layout
            names = [layers]
            cmap = [cmaps]
            color_range = [crange]

        return plot_surf(surfs=self.surfaces, layout=hemi_layout,
                         array_name=names, cmap=cmap, color_bar=False,
                         color_range=color_range, view=view_layout,
                         background=self.background, zoom=self.zoom,
                         nan_color=(0, 0, 0, 0), share=True,
                         label_text=self.label_text, size=self.size, 
                         return_plotter=True)

    def _add_colorbars(self, location='bottom', label_direction=None,   
                       n_ticks=3, decimals=2, fontsize=10,
                       draw_border=True, outer_labels_only=False, 
                       pad=.08, shrink=.3, fraction=.05):
        """Draw colorbar for applicable layers  

        Parameters
        ----------
        location : {'left', 'right', 'top', 'bottom'}, optional
            The location, relative to the surface plot. 
        label_direction : int or None, optional
            Angle to draw label for colorbars, if provided. Horizontal = 0, 
            vertical = 90. If None and `orientation` is 'horizontal', labels 
            are drawn horizontally. If None and `orientation` is 'vertical', 
            labels are drawn vertically. By default None
        n_ticks : int, optional
            Number of ticks to include on colorbar, by default 3 (minimum, 
            maximum, and middle values)
        decimals : int, optional
            Number of decimals to show for colorbal tick values. Set 0 to show 
            integers. By default 2
        fontsize : int, optional
            Font size for labels and tick labels, by default 10
        draw_border : bool, optional
            Draw ticks and black border around colorbar, by default True
        outer_labels_only : bool, optional
            Show tick labels for only the outermost colorbar. This cleans up 
            tick labels when all colorbars are the same scale. By default False
        pad : float, optional
            Space that separates each colorbar, by default .08
        shrink : float, optional
            Fraction by which to multiply the size of the colorbar, by 
            default .3
        fraction : float, optional
            Fraction of original axes to use for colorbar, by default .05
        """
        cbar_pads = [.01] + [pad] * (len(self._show_cbar) - 1)
        cbar_indices = [i for i, c in enumerate(self._show_cbar) if c]
        
        # draw in reverse order so that outermost colorbar is uppermost layer
        for i in cbar_indices[::-1]:
            vmin, vmax = self.color_ranges[i]

            norm = mpl.colors.Normalize(vmin, vmax)
            sm = plt.cm.ScalarMappable(cmap=self.cmaps[i], norm=norm)
            sm.set_array([])
            ticks = np.linspace(vmin, vmax, n_ticks)
            
            cb = plt.colorbar(sm, ticks=ticks, location=location, 
                              fraction=fraction, pad=cbar_pads[i], 
                              shrink=shrink)

            tick_labels = np.linspace(vmin, vmax, n_ticks)
            if decimals > 0:
                tick_labels = np.around(tick_labels, decimals)
            else:
                tick_labels = tick_labels.as_type(int)

            if outer_labels_only and i != cbar_indices[-1]:
                cb.set_ticklabels([])
            else:
                cb.set_ticklabels(tick_labels)
            
            if self.cbar_labels[i] is not None:
                cb = _set_colorbar_labels(cb, self.cbar_labels[i], location,
                                          fontsize=fontsize, 
                                          rotation=label_direction)
            if not draw_border:
                cb.outline.set_visible(False)
                cb.ax.tick_params(size=0)
    
    def plot(self, figsize=None, colorbar=True, cbar_kws=None, 
             transparent_bg=True, scale=(2, 2)):
        """Draw matplotlib figure of surface plot

        Parameters
        ----------
        figsize : tuple, optional
            Overall figure size, specified by (width, height). By default None
        colorbar : bool, optional
            Draw colorbars for each applicable layer, by default True
        cbar_kws : dict, optional
            Keyword arguments for `Plot._add_colorbar`. By default None, which
            will plot the default colorbar parameters
        scale : tuple, optional
            Amount to scale the surface plot. By default (2, 2), which is a 
            good baseline for higher resolution plotting. 

        Returns
        -------
        matplotlib.pyplot.figure
            Surface plot figure
        """
        p = self.build()
        x = p.to_numpy(transparent_bg=True, scale=scale)

        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(x)
        ax.axis('off')
        if colorbar:
            cbar_kws = {} if cbar_kws is None else cbar_kws
            self._add_colorbars(**cbar_kws)

        return fig

    def save(self, fname, transparent_bg=True, scale=(1, 1)):
        """Save Brainspace vtk rendering to file.

        Notes
        -----
        This save the plot created by 
        brainspace.plotting.surface_plotting.plot_surf, and will not include 
        colorbars created by `Plot.plot()` or any other matplotlib components.   

        Parameters
        ----------
        fname : str or os.PathLike
            File name for saving. By default None
        transparent_bg : bool, optional
            Whether to us a transparent background. By default True
        scale : tuple, optional
            Amount to scale the surface plot, by default (1, 1)
        """
        p = self.build()
        p.screenshot(fname, transparent_bg, scale)

    def show(self, embed_nb=False, interactive=True, transparent_bg=True, 
             scale=(1, 1)):
        """View Brainspace surface rendering as an IPython image or in an 
        interactive vtk window.

        Notes
        -----
        This only shows the plot created by 
        brainspace.plotting.surface_plotting.plot_surf, and will not include 
        colorbars created by `Plot.plot()` or any other matplotlib components.  

        Parameters
        ----------
        embed_nb : bool, optional
            Whether to embed figure in notebook. Only used if running in a 
            notebook. By default False
        interactive : bool, optional
            Whether to enable interaction, by default True
        scale : tuple, optional
            Amount to scale the surface plot, by default (1, 1)

        Returns
        -------
        Ipython Image or vtk panel
            Brainspace surface plot rendering
        """
        p = self.build()
        return p.show(embed_nb, interactive, scale=scale)




