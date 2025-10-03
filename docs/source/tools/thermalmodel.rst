Thermal Modeling:
=================
Excel Thermal Model:
```````````````````````

One of the major motivating use cases for this repository is as a necessary library of fits for building thermal models of cryogenic systems.
The repository includes a barebones version of a thermal model written in Excel, as well as a publicly released example of a thermal model from the Simons Observatory. 
Such Excel models use the output *tc_fullrepo_<date>.py* files as the source of the material thermal conductivity fits necessary for calculating the integrated thermal conductivity of system components, and ultimately the required cooling power. 
It should be noted that the Excel models make use of Excel Macros written in Microsoft's Visual Basic for Applications (VBA). The developers recognize that VBA may not be the coding language of preference for many users, however, the benefits reaped from using a visual software such as Excel were deemed to outweigh the downsides. 
Regardless, the models are designed such that in theory, the VBA needs never be changed. Due note, because the provided Excel notebooks use Macros, the document will need to be *trusted* and have macros enables before the notebook will work.

Python Thermal Model:
`````````````````````

Due to the difficulties of using the Excel model, a Python GUI version of the thermal model was developped. The GUI is built on the Streamlit framework. To run it, you must first install the required packages. The easiest way to do this is to use the provided `requirements.txt` file. You can install the required packages by running:

`pip install -r requirements.txt`

Once the packages are installed, you can run the thermal model by executing the following command in your terminal:

`streamlit run <path_to_PythonThermalModel>thermal_model_gui.py`

More information about the Python Thermal Model can be found in the documentation for the standalone Python Thermal Model repository:
https://github.com/henry-e-n/python_thermal_model.git
