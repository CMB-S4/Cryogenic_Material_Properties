Importing Fits
==============

Python
``````
To import the compilation files in Python

.. code-block:: python

    import numpy as np
    TC_data = np.loadtxt("tc_compilation_<date>.csv", dtype=str, delimiter=',')

    headers = TC_data[0]
    material_names = TC_data[:,0]

The file name of the compilation file includes the date of last edit. Therefore, one must either manually add the appropriate date or use code to pull the most recent compilation file. 

Additionally, a variety of useful functions have been added as methods of the ``Material`` and ``Fits`` classes.

Excel
`````
To import the compiled thermal conductivity data into Excel, one should download and open the relevant *tc_compilation_<date>.csv* and simply copy and paste the entire contents of the file into an Excel sheet (or use the Excel data import tool).