# -*- coding: utf-8 -*-
"""
.. _tutorial02_ref:

Tutorial 02: Types of Surfaces
==============================

This tutorial covers what types of surfaces that can be plotted with 
``brainplot``. 

Types of surfaces
-----------------

Put briefly, ``brainplot`` can take file paths to any valid surface file(s) 
with geometry data. Under the hood, :class:`brainplot.plotting.Plot` runs 
:func:`brainspace.mesh.mesh_io.read_surface` to load files. Typically, these
will be Freesurfer or GIFTI files. 

:class:`Plot` can also read instances of 
:class:`brainspace.vtk_interface.wrappers.data_object.BSPolyData`, which are 
returned by :func:`read_surface`. So, pre-loaded surfaces with 
:func:`read_surface` can be plotted as well.

Beyond that, ``brainplot`` is invariant to the actual brain surfaces you wish
to use. Common human surfaces include `fsaverage` surfaces packaged with 
Freesurfer, and Human Connectome Project `fsLR` surfaces (`downloadable here 
<https://balsa.wustl.edu/reference/show/pkXDZ>`_). Several different 
human surfaces can also all be found on OSF `here <https://osf.io/4mw3a/>`_. 
Non-human surfaces can also be plotted, such as the `NMTv2 Macaque surfaces 
<https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/nonhuman/macaque_tempatl/template_nmtv2.html>`_.

Note that throughout these tutorials, surfaces are automatically fetched using
``brainnotation`` or  ``Brainspace`` to avoid having to specify local files. It
is also possible to `fetch fsaverage surfaces <https://nilearn.github.io/modules/generated/nilearn.datasets.fetch_surf_fsaverage.html#nilearn.datasets.fetch_surf_fsaverage>`_
using ``nilearn``. These are all great options to automically get surfaces in
your workflow, and make reproducibility and portability of your code a bit 
more feasible.

.. note::
    Make sure to *always* use the correct surface for your data. Double check 
    the number of vertices in both your data and the surfaces you are using for
    plotting.

In :ref:`sphx_glr_auto_examples_plot_tutorial_01.py` we plotted `fsLR` 
surfaces. For the sake of demonstration, let's plot Freesurfer's `fsaverage` 
here, again using ``brainnotation`` fetching functions.
"""
from brainnotation.datasets import fetch_fsaverage
from brainplot import Plot

surfaces = fetch_fsaverage(density='164k')
lh, rh = surfaces['inflated']

# make figure
p = Plot(lh, rh)
fig = p.build()
fig.show()
###############################################################################
# Brightness
# ----------
#
# By default, :class:`Plot` will plot a medium-gray surface, typical of most
# surface plotting packages like Connectome Workbench. The brightness of the
# blank surface can be adjusted using the `brightness` parameter, if desired.
# Values range from 0 (black) to 1 (white). For example:  
p = Plot(lh, rh, brightness=.8)
fig = p.build()
fig.show()
