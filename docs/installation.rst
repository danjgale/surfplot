
Installation
============

``surfplot`` is installable via ``pip``:

.. code-block:: bash

	pip install surfplot

Alternatively, you can install the most up-to-date version of from GitHub:

.. code-block:: bash

	git clone https://github.com/danjgale/surfplot.git
	cd surfplot
	pip install . 

Note that ``surfplot`` requires Python 3.7+ and some key dependencies:

	- `brainspace`_ (>=0.1.1)
	- `matplotlib`_ (>=3.3.0)
	- `numpy`_ (>=1.16.0)
	- `nibabel`_ (>=3.0.0)
	- `vtk`_ (>=8.1.0)

Several of the :ref:`tutorials_examples` make use of additional neuroimaging packages. Although these packages are not required for installation, they are recommended to make your surfplotting life a bit easier. These are:

	- `nilearn`_ (for manipulating images and volume-to-surface projections)
	- `neuromaps`_ (for volume-to-surface projections and surface-to-surface resampling)


.. _brainspace: https://brainspace.readthedocs.io/en/latest/index.html
.. _matplotlib: https://matplotlib.org/
.. _numpy: https://numpy.org/
.. _nibabel: https://nipy.org/nibabel/
.. _vtk: https://vtk.org/
.. _nilearn: https://nilearn.github.io/index.html
.. _neuromaps: https://netneurolab.github.io/neuromaps/