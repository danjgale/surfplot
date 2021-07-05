
brainplot: A Python package for plotting brain surfaces
=======================================================

.. figure:: https://raw.githubusercontent.com/danjgale/brainplot/main/docs/auto_examples/examples/images/sphx_glr_plot_example_01_001.png
	:target: https://brainplot.readthedocs.io/en/latest/auto_examples/examples/plot_example_01.html#sphx-glr-auto-examples-examples-plot-example-01-py
	:alt: example
	:align: center
	
	Example Neurosynth association maps; see `Example 01`_

``brainplot`` is a flexible and easy-to-use package that makes publication-ready brain surface plots. Users can easily set the plot views and layout, add multiple data layers, draw outlines, and further customize their figure directly using matplotlib. 

At its core, ``brainplot`` is simply a high-level interface to `Brainspace's <https://brainspace.readthedocs.io/en/latest/index.html>`_ excellent surface `plotting <https://brainspace.readthedocs.io/en/latest/python_doc/api_doc/brainspace.plotting.html>`_ and `manipulation <https://brainspace.readthedocs.io/en/latest/python_doc/api_doc/brainspace.mesh.html>`_ capabilities, which are built on top of `Visualization Toolkit (VTK) <https://vtk.org/>`_. ``brainplot`` is designed around common use-cases for surface plotting and popular surface plotting software (e.g., `Connectome Workbench <https://www.humanconnectome.org/software/connectome-workbench>`_). ``brainplot`` also provides some additional utility functions to streamline the plotting process.

Getting started
---------------

Follow the `installation instructions`_ to install ``brainplot``, and then check out the `tutorials and examples`_ to learn how to get up and running! Refer to the `API reference`_ for complete documentation. 


License information
-------------------

This codebase is licensed under the `3-clause BSD license <https://opensource.org/licenses/BSD-3-Clause>`_. The full license can be found in the `LICENSE <https://github.com/danjgale/brainplot/blob/main/LICENSE>`_ file in the ``brainplot`` distribution.

Support
-------

If you encounter problems or bugs with ``brainplot``, or have questions or improvement suggestions, please feel free to get in touch via the `Github issues <https://github.com/danjgale/brainplot/issues>`_.

Acknowledgements
----------------

A big thank you to the ``Brainspace`` developers:

Vos de Wael R, Benkarim O, Paquola C, Lariviere S, Royer J, Tavakol S, Xu T, Hong S-J, Langs G, Valk S, Misic B, Milham M, Margulies D, Smallwood J, Bernhardt BC. 2020. BrainSpace: a toolbox for the analysis of macroscale gradients in neuroimaging and connectomics datasets. *Communications Biology*. 3:103.

.. _Example 01: https://brainplot.readthedocs.io/en/latest/auto_examples/examples/plot_example_01.html#sphx-glr-auto-examples-examples-plot-example-01-py
.. _installation instructions: https://brainplot.readthedocs.io/en/latest/installation.html
.. _tutorials and examples: https://brainplot.readthedocs.io/en/latest/auto_examples/index.html
.. _API reference: https://brainplot.readthedocs.io/en/latest/api.html