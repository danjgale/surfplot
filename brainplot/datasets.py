"""Convenient data fetchers for tutorial examples"""

import os
import numpy as np

DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

def load_example_data(dataset='default_mode', join=False):
    """Load example datasets for tutorials

    Precomputed association maps for terms 'default mode' or 'frontoparietal'
    using Neurosynth. In brief, maps were downloaded from Neurosynth and 
    projected to fsLR space using ``brainnotation.transforms.mni152_to_fslr``.
    Then, their vertex arrays were saved. 

    1. Default mode: https://www.neurosynth.org/analyses/terms/default%20mode/  
    2. Frontoparietal: https://www.neurosynth.org/analyses/terms/frontoparietal/

    Yarkoni T, Poldrack RA, Nichols TE, Van Essen DC, Wager TD. 2011. 
    Large-scale automated synthesis of human functional neuroimaging data. 
    Nat Methods. 8:665–670.

    Parameters
    ----------
    dataset : {'default_mode', 'frontoparietal'}, optional
        Neurosynth association map. Default: 'default_mode'
    join : bool, optional
        Return data as a single concatenated array. Default: False, which
        returns left and right hemisphere arrays, respectively

    Returns
    -------
    numpy.ndarray
        Vertex array(s)
    """
    if dataset not in ['default_mode', 'frontoparietal']:
        raise ValueError("dataset must be one 'default_mode' or "
                         "'frontoparietal'")

    lh = np.loadtxt(os.path.join(DATA, f'lh_{dataset}_example.tsv'))
    rh = np.loadtxt(os.path.join(DATA, f'rh_{dataset}_example.tsv'))

    if join:
        return np.concatenate([lh, rh])
    else:
        return lh, rh
