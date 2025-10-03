
Adding Room Temperature Data
============================

Many materials use a room temperature data point to aid with the interpolation up to room temperature in the cases where sufficient data in that region is not available.

To add a room temperature data point, follow these steps:

#. Navigate to the material folder.
#. If the file titled ``room_temperature.yaml`` does not exist, create it.
#. Within the ``room_temperature.yaml`` file, add the room temperature data in the following format:

.. code-block:: yaml
    room_temperature_conductivity: [<Temperature of Point (near 300K)>, <Conductivity at that Temperature (W/m-K)>]
    room_temperature_reference: <Author(s), Title of Reference, Source>

#. Save the file.
