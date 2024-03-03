# Cryogenic_Material_Properties
## Description
Compilation of material properties at cryogenic temperatures for use in design and testing of cryogenic systems.

This Git Repository will serve to store raw thermal conductivity (TC) data and other material properties and analysis tools (in Python) for streamlined use. The data is compiled from decades of published resources. The repository also includes the reference information for each set of measurements. 

The repository is being actively developed by Henry Nachman and Dr. Nicholas Galitzki at the University of Texas at Austin. 

## Operation
Most users of this repository will only ever use the thermal_conductivity_compilation files, which may then be imported into other programs. These files contain the multi-order fits to real thermal conductivity data. The *compile_TC.py* is responsible for compiling each individual material fit, and exporting the full .csv and .txt files.  

For users who wish to adjust the fits, add more data, or investigate the 'behind the scenes' of this repository, it is encouraged to familiarize oneself with the 'thermal_conductivity_tutorial.ipynb' notebook (found in the thermal_conductivity folder) in its entirety.
This notebook produces all of the plots and fits (and puts them in the appropriate folders).

The output of the notebook is a compiled .csv and .txt file with the thermal conductivity fit parameters for each material. 

## Compilation File
The compilation file is of the following structure:
```
| Material Name | Fit Type | Low Temp | High Temp | a        | b       | c       | d       | A       | B        | C       | D        | erf param |
| ---------------------------------------------------------------------------------------------------------------------------------------------- |
| SS304         | loglog   | 0.385    | 1672.000  | -0.00002 | 0.00036 | 0.00049 | 0.07217 | 0.21898 | -1.62951 | 4.42078 | -3.11248 | 20.00000  |
```
Fit Type : defines the structure of the fit - currently there is a single fit type, as defined in the Fitting Method section below.

Low Temp/High Temp : Define the range (low, high) of the fit function in Kelvin (K)

lower case letters : Define the fit parameters for the low temperature fit (a+bT+cT^2+...)

upper case letters : Define the fit parameters for the high temperature fit (A+B*Log10(T)+C*(Log10(T))^2+D*(Log10(T))^3+...)

erf param : Defines the temperature point (in K) at which the error function is positioned

## Fitting Method
The thermal conductivity fits are produced by first fitting the low temperature data and the high temperature data separately. Then, the two fits are connected using an error function.

The final fit follows the following structure:
```
Log10(k) = Log10(T[a+bT+cT^2+...])*0.5*[1-ERF(15*(Log10(10T/erf_param)))]+[A+B*Log10(T)+C*(Log10(T))^2+D*(Log10(T))^3+...]*0.5*[1+ERF(15*(Log10(T/erf_param)))]
```

or in python form
```
    erf_low = 0.5*(1-erf(15*(np.log10(10*T/erf_param))))
    low_range = np.log10(np.abs(T*(low_fit(T))))
    erf_hi = 0.5*(1+erf(15*(np.log10(T/erf_param))))
    hi_range = (hi_fit(np.log10(T)))

    logk = low_range*erf_low+hi_range*erf_hi
    # logk = np.log10(np.abs(T*(low_fit(T))))*0.5*(1-erf(15*(np.log10(10*T/erf_param))))+(hi_fit(np.log10(T)))*0.5*(1+erf(15*(np.log10(T/erf_param))))
```

## Other Fits
Occasionally, when access to the raw thermal conductivity measurements is not possible, the thermal conductivity fits themselves will be taken directly from reference literature. There may also be times when the data from a particular material is poorly fit by the above method. In these cases, the fit may be of a different form than the fit described above. The handle this, the files describing the fit parameters will contain a *Fit Type* identification. This ID can serve as a pointer to the included *fit_types.py* file, which describes the different fit types. 


## Organizational Structure
All current development exists within the 'thermal_conductivity' folder
```
thermal_conductivity
    - thermal_conductivity_tutorial.ipynb
    - lib
        - SS304
            - plot files
            - fit.lh5
            - RAW
                - references.txt
                - measurement1.csv
                - measurement2.csv 
                - ...
        - Other materials eventually
```

## Plotting
Plots for each material can be found within each material subfolder.

## Adding Data ~ for developers only
The code pipeline is designed to be easily scaleable, thus, incorporation of new measurements, or new materials is natively built in.

To do so, follow the outline steps:

1. Make a branch or local copy of this repository
2. Navigate to:
```
~/thermal_conductivity/lib/
```
3. Create a new folder with the same name of the material you wish to add (the name of the folder is crucial as it is also how that material will be referenced).
4. Within that folder create a new folder within which to store the raw data. (I recommend naming it 'RAW', though theoretically, this is not a requirement)
5. Within this 'RAW' folder, paste the relevant measurement .csv files (the data MUST be in csv format otherwise the code will not be able to find it). Each .csv data file must be of the format shown below, see one of the existing materials for more examples. 

| TITLE OF REFERENCE | AUTHORS (separated by non-comma delimiter) | REFERENCE SOURCE |
| --- | --- | --- |
| **T (K)** | **k (W/m-K)** | **k/T** |
|293|14.31482265|0.04885605|
|300|14.42851886|0.048095063|
|320|14.75183857|0.046099496|
|...|...|...|
