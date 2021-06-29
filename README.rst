
brainplot: A simple Python package for plotting brain surfaces
==============================================================

.. figure:: _static/example.png
	:scale: 25 %
	:align: center
	:figwidth: 500px

	Multi-layer plot of Default Mode and Frontoparietal network associations from Neurosynth. See `example`_.

``brainplot`` is a flexible and easy-to-use package that makes publication-ready brain surface plots. Users can easily set the views and layout, add multiple data layers, draw outlines, and further customize their figure using matplotlib. 

Notably, ``brainplot`` is built on top of `Brainspace`_ to provide a high-level interface to its *excellent* brain surface plotting capabilities. It is not intended to be a replacement of Brainspace, but rather an extension of its plotting functions.  

Installation
------------

``brainplot`` is installable via ``pip``:

.. code-block:: bash

	pip install brainplot

Alternatively, you can install the most up-to-date version of from GitHub:

.. code-block:: bash

	git clone https://github.com/danjgale/brainplot.git
	cd brainplot
	pip install . 

Note that ``brainplot`` requires Python 3.6+ and some key dependencies:
	- numpy (>=1.16.0)
	- matplotlib (>=3.3.0)
	- nibabel (>=3.0.0)
	- brainspace (>=0.1.1)
	- vtk (>=8.1.0)

Several of the tutorials make use of additional neuroimaging packages. Although these packages are not required for installation, they are recommended to make your brainplotting life a bit easier. These are:

	- `nilearn`_ (>=0.7.0; for manipulating images and volume-to-surface projections)
	- `brainnotation`_ (for volume-to-surface projections and surface-to-surface resampling). 

Usage
-----


Contributing
------------

.. _example: 
.. _Brainspace: https://brainspace.readthedocs.io/en/latest/index.html
.. _nilearn: https://nilearn.github.io/index.html
.. _brainnotation: https://netneurolab.github.io/brainnotation/