Fitting Method
==============

The thermal conductivity fits that are produced from raw data are done so by first fitting the low temperature data and the high temperature data separately. Then, the two fits are connected using an error function.

The final fit follows the following structure:


``
Log10(k) = Log10(T[a+bT+cT^2+...])*0.5*[1-ERF(15*(Log10(10T/erf_param)))]+[A+B*Log10(T)+C*(Log10(T))^2+D*(Log10(T))^3+...]*0.5*[1+ERF(15*(Log10(T/erf_param)))]
``

or in python form

.. code-block:: python

    erf_low = 0.5*(1-erf(15*(np.log10(10*T/erf_param))))
    low_range = np.log10(np.abs(T*(low_fit(T))))
    erf_hi = 0.5*(1+erf(15*(np.log10(T/erf_param))))
    hi_range = (hi_fit(np.log10(T)))

    logk = low_range*erf_low+hi_range*erf_hi

Other Fits
==========

Occasionally, when access to the raw thermal conductivity measurements is not possible, the thermal conductivity fits themselves will be taken directly from reference literature. There may also be times when the data from a particular material is poorly fit by the above method. In these cases, the fit may be of a different form than the fit described above. To handle this, the files describing the fit parameters will contain a *Fit Type* identification. This ID can serve as a pointer to the included *fit_types.py* file, which describes the different fit types. 

Currently, many of the available fits in the repository are taken from work done by Ray Radebaugh and associates at NIST (see. https://trc.nist.gov/cryogenics/materials/materialproperties.htm). These fits are identified with a NIST fit ID.

