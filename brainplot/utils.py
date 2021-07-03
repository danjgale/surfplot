"""Utility functions that streamline preparing vertex arrays for plotting"""

import os
import numpy as np

DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

def add_fslr_medial_wall(data, split=False):
    """Add medial wall to data in fsLR space

    Data in 32k fs_LR space (e.g., Human Connectome Project data) often 
    exclude the medial wall in their data arrays, which results in a total of 
    59412 vertices across hemispheres. This function adds back in the missing 
    medial wall vertices to produce a data array with the full 64984 vertices, 
    which is required for plotting with 32k density fsLR surfaces. 

    Parameters
    ----------
    data : numpy.ndarray
        Surface vertices. Must have exactly 59412 or 64984 vertices. Note that
        if 64984 vertices are present, then the medial wall is already 
        included. If so, then only hemisphere splitting will be performed, 
        if applied.
    split : bool
        Return left and right hemipsheres as separate arrays. Default: False
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
        else:
            return data
    
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


def threshold(data, thresh, binarize=False, two_sided=True):
    """Threshold vertex array

    Parameters
    ----------
    data : numpy.ndarray
        Vertex array
    thresh : float
        Threshold value. All values below or equal to threshold are set 0.
    binarize : bool, optional
        Set all values above threshold to 1. Default: False
    two_sided : bool, optional
        Apply thresholding to both positive and negative values. Default: True

    Returns
    -------
    numpy.ndarray
        Thresholded data
    """
    fill = 1 if binarize else data
    if two_sided:
        return np.where(np.abs(data) > thresh, fill, 0)
    else:
        return np.where(data > thresh, fill, 0)
