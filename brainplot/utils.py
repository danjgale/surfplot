"""Utilities to streamline plotting"""

import os
import numpy as np

DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

def add_medial_wall(data, split=False):
    """Add medial wall to data in fs_LR

    Data in 32k fs_LR space (e.g., Human Connectome Project data) often 
    exclude the medial wall in their data arrays, which results in a total of 
    59412 vertices across hemispheres. This function adds back in the missing 
    medial wall vertices to produce a data array with the full 64984 vertices, 
    which is required for plotting with 32k density fs_LR surfaces. 

    Parameters
    ----------
    data : numpy.ndarray
        Surface vertices. Must have exactly 59412 or 64984 vertices. Note that
        if 64984 vertices are present, then the medial wall is already included.
    split : bool
        Return left and right hemipsheres as separate arrays, by default False
    Returns
    -------
    numpy.ndarray
        Vertices with medial wall included (64984 vertices total)

    Raises
    ------
    ValueError
        `data` has the incorrect number of vertices (59412 or 64984 only 
        accepted)
    """
    data = data.copy().ravel()

    full_vertices = 64984
    hemi_vertices = full_vertices / 2

    if len(data) == full_vertices:
        if split:
            return data[:hemi_vertices], data[hemi_vertices:full_vertices]
    
    if len(data) != 59412:
        raise ValueError(f'{data.shape[0]} vertices were detected. `data` ' 
                         'must have exactly 59412 or 64984 vertices.')

    verts = np.loadtxt(os.path.join(DATA, 'medwall.tsv'))
    verts[verts == 1] = np.nan
    verts[verts == 0] = data

    if split:
        return verts[:hemi_vertices], verts[hemi_vertices:full_vertices]
    else:
        return verts