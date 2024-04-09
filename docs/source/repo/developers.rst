Adding and Manipulating Data
============================

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
