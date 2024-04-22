Compilation File
==============

The compilation file is of the following structure::

    | Material Name             | Fit Type             | Low Temp             | High Temp             | Perc Err             | a             | b             | c             | d             | e             | f             | g             | h             | i             | erf param             | A             | B             | C             | D             |
    | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | SS304                     | loglog               | 0.385                | 1672.000              | 3.953                | 2.23367e-07   | -5.04296e-05  | 3.01386e-03   | 6.96502e-02   | ^             | ^             | ^             | ^             | ^             | 1.19786e+02           | 3.42081e-02   | -1.71132e-01  | 6.23536e-01   | 1.49213e-01   | 


Fit Type : Defines the structure of the fit depending on the source of the fit parameters.

Low Temp/High Temp : Define the range (low, high) of the fit function in Kelvin (K)

Perc Err: Defines the average percent error of the fit, as reported by the fit source, or the fitting algorithm.

lower case letters : Define the fit parameters for the low temperature fit ``(a+bT+cT^2+...)``

upper case letters : Define the fit parameters for the high temperature fit ``(A+B*Log10(T)+C*(Log10(T))^2+D*(Log10(T))^3+...)``

erf param : Defines the temperature point (in K) at which the error function is positioned