.. Cryogenic Materials Repository documentation master file, created by
   sphinx-quickstart on Mon Apr  8 16:36:15 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cryogenic Materials Repository
==============================

Compilation of material properties at cryogenic temperatures for use in design and testing of cryogenic systems.

This Git Repository will serve to store raw thermal conductivity (TC) data and other material properties and analysis tools (in Python) for streamlined use. The data is compiled from decades of published resources. The repository also includes the reference information for each set of measurements. 

The repository is being actively developed by Henry Nachman, Oorie Desai, and Dr. Nicholas Galitzki at the University of Texas at Austin. 

.. toctree::
   :maxdepth: 3
   :caption: User Guide:

   user/intro
   user/starting

.. toctree::
   :maxdepth: 3
   :caption: Repository Documentation

   repo/structure
   repo/fitting
   repo/compfile
   repo/developers
   
.. toctree::
   :maxdepth: 3
   :caption: Tools

   tools/importing
   tools/thermalmodel

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
