"""Main module containing the Plotter class"""

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
    if isinstance(surf, str):
        return read_surface(surf)
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
    valid_views = ['medial', 'lateral', 'ventral', 'dorsal', 'anterior', 'posterior']
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


def _set_label_positions(orientation, rotation):
    """Get rotation, horizontal alignment, and vertical alignment, 
    respectively, based on orientation and rotation
    """
    if orientation == 'horizontal':
        rotation = 'horizontal' if rotation is None else rotation
        return rotation, 'right', 'center'
    
    else:
        rotation = 90 if rotation is None else rotation
        if rotation == 90 or rotation == 0:
            return rotation, 'center', 'bottom'
        else:
            return rotation, 'left', 'center'


def _set_colorbar_labels(cbar, label, orientation, fontsize=10, rotation=None):
    """Add colorbar labels to drawn colorbar"""
    rotation, ha, va = _set_label_positions(orientation, rotation)
    label_args = dict(rotation=rotation, ha=ha, va=va, fontsize=fontsize)
    
    if orientation == 'horizontal':
        cbar.ax.set_ylabel(label, **label_args)
    else:
        cbar.ax.set_title(label, pad=10, **label_args)
    return cbar


class Plot(object):
    def __init__(self, surf_lh=None, surf_rh=None, layout='grid', views=None, 
                 size=(400, 400), zoom=1, background=(1, 1, 1),
                 label_text=None, surf_shade=.5):
    
        hemi_inputs = zip(['left', 'right'], [surf_lh, surf_rh])
        self.surfaces = {k: _check_surf(v) 
                         for k, v in hemi_inputs if v is not None}

        if views == None:
            views = ['lateral', 'medial']
        self.plot_layout = set_layout(surf_lh, surf_rh, layout, views)

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
        self.add_overlay(backdrop, 'Greys_r', color_range=(0, 1 / surf_shade), 
                         show_cbar=False)


    def add_overlay(self, data, cmap='viridis', color_range=None,
                    outline=False, zero_transparent=True, show_cbar=True, 
                    cbar_label=None):
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
                raise ValueError("Only valid keys for `x` are 'left' and/or "
                                 "'right'")
        else:
            raise TypeError('`x` must be an instance of numpy.ndarray or dict')

        for k, v in self.surfaces.items():
            if outline:
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

    def build(self, flip=False):
        view_layout, hemi_layout = self.plot_layout
        dims = np.array(view_layout).shape
                
        if flip and len(self.surfaces) == 2:
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

    def _add_colorbars(self, orientation='horizontal', label_direction=None,   
                       n_ticks=3, decimals=2, fontsize=10,
                       show_outline=True, share_tick_labels=False, 
                       pad=.08, shrink=.3, fraction=.05):
        
        cbar_pads = [.01] + [pad] * (len(self._show_cbar) - 1)
        cbar_indices = [i for i, c in enumerate(self._show_cbar) if c]
        
        # draw in reverse order so that outermost colorbar is uppermost layer
        for i in cbar_indices[::-1]:
            vmin, vmax = self.color_ranges[i]

            norm = mpl.colors.Normalize(vmin, vmax)
            sm = plt.cm.ScalarMappable(cmap=self.cmaps[i], norm=norm)
            sm.set_array([])
            ticks = np.linspace(vmin, vmax, n_ticks)
            
            cb = plt.colorbar(sm, ticks=ticks, orientation=orientation, 
                              fraction=fraction, pad=cbar_pads[i], 
                              shrink=shrink)

            tick_labels = np.linspace(vmin, vmax, n_ticks)
            if decimals > 0:
                tick_labels = np.around(tick_labels, decimals)
            else:
                tick_labels = tick_labels.as_type(int)

            if share_tick_labels and i != cbar_indices[-1]:
                cb.set_ticklabels([])
            else:
                cb.set_ticklabels(tick_labels)
            
            if self.cbar_labels[i] is not None:
                cb = _set_colorbar_labels(cb, self.cbar_labels[i], orientation,
                                          fontsize=fontsize, 
                                          rotation=label_direction)
            if not show_outline:
                cb.outline.set_visible(False)
                cb.ax.tick_params(size=0)
    
    def plot(self, transparent_bg=True, scale=(2, 2), flip=False, 
             figsize=None, colorbar=True, cbar_kws=None):

        p = self.build(flip)
        x = p.to_numpy(transparent_bg, scale)

        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(x)
        ax.axis('off')
        if colorbar:
            cbar_kws = {} if cbar_kws is None else cbar_kws
            self._add_colorbars(**cbar_kws)

        return fig

    def save(self, fname=None, transparent_bg=True, scale=(1, 1), flip=False):
        p = self.build(flip)
        p.screenshot(fname, transparent_bg, scale)

    def show(self, embed_nb=False, interactive=True, transparent_bg=True, 
             scale=(1, 1), flip=False):
        p = self.build(flip)
        return p.show(embed_nb, interactive, transparent_bg, scale)




