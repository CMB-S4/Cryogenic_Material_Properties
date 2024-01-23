# Cryogenic_Material_Properties
Compilation of material properties at cryogenic temperatures for use in design and testing of cryogenic systems.

This Git Repository will serve to store the RAW thermal conductivity and other material properties data, compiled from decades of published resources, and analysis tools (in Python) for streamlined use and analysis.

The repository is being actively developed by Dr. Nicholas Galitzki and graduate students at the University of Texas. 

## Organizational Structure
All current development exits within the 'thermal_conductivity' folder
```
thermal_conductivity
    - lib
        - SS304
            - SS304.pdf
            - fitPlot.pdf
            - SS304.yaml
            - RAW
                - measurement1.csv
                - measurement2.csv ...
        - Other materials eventually
    - GOAL_TXT.txt
```
The basic operating procedure is to run the 'thermal_conductivity_tutorial.ipynb' notebook in its entirety.
This notebook produces all of the plots and fits (and puts them in the appropriate folders)

GOAL: produce one big txt file within the thermal conductivity folder which has the fit parameters for each material.