"""Main module containing the Plot class
"""
import pathlib
import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import nibabel as nib
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


def _set_layout(lh, rh, layout, views):
    """Determine hemisphere and view layout based user input"""
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


def _check_data(data):
    """Ensure that data is of appropriate type and return numpy array"""
    if isinstance(data, np.ndarray):
        return data.astype(float)
    elif isinstance(data, (str, pathlib.PosixPath)):
        data = nib.load(data)
    elif isinstance(data, (nib.Cifti2Image, nib.GiftiImage)):
        pass
    else:
        raise TypeError('data must be a file path to a valid GIFTI or CIFTI '
                        'file, or an instance of numpy.ndarray, '
                        'nibabel.Cifti2Image nibabel.GiftiImage')
    
    if isinstance(data, nib.Cifti2Image):
        return data.get_fdata().ravel().astype(float)
    else:
        return data.agg_data().ravel().astype(float)

    
def _find_color_range(v):
    """Find min and max of both hemispheres"""
    hemis = ['left', 'right']
    with warnings.catch_warnings():
        # not necessary to warn the user about this. NaNs won't impact anything
        warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
        vmin = np.nanmin([np.nanmin(v[h]) for h in hemis if h in v])
        vmax = np.nanmax([np.nanmax(v[h]) for h in hemis if h in v])
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
            return rotation, 'left', 'bottom'
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
    """Plot brain surfaces with data layers

    Parameters
    ----------
    surf_lh, surf_rh : str or os.PathLike or BSPolyData, optional
        Left and right hemisphere cortical surfaces, either as a file path 
        to a valid surface file (e.g., .gii. .surf) or a pre-loaded 
        surface from :func:`brainspace.mesh.mesh_io.read_surface`. At least one 
        hemisphere must be provided. Default: None
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
        views are plotted. Default: None
    flip : bool, optional
        Flip the display order of left and right hemispheres in `grid` or 
        `row` layouts, if applicable. Useful when showing only 'anterior` 
        or 'inferior' views. Default: False
    size : tuple of int, optional
        The size of the space to plot surfaces, defined by (width, height). 
        Note that this differs from `figsize` in Plot.build(), which 
        determines the overall figure size for the matplotlib figure. 
        Default: (500, 400)
    zoom : int, optional
        Level of zoom to apply. Default: 1.5
    background : tuple, optional
        Background color, default: (1, 1, 1)
    label_text : dict[str, array-like], optional
        Brainspace label text for column/row. Possible keys are 
        {‘left’, ‘right’, ‘top’, ‘bottom’}, which indicate the location. 
        See brainspace.plotting.surface_plotting.plot_surf for more 
        details Default: None. 
    brightness : float, optional
        Brightness of plain gray surface. 0 = black, 1 = white. Default: 
        .5
    
    Raises
    ------
    ValueError
        Neither `surf_lh` or `surf_rh` are provided
    """
    def __init__(self, surf_lh=None, surf_rh=None, layout='grid', views=None, 
                 flip=False, size=(500, 400), zoom=1.5, background=(1, 1, 1),
                 label_text=None, brightness=.5):
        hemi_inputs = zip(['left', 'right'], [surf_lh, surf_rh])
        self.surfaces = {k: _check_surf(v) 
                         for k, v in hemi_inputs if v is not None}
        
        if len(self.surfaces) == 0:
            raise ValueError('No surfaces are provided')

        if views == None:
            views = ['lateral', 'medial']
        self.plot_layout = _set_layout(surf_lh, surf_rh, layout, views)
        self.flip = flip

        # plot_surf args
        self.size = size
        self.zoom = zoom
        self.background = background
        self.label_text = label_text

        # these are updated with each overlay
        self.layers, self.cmaps, self.color_ranges = [], [], []
        self._show_cbar, self.cbar_labels = [], []

        # add gray surface default:
        backdrop = np.ones(sum([v.n_points for v in self.surfaces.values()]))
        brightness = 1e-6 if brightness == 0 else brightness
        backdrop *= brightness
        self.add_layer(backdrop, 'Greys_r', color_range=(0, 1), cbar=False)

    def add_layer(self, data, cmap='viridis', color_range=None,
                  as_outline=False, zero_transparent=True, cbar=True, 
                  cbar_label=None):
        """Add plotting layer to surface(s)

        Parameters
        ----------
        data : str or os.PathLike, numpy.ndarray, dict, nibabel.gifti.gifti.GiftiImage, or nibabel.cifti2.cifti2.Cifti2Image
            Vertex data to plot on surfaces. Must be a valid file path of a 
            GIFTI or CIFTI image, a loaded GIFTI or CIFTI image, a numpy array
            with length equal to the total number of vertices in the provided 
            surfaces (e.g., 32k in left surface + 32k in right surface = 64k 
            total), or a dictionary with 'left' and/or 'right keys. 
            If a numpy array, vertices are assumed to be in order of 
            left-to-right, if applicable. If a dictionary, then values can be
            any of the possible types mentioned above, assuming that the 
            vertices match the vertices of their respective surface.
        cmap : matplotlib colormap name or object, optional
            Colormap to use for data, default: 'viridis'
        color_range : tuple[float, float], optional
            Minimum and maximum value for color map. If None, then the minimum
            and maximum values in `data` are used. Default: None
        as_outline : bool, optional
            Plot only an outline of contiguous vertices with the same value. 
            Useful if plotting regions of interests, atlases, or discretized 
            data. Not recommended for continous data. Default: False
        zero_transparent : bool, optional
            Set vertices with value of 0 to NaN, which will turn them 
            transparent on the surface. Useful when value of 0 has no 
            importance (e.g., thresholded data, an atlas). Default: True
        cbar : bool, optional
            Show colorbar for layer, default: True
        cbar_label : str, optional
            Label to include with colorbar if shown. Note that this is not 
            required for the colorbar to be drawn. Default: None

        Raises
        ------
        ValueError
            `data` keys must be 'left' and/or 'right'
        TypeError
            `data` is neither an instance of str or os.PathLike, numpy.ndarray,
            dict, nibabel.gifti.gifti.GiftiImage, or 
            nibabel.cifti2.cifti2.Cifti2Image
        """
        # let the name just be the layer number 
        name = str(len(self.layers))

        valid_types = (np.ndarray, str, pathlib.PosixPath, nib.GiftiImage, 
                       nib.Cifti2Image)
        if isinstance(data, valid_types):
            data = _check_data(data)

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
                vertices = {k: _check_data(v) for k, v in data.items()}
            else:
                raise ValueError("Only valid keys for `data` are 'left' "
                                 "and/or 'right'")
        else:
            raise TypeError("Data type invalid")

        for k, v in self.surfaces.items():
            if k in vertices.keys():
                if as_outline:
                    x = get_labeling_border(v, vertices[k]).astype(float)
                else:
                    x = vertices[k]
                if zero_transparent:
                    x[x == 0] = np.nan
                v.append_array(x, name=name, at='p')
            else:
                # blank layer for unspecified hemisphere
                x = np.zeros(v.n_points)
                x[x == 0] = np.nan
                v.append_array(x, name=name, at='p')
        
        self.layers.append(name)
        self.cmaps.append(cmap)
        
        if color_range is None:
            self.color_ranges.append(_find_color_range(vertices))
        else:
            self.color_ranges.append(color_range)

        self._show_cbar.append(cbar)
        self.cbar_labels.append(cbar_label)

    def render(self, offscreen=True):
        """Generate surface plot with all provided layers

        Parameters
        ----------
        offscreen : bool, optional
            Render offscreen. Default: True

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
                         return_plotter=True, offscreen=offscreen)

    def _add_colorbars(self, location='bottom', label_direction=None,   
                       n_ticks=3, decimals=2, fontsize=10, draw_border=True, 
                       outer_labels_only=False, aspect=20, pad=.08, shrink=.3, 
                       fraction=.05):
        """Draw colorbar(s) for applicable layer(s)  

        Parameters
        ----------
        location : {'left', 'right', 'top', 'bottom'}, optional
            The location, relative to the surface plot. If location is 'top' or
            'bottom', then colorbars are horizontal. If location is'left' or 
            'right', then colorbars are vertical. 
        label_direction : int or None, optional
            Angle to draw label for colorbars, if provided. Horizontal = 0, 
            vertical = 90. If None and `location` is 'top' or 'bottom', labels 
            are drawn horizontally. If None and `location` is 'left' or 
            'right', labels are drawn vertically. Default: None
        n_ticks : int, optional
            Number of ticks to include on colorbar, default: 3 (minimum, 
            maximum, and middle values)
        decimals : int, optional
            Number of decimals to show for colorbal tick values. Set 0 to show 
            integers. Default: 2
        fontsize : int, optional
            Font size for colorbar labels and tick labels. Default: 10
        draw_border : bool, optional
            Draw ticks and black border around colorbar. Default: True
        outer_labels_only : bool, optional
            Show tick labels for only the outermost colorbar. This cleans up 
            tick labels when all colorbars are the same scale. Default: False
        pad : float, optional
            Space that separates each colorbar. Default: .08
        aspect : float, optional
            Ratio of long to short dimensions. Default: 20
        shrink : float, optional
            Fraction by which to multiply the size of the colorbar. 
            Default: .3
        fraction : float, optional
            Fraction of original axes to use for colorbar. Default: .05
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
                              shrink=shrink, aspect=aspect)

            tick_labels = np.linspace(vmin, vmax, n_ticks)
            if decimals > 0:
                tick_labels = np.around(tick_labels, decimals)
            else:
                tick_labels = tick_labels.astype(int)

            if outer_labels_only and i != cbar_indices[-1]:
                cb.set_ticklabels([])
            else:
                cb.set_ticklabels(tick_labels)
                cb.ax.tick_params(labelsize=fontsize)
            
            if self.cbar_labels[i] is not None:
                cb = _set_colorbar_labels(cb, self.cbar_labels[i], location,
                                          fontsize=fontsize, 
                                          rotation=label_direction)
            if not draw_border:
                cb.outline.set_visible(False)
                cb.ax.tick_params(size=0)
    
    def build(self, figsize=None, colorbar=True, cbar_kws=None, scale=(2, 2)):
        """Build matplotlib figure of surface plot

        Parameters
        ----------
        figsize : tuple, optional
            Overall figure size, specified by (width, height). Default: None, 
            which will determine the figure size based on the `size` parameter.
        colorbar : bool, optional
            Draw colorbars for each applicable layer, default: True
        cbar_kws : dict, optional
            Keyword arguments for 
            :func:`~surfplot.plottong.Plot._add_colorbar`. Default: None, 
            which will plot the default colorbar parameters. 
        scale : tuple, optional
            Amount to scale the surface plot. Default: (2, 2), which is a 
            good baseline for higher resolution plotting. 

        Returns
        -------
        matplotlib.pyplot.figure
            Surface plot figure
        """
        p = self.render()
        p._check_offscreen()
        x = p.to_numpy(transparent_bg=True, scale=scale)

        if figsize is None:
            figsize = tuple((np.array(self.size) / 100) + 1)

        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(x)
        ax.axis('off')
        if colorbar:
            cbar_kws = {} if cbar_kws is None else cbar_kws
            self._add_colorbars(**cbar_kws)

        return fig

    def show(self, embed_nb=False, interactive=True, transparent_bg=True, 
             scale=(1, 1)):
        """View Brainspace vtk surface rendering

        Notes
        -----
        This only shows the plot created by 
        brainspace.plotting.surface_plotting.plot_surf, and will not include 
        colorbars created by :func:`~surfplot.plottong.Plot.plot` or any 
        other matplotlib components.  

        Parameters
        ----------
        embed_nb : bool, optional
            Whether to embed figure in notebook. Only used if running in a 
            notebook. Default: False
        interactive : bool, optional
            Whether to enable interaction, default: True
        scale : tuple, optional
            Amount to scale the surface plot, default: (1, 1)

        Returns
        -------
        Ipython Image or vtk panel
            Brainspace surface plot rendering
        """
        p = self.render(offscreen=False)
        return p.show(embed_nb, interactive, scale=scale)
