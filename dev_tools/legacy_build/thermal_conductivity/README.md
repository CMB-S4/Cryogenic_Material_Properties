Within this folder you will find the code needed to fit data, and compile the thermal conductivity data. 

Generally, the scripts make use of the argparse package for command line execution. The run commands are listed below. 

To fit raw thermal conductivity data:
```
python fit_data.py --matlist <None> --plot <True>
```
--matlist takes a list of materials to fit. Add material names sequentially with space delimiters and no brackets (with quotes). Material names should match material folder exactly. When left empty, the script defaults to fitting all materials in the repository containing RAW data.

To see the different fit types:
```
fit_types.py
```

To manually add a fit from an external source:
```
manual_add.ipynb
```

<!-- To scrape thermal conductivity fits from the NIST website (Note this should not need to be run unless the NIST website has been recently updated):
```
NIST_scrape.py
``` -->

<!-- To make plots of all the materials:
```
material_plots.py
``` -->

To update the plots and parent material folders:
```
ptyhon update_repo.py
```