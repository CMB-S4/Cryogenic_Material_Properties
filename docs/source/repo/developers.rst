Adding and Manipulating Data
============================

The code pipeline is designed to be easily scaleable, thus, incorporation of new measurements, or new materials is natively built in.

To do so, follow the outline steps:

#. Make a branch or local copy of this repository
#. Navigate to: ``~/thermal_conductivity/lib/``
#. Create a new folder with the same name of the material you wish to add (the name of the folder is crucial as it is also how that material will be referenced).
#. Within that folder create a new folder within which to store the raw data. (I recommend naming it 'RAW', though theoretically, this is not a requirement)
#. Within this 'RAW' folder, paste the relevant measurement .csv files (the data MUST be in csv format otherwise the code will not be able to find it). Each .csv data file must be of the format shown below, see one of the existing materials for more examples. Note, make sure there are no commas present in the reference information otherwise python will be unable to parse the comma delimited file.
#. Once the data is added, the material instance should be updated so that its fit can be recalculated. More information on this can be found on the ``Update`` page.
.. list-table:: Raw Data Table format
   :widths: 25 25 50
   :header-rows: 2

   * - TITLE OF REFERENCE
     - AUTHORS (separated by non-comma delimiter)
     - REFERENCE SOURCE
   * - **T (K)** 
     - **k (W/m-K)**
     - **k/T** 
   * - 293
     - 14.31
     - 0.0488
   * - 300
     - 14.43
     - 0.0481
   * - 320
     - 14.75
     - 0.0461

Adding Fits
============================

Adding a fit (without adding data) is done by adding a ``Fit`` object to the list of fits attributed to a ``Material`` object.

#. Load the material instance (from the corresponding ``.pkl`` file) using the following code.
#. Create a new ``Fit`` object.
#. Append the new ``Fit`` object to the list of fits attributed to the ``Material`` object.
#. Save the updated ``Material`` object back to the ``.pkl`` file.

Adding Room Temperature Data
============================

Many materials use a room temperature data point to aid with the interpolation up to room temperature in the cases where sufficient data in that region is not available.

To add a room temperature data point, follow these steps:

#. Navigate to the material folder.
#. If the file titled ``room_temperature.yaml`` does not exist, create it.
#. Within the ``room_temperature.yaml`` file, add the room temperature data in the following format:
```yaml
room_temperature_conductivity: [<Temperature of Point (near 300K)>, <Conductivity at that Temperature (W/m-K)>]
room_temperature_reference: <Author(s), Title of Reference, Source>
```
#. Save the file.
