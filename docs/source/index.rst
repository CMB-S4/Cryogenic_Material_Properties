.. Cryogenic Materials Repository documentation master file, created by
   sphinx-quickstart on Mon Apr  8 16:36:15 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cryogenic Materials Repository
==============================
Welcome to the Cryogenic Materials Repository (CMR) documentation!

The CMR is a compilation of material properties at cryogenic temperatures for use in design and testing of cryogenic systems.

This Git Repository will serve to store raw thermal conductivity (TC) data and other material properties and analysis tools (in Python) for streamlined use. The data is compiled from decades of published resources. The repository also includes the reference information for each set of measurements. 

The repository is being actively developed by Henry Nachman, Oorie Desai, and Dr. Nicholas Galitzki at the University of Texas at Austin. 

For more detailed information on all of the features of the repository, please explore the extended documentation below.

.. toctree::
   :maxdepth: 3
   :caption: About:

   user/overview
   user/starting
   repo/repo_structure
   repo/fitting
   repo/compfile

.. toctree::
   :maxdepth: 3
   :caption: Repository Documentation:
   
   repo/mat_class
   
.. toctree::
   :maxdepth: 3
   :caption: Tools and Tutorials:

   tools/tutorial
   tools/importing
   repo/adding_data
   repo/adding_fits
   repo/adding_rt
   tools/thermalmodel

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
