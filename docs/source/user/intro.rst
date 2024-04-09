General Usage
=============

Most users of this repository will only ever use the *thermal_conductivity_compilation* files, which may then be imported into other programs. These files contain the multi-order fits to real thermal conductivity data. The *compile_TC.py* is responsible for compiling each individual material fit, and exporting the full .csv and .txt files. It is also how the compilation files are updated after changes in the library.

More information on accessing and using this information can be found in the tools documentation.

For users who wish to adjust the fits, add more data, or investigate the 'behind the scenes' of this repository, it is encouraged to familiarize oneself with the documention found in the repository section. 

Ultimately, the output of the code pipeline are a .csv and a .txt file with the thermal conductivity fit parameters for each material. The code also produces plots for each material. 

About Us and Contact
````````

This repository was created in support of the mission of the CMB-S4 collaboration. It is designed primarily with the desires and experiences of researchers in experimental cosmology in mind. However, it is the hope of the developers that this repository can serve as a useful tool for scientists and researchers regardless in a wide range of fields beyond our own. As such, we encourage any user who may wish to contribute their own expertise to get in contact with us to help further develop this repository. 