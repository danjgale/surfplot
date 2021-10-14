surfplot
========

.. image:: https://zenodo.org/badge/380025008.svg
   :target: https://zenodo.org/badge/latestdoi/380025008

``surfplot`` is a flexible and easy-to-use package that makes publication-ready brain surface plots. Users can easily set the plot views and layout, add multiple data layers, draw outlines, and further customize their figure directly using matplotlib. 

.. figure:: https://raw.githubusercontent.com/danjgale/surfplot/main/docs/auto_examples/examples/images/sphx_glr_plot_example_01_001.png
	:target: https://surfplot.readthedocs.io/en/latest/auto_examples/examples/plot_example_01.html#sphx-glr-auto-examples-examples-plot-example-01-py
	:alt: example
	:align: center
	
	Example Neurosynth association maps; see `Example 1`_

At its core, ``surfplot`` is simply a high-level interface to `Brainspace's <https://brainspace.readthedocs.io/en/latest/index.html>`_ excellent surface `plotting <https://brainspace.readthedocs.io/en/latest/python_doc/api_doc/brainspace.plotting.html>`_ and `manipulation <https://brainspace.readthedocs.io/en/latest/python_doc/api_doc/brainspace.mesh.html>`_ capabilities, which are built on top of `Visualization Toolkit (VTK) <https://vtk.org/>`_. Surfaces are rendered with Brainspace and then embedded into a matplotlib figure for easy integration with typical plotting workflows. A big thank you to the ``Brainspace`` developers for making this package possible. 

``surfplot`` is designed around common use-cases for surface plotting and popular surface plotting software (e.g., `Connectome Workbench <https://www.humanconnectome.org/software/connectome-workbench>`_). ``surfplot`` also provides some additional utility functions to streamline the plotting process.

Getting started
---------------

Follow the `Installation Instructions`_ to install ``surfplot``, and then check out the `Tutorials and Examples`_ to learn how to get up and running! Refer to the `API reference`_ for complete documentation. 

Citing surfplot
---------------

Please cite the following if you use ``surfplot``:

Gale, Daniel J., Vos de Wael., Reinder, Benkarim, Oualid, & Bernhardt, Boris. (2021). Surfplot: Publication-ready brain surface figures (v0.1.0). Zenodo. https://doi.org/10.5281/zenodo.5567926

Vos de Wael R, Benkarim O, Paquola C, Lariviere S, Royer J, Tavakol S, Xu T, Hong S-J, Langs G, Valk S, Misic B, Milham M, Margulies D, Smallwood J, Bernhardt BC. 2020. BrainSpace: a toolbox for the analysis of macroscale gradients in neuroimaging and connectomics datasets. *Communications Biology*. 3:103. https://doi.org/10.1038/s42003-020-0794-7

License information
-------------------

This codebase is licensed under the `3-clause BSD license <https://opensource.org/licenses/BSD-3-Clause>`_. The full license can be found in the `LICENSE <https://github.com/danjgale/surfplot/blob/main/LICENSE>`_ file in the ``surfplot`` distribution.

Support
-------

If you encounter problems or bugs with ``surfplot``, or have questions or improvement suggestions, please feel free to get in touch via the `Github issues <https://github.com/danjgale/surfplot/issues>`_.

.. _Example 1: https://surfplot.readthedocs.io/en/latest/auto_examples/examples/plot_example_01.html#sphx-glr-auto-examples-examples-plot-example-01-py
.. _Installation Instructions: https://surfplot.readthedocs.io/en/latest/installation.html
.. _Tutorials and Examples: https://surfplot.readthedocs.io/en/latest/auto_examples/index.html
.. _API reference: https://surfplot.readthedocs.io/en/latest/api.html
