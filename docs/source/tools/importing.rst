Importing Fits
==============

Python
``````
To import the compilation files in Python

.. code-block:: python

    import numpy as np
    TC_data = np.loadtxt("thermal_conductivity_compilation.csv", dtype=str, delimiter=',')

    headers = TC_data[0]
    material_names = TC_data[:,0]

Excel
`````

To import the compiled thermal conductivity data into Excel, one should download and open the *thermal_conductivity_compilation.csv* and simply copy, and paste the entire contents of the file into an Excel sheet.