# Cryogenic_Material_Properties
## Description
**A compilation of material properties, fits, and plots at cryogenic temperatures for use in design and testing of cryogenic systems.**

## Last Updated: 04 June 2025

This Git Repository will serve to store raw thermal conductivity (TC) data and other material properties, plots, and analysis tools. The data is compiled from decades of published resources. The repository also includes the reference information for each set of measurements. 

The repository is being actively developed by Henry Nachman, Oorie Desai, and Dr. Nicholas Galitzki at the University of Texas at Austin.

If you have questions/feedback, or wish to contribute please contact:
Henry Nachman: henry.nachman@utexas.edu

## Compilation Files
`tc_fullrepo_`: An extensive compilation of one fit for every material included in the repository. By default, the fit included is the in-house fit to raw data. If no raw data exists in the repo, another fit is reported. 

`tc_simplified_`: A simplified compilation file with a curated list of materials and fits. Includes *flagged* materials, whose fits are known to be problematic.

Any a fit is added to the repo, these compilation files should be reconstructed. To do this, run the compile_TC.py file in your python environment:
```
python compile_TC.py
```

<!-- `tc_other_fits`: Fits extracted directly from other sources (not produced 'in-house'). These fits may follow a different fit type. This file currently has many more fits than the raw data file because many sources report/publish only their fit.

`tc_rawdata_fits`: The fits produced from temperature + thermal conductivity data that has been accumulated from a variety of sources. More information on the fitting method can be found in the documentation. -->


## Documentation

Please navigate to our Read The Docs for a full description of the repository and more.

https://cryogenic-material-properties.readthedocs.io/en/latest/


## Tools

Some useful Python and Excel tools can also be found in this repository for the everyday user. These are found in the `ThermalModelTools` folder.

## Site Map

![image](https://github.com/user-attachments/assets/95638dfd-af29-4a12-9c2c-8549a2ef0bbb)
