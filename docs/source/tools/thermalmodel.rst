Thermal Modelling
=================

Excel Thermal Model Notebooks:

 One of the major motivating use cases for this repository is as a necessary library of fits for building thermal models of cryogenic systems.
 The repository includes a barebones version of a thermal model written in Excel, as well as a publicly released example of a thermal model from the Simons Observatory. 
 Such Excel models use the output *tc_fullrepo_<date>.py* files as the source of the material thermal conductivity fits necessary for calculating the integrated thermal conductivity of system components, and ultimately the required cooling power. 
 It should be noted that the Excel models make use of Excel Macros written in Microsoft's Visual Basic for Applications (VBA). The developers recognize that VBA may not be the coding language of preference for many users, however, the benefits reaped from using a visual software such as Excel were deemed to outweigh the downsides. 
 Regardless, the models are designed such that in theory, the VBA needs never be changed. Due note, because the provided Excel notebooks use Macros, the document will need to be *trusted* and have macros enables before the notebook will work.

Python Thermal Model:

 Due to the difficulties of using the Excel model, development of an entirely Python model with an easy to use GUI is also in the works. Currently, the GUI allows for easy addition of components which can then be saved to a .json file and parsed via python code.