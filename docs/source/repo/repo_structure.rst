Repository Structure
====================

Upon navigating to the repository website on GitHub you will be met with eight compilation files as well as subdirectories leading to the behind the scenes code for the repository and more.

The primary output of this repository are files containing a compilation of the available material property fits.

The *ThermalModelTools* folder contains example thermal models showing how this repository can be used in a scientific application.

All of the backend code and material library is contained in the *thermal_conductivity* folder.

Stepping into the *thermal_conductivity* folder, you will be met with all of the python and Jupyter notebooks used in the creation of the structure and fits of the repository.

The actual library of material data is housed in the *lib* folder.

Here is an example material folder. At the root level, this folder contains a config.yaml file used to identify any material 'parents'. Within the subfolders you will find the files describing the produced fit, plots of the fits, and other fits created either by NIST (if applicable) or other sources. If the material has raw data it will be stored within the *RAW* directory where each dataset is saved as a .csv file. You will also find the data references within this folder. 

.. image:: images/SS304_home.png


All current development exists within the 'thermal_conductivity' folder

* tc_fullrepo_date.csv
* ttc_fullrepo_date.txt
* compile_TC.py

  * thermal_conductivity

    * fit_data.py
    * fit_types.py
    * manual_add.ipynb
    * NIST_scrape.py
    * lib
      * <Material Name>
        * fits
        * NIST
        * OTHER
        * plots
        * RAW