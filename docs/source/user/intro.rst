General Usage
=============

Most users of this repository will only ever use the thermal_conductivity_compilation files, which may then be imported into other programs. These files contain the multi-order fits to real thermal conductivity data. The *compile_TC.py* is responsible for compiling each individual material fit, and exporting the full .csv and .txt files. It is also how the compilation files are updated after changes in the library.

More information on accessing and using this information can be found in the tools documentation.

For users who wish to adjust the fits, add more data, or investigate the 'behind the scenes' of this repository, it is encouraged to familiarize oneself with the documention found in the repository section. 

Ultimately, the output of the code pipeline are a .csv and a .txt file with the thermal conductivity fit parameters for each material. The code also produces plots for each material. 