
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "auto_examples/plot_tutorial_06.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        :ref:`Go to the end <sphx_glr_download_auto_examples_plot_tutorial_06.py>`
        to download the full example code.

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_plot_tutorial_06.py:


.. _tutorial06_ref:

Tutorial 6: Regions and Parcellations
=====================================

This tutorial demonstrates how to plot brain regions.

Regions and parcellations can be plotted with ``brainplot`` as one or more 
layers, and it's possible to add region outlines by simply adding a layer with
the `as_outline` parameter.

Parcellations
-------------

Multiple brain regions can be plotted as a single layer as long as the vertices 
in different regions have different numerical labels/values, which is typical 
for any parcelation. To demonstrate, we can use the 
:func:`~brainspace.datasets.load_parcellation` from ``Brainspace`` to load the
`Schaefer 400 parcellation`_.

.. GENERATED FROM PYTHON SOURCE LINES 23-37

.. code-block:: Python

    from neuromaps.datasets import fetch_fslr
    from surfplot import Plot
    from brainspace.datasets import load_parcellation

    surfaces = fetch_fslr()
    lh, rh = surfaces['inflated']
    p = Plot(lh, rh)

    # add schaefer parcellation (no color bar needed)
    lh_parc, rh_parc = load_parcellation('schaefer')
    p.add_layer({'left': lh_parc, 'right': rh_parc}, cbar=False)

    fig = p.build()
    fig.show()



.. image-sg:: /auto_examples/images/sphx_glr_plot_tutorial_06_001.png
   :alt: plot tutorial 06
   :srcset: /auto_examples/images/sphx_glr_plot_tutorial_06_001.png
   :class: sphx-glr-single-img





.. GENERATED FROM PYTHON SOURCE LINES 38-42

Now can add a second layer of just the region outlines. This is done by 
setting `as_outline=True`. The color of the outlines are set by the `cmap` 
parameter, as with any data. To show black outlines, we can just use the 
`gray` colormap.

.. GENERATED FROM PYTHON SOURCE LINES 42-46

.. code-block:: Python

    p.add_layer({'left': lh_parc, 'right': rh_parc}, cmap='gray', 
                as_outline=True, cbar=False)
    fig = p.build()
    fig.show()



.. image-sg:: /auto_examples/images/sphx_glr_plot_tutorial_06_002.png
   :alt: plot tutorial 06
   :srcset: /auto_examples/images/sphx_glr_plot_tutorial_06_002.png
   :class: sphx-glr-single-img





.. GENERATED FROM PYTHON SOURCE LINES 47-56

Regions of Interest
-------------------

Often times we want to show a selection of regions, instead of all regions. 
These could be regions from a parcellation, regions defined from a 
functional localizer, etc. 

Let's select two regions from the Schaefer parcellation and zero-out the 
remaining regions. We'll just stick with the left hemisphere here.

.. GENERATED FROM PYTHON SOURCE LINES 56-60

.. code-block:: Python

    import numpy as np
    region_numbers = [71, 72]
    # zero-out all regions except 71 and 72
    regions = np.where(np.isin(lh_parc, region_numbers), lh_parc, 0)







.. GENERATED FROM PYTHON SOURCE LINES 61-64

Although we can use a pre-defined color map, we might want to define a 
custom colormap where we can define the exact color for each region. This is
possible using ``matplotlib``:

.. GENERATED FROM PYTHON SOURCE LINES 64-68

.. code-block:: Python

    from matplotlib.colors import ListedColormap

    colors = ['orange', 'steelblue']
    cmap = ListedColormap(colors, 'regions', N=2)







.. GENERATED FROM PYTHON SOURCE LINES 69-71

Now we can plot both regions with their outlines:
only need to show the left lateral view

.. GENERATED FROM PYTHON SOURCE LINES 71-78

.. code-block:: Python

    p = Plot(lh, views='lateral')
    p.add_layer(regions, cmap=cmap, cbar=False)
    p.add_layer(regions, cmap='gray', as_outline=True, cbar=False)

    fig = p.build()
    fig.show()
    # sphinx_gallery_thumbnail_number = 3



.. image-sg:: /auto_examples/images/sphx_glr_plot_tutorial_06_003.png
   :alt: plot tutorial 06
   :srcset: /auto_examples/images/sphx_glr_plot_tutorial_06_003.png
   :class: sphx-glr-single-img





.. GENERATED FROM PYTHON SOURCE LINES 79-84

.. note::
  Multiple regions can also be plotted as individual layers, rather
  than combined as a single layer, as shown here. In this case, the vertex 
  array(s) for each layer would be binary. 

.. _Schaefer 400 parcellation: https://github.com/ThomasYeoLab/CBIG/tree/master/stable_projects/brain_parcellation/Schaefer2018_LocalGlobal


.. rst-class:: sphx-glr-timing

   **Total running time of the script:** (0 minutes 0.400 seconds)


.. _sphx_glr_download_auto_examples_plot_tutorial_06.py:

.. only:: html

  .. container:: sphx-glr-footer sphx-glr-footer-example

    .. container:: sphx-glr-download sphx-glr-download-jupyter

      :download:`Download Jupyter notebook: plot_tutorial_06.ipynb <plot_tutorial_06.ipynb>`

    .. container:: sphx-glr-download sphx-glr-download-python

      :download:`Download Python source code: plot_tutorial_06.py <plot_tutorial_06.py>`

    .. container:: sphx-glr-download sphx-glr-download-zip

      :download:`Download zipped: plot_tutorial_06.zip <plot_tutorial_06.zip>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
