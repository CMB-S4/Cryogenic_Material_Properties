Fitting Method
==============

The thermal conductivity fits that are produced from raw data are done so by first fitting the low temperature data and the high temperature data separately. Then, the two fits are connected using an error function.

The final fit follows the following structure:


$$ \log_{10}(k) = \log_{10}\left(T\left[aT^N+bT^{N-1}+cT^{N-2}+\ldots\right]\right)*0.5*\left[1-\mathrm{ERF}\left(15*\left(\log_{10}\left(\frac{10T}{\mathrm{erf\_param}}\right)\right)\right)\right]+\left[A\log_{10}(T)^n+B\log_{10}(T)^{n-1}+C\left(\log_{10}(T)\right)^{n-2}+D\left(\log_{10}(T)\right)^{n-3}+\ldots\right]*0.5*\left[1+\mathrm{ERF}\left(15*\left(\log_{10}\left(\frac{T}{\mathrm{erf\_param}}\right)\right)\right)\right]$$

where N, and n are the number of low and high parameters (respectively). 

In python form this fit is as follows:

.. code-block:: python

    low_fit = T*np.polyval(low_param, T)
    hi_fit = 10**np.polyval(hi_param, np.log10(T))

    erf_low = 0.5*(1-erf(15*(np.log10(10*T/erf_param))))
    low_range = np.log10(np.abs(T*(low_fit(T))))
    erf_hi = 0.5*(1+erf(15*(np.log10(T/erf_param))))
    hi_range = (hi_fit(np.log10(T)))

    logk = low_range*erf_low+hi_range*erf_hi

Fit Development and Improvement
```````````````````````````````
Project developers are aware of a particular shortcoming of the above described fit method, notably that it struggles to fit datasets in which there exists a large gap (in temperature) within the data.
We are actively working on a solution to this which involves using an interpolating spline across the data gap. This feature will be pushed to the repository in a future release.

Other Fits
``````````

Occasionally, when access to the raw thermal conductivity measurements is not possible, the thermal conductivity fits themselves will be taken directly from reference literature. There may also be times when the data from a particular material is poorly fit by the above method. In these cases, the fit may be of a different form than the fit described above. To handle this, the files describing the fit parameters will contain a *Fit Type* identification. This ID can serve as a pointer to the included *fit_types.py* file, which describes the different fit types.

Currently, many of the available fits in the repository are taken from work done by Ray Radebaugh and associates at NIST (see. https://trc.nist.gov/cryogenics/materials/materialproperties.htm). Fits from NIST and other external are reported in the *tc_other_fits_* file.

