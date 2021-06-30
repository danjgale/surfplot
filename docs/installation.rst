
Installation
============

``brainplot`` is installable via ``pip``:

.. code-block:: bash

	pip install brainplot

Alternatively, you can install the most up-to-date version of from GitHub:

.. code-block:: bash

	git clone https://github.com/danjgale/brainplot.git
	cd brainplot
	pip install . 

Note that ``brainplot`` requires Python 3.7+ and some key dependencies:

	- `brainspace`_ (>=0.1.1)
	- `matplotlib`_ (>=3.3.0)
	- `numpy`_ (>=1.16.0)
	- `nibabel`_ (>=3.0.0)
	- `vtk`_ (>=8.1.0)

Several of the :ref:`tutorials` make use of additional neuroimaging packages. Although these packages are not required for installation, they are recommended to make your brainplotting life a bit easier. These are:

	- `nilearn`_ (for manipulating images and volume-to-surface projections)
	- `brainnotation`_ (for volume-to-surface projections and surface-to-surface resampling)


.. _brainspace: https://brainspace.readthedocs.io/en/latest/index.html
.. _matplotlib: https://matplotlib.org/
.. _numpy: https://numpy.org/
.. _nibabel: https://nipy.org/nibabel/
.. _vtk: https://vtk.org/
.. _nilearn: https://nilearn.github.io/index.html
.. _brainnotation: https://netneurolab.github.io/brainnotation/