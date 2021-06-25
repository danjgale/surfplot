"""Main module containing the Plotter class"""

import numpy as np
from brainspace.mesh.mesh_io import read_surface
from brainspace.plotting.utils import PTuple
from brainspace.mesh.array_operations import get_labeling_border
from brainspace.vtk_interface.wrappers import BSPolyData

from surf import plot_surf

from brainspace.datasets import load_conte69, load_parcellation
from brainnotation.transforms import mni152_to_fslr


def check_surf(surf):
    if isinstance(surf, str):
        return read_surface(surf)
    elif isinstance(surf, BSPolyData) or (surf is None):
        return surf
    else:
        raise ValueError('Surface be a path-like string, an instance of '
                         'BSPolyData, or None')


def set_layout(lh, rh, layout, views):

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


class Plot(object):
    def __init__(self, surf_lh=None, surf_rh=None, layout='grid', views=None, 
                 size=(400, 400), zoom=1, background=(1, 1, 1), 
                 surf_shade=.5):

        hemi_inputs = zip(['left', 'right'], [surf_lh, surf_rh])
        self.surfaces = {k: check_surf(v) 
                         for k, v in hemi_inputs if v is not None}

        if views == None:
            views = ['lateral', 'medial']
        
        self.plot_layout = set_layout(surf_lh, surf_rh, layout, views)
        self.size = size
        self.zoom = zoom
        self.background = background
        self.layers, self.cmaps, self.color_ranges = [], [], []

        # add gray surface by default
        backdrop = np.ones(sum([v.n_points for v in self.surfaces.values()]))
        self.add_overlay(backdrop, 'Greys_r', vmin=0, 
                         vmax=1/surf_shade)


    def add_overlay(self, data, cmap='viridis', vmin=None, vmax=None, outline=False):
        

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
            x[x == 0] = np.nan
            v.append_array(x, name=name, at='p')
        
        self.layers.append(name)
        self.cmaps.append(cmap)
        
        if vmin == None and vmax == None:
            # let range automatically be determined
            self.color_ranges.append(None)
        else:
            self.color_ranges.append((vmin, vmax))


    def _make(self):

        view_layout, hemi_layout = self.plot_layout
        dims = np.array(view_layout).shape
        
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

        return plot_surf(surfs=self.surfaces, layout = hemi_layout,
                         array_name=names, cmap=cmap, color_bar='right',
                         color_range=color_range, view=view_layout,
                         background=self.background,
                         nan_color=(0.85, 0.85, 0.85, 0),
                         zoom=self.zoom, size=self.size, share=False,
                         return_plotter=True)

    def show(self, embed_nb=False, interactive=True):
        p = self._make()
        return p.show(embed_nb=embed_nb, interactive=interactive)

    def save(self):
        pass
