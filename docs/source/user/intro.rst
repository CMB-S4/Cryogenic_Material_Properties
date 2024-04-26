General Usage
=============

Most users of this repository will only ever use the *thermal_conductivity_compilation* files, which may then be imported into other programs. These files contain the multi-order fits to real thermal conductivity data. The *compile_TC.py* is responsible for compiling each individual material fit, and exporting the full .csv and .txt files. It is also how the compilation files are updated after changes in the library.

More information on accessing and using this information can be found in the tools documentation.

For users who wish to adjust the fits, add more data, or investigate the 'behind the scenes' of this repository, it is encouraged to familiarize oneself with the documention found in the repository section. 

Ultimately, the output of the code pipeline are a .csv and a .txt file with the thermal conductivity fit parameters for each material. The code also produces plots for each material. 

Goals and Motivation
````````````````````
- **Data:** Compile and house a repository of cryogenic material data (beginning with thermal conductivity and eventually expanding to other desired properties)
- **Fitting:** Develop a method of fitting data to produce high quality, adaptable fits which can be used for calculations and store fits created by others for materials for which raw data is not available
- **Transparency:** Produce a transparent database that saves references to data and clearly shows and explains how fits are procured
- **Tools:** Provide example tools demonstrating the operation of the pipeline output in scientific applications
- **Versatility:** Develop a pipeline that can be easily updated by users as new data is added, or changed depending on specific scientific goals.



About Us and Contact
````````

This repository was created in support of the mission of the CMB-S4 collaboration. It is designed primarily with the desires and experiences of researchers in experimental cosmology in mind. However, it is the hope of the developers that this repository can serve as a useful tool for scientists and researchers in a wide range of fields beyond our own. As such, we encourage any user who may wish to contribute their own expertise to get in contact with us to help further develop this repository. 