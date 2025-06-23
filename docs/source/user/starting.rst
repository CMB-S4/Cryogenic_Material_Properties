Getting Started
===============

Navigating the repository
--------------------

Most users of this repository will only ever use the thermal conductivity compilation files, which may then be imported into other programs. These files contain the multi-order fits to real thermal conductivity data. The *compile_TC.py* is responsible for compiling each individual material fit, and exporting the full .csv and .txt files. It is also how the compilation files are updated after changes in the library.

More information on accessing and using this information can be found in the tools documentation.

For users who wish to adjust the fits, add more data, or investigate the 'behind the scenes' of this repository, it is encouraged to familiarize oneself with the documention found in the repository section. 

Ultimately, the output of the code pipeline are a .csv and a .txt file with the thermal conductivity fit parameters for each material. The code also produces plots for each material. 



For those who wish to update the compilation files, add local data, or manipulate the fits and code in any way, it is recommended to make a clone of this repository.

Currently, the amount of raw data and fit plots is sufficiently low to keep the total storage size of the repository to a reasonable download size. There is work being done to eliminate the need to download all the raw data as the repository expands in size and scope.

Updating the repository
========================

To update the repository with new fits, update appropriate parent materials, and create the appropriate plots, it should suffice to run the following python script from the command line:
``python thermal_conductivity\update_repo.py``

To update the compilation files, run the following script:
``python compile_TC.py``