## Author: Henry Nachman
import numpy as np
from scipy.special import erf


######################################################################
def koT_function(T, koT, orders, weights):
    low_fit_xs = np.linspace(np.min(T), np.max(T), 100)
    lofit_full = np.polyfit(T, koT, orders, full=True, w=weights)
    low_fit, residuals_lo, rank_lo, sing_vals_lo, rcond_lo = lofit_full
    low_poly1d = np.poly1d(low_fit)
    return low_fit_xs, low_fit

def logk_function(logT, logk, orders, weights):
    fit_T = np.linspace(np.min(logT), np.max(logT), 100)
    fit_full = np.polyfit(logT, logk, orders, full=True, w=weights)
    fit, residuals_hi, rank_hi, sing_vals_hi, rcond_hi =  fit_full
    # hi_poly1d = np.poly1d(fit)
    return fit_T, fit

def loglog_func(T, low_param, hi_param, erf_param):
    """
    Description : Takes a temperature (or temp array) and fit arguments returns the estimated k value.

    Arguments : 
    - T - temperature at which to estimate the thermal conductivity.
    """
    low_fit = T*np.polyval(low_param, T)
    hi_fit = 10**np.polyval(hi_param, np.log10(T))

    if erf_param==0:
        erf_hi = 0
        erf_low = 1
    elif erf_param==-1:
        erf_low = 0
        erf_hi = 1
    else:
        erf_low = 0.5*(1-erf(15*(np.log10((T)/erf_param))))
        erf_hi = 0.5*(1+erf(15*(np.log10(T/erf_param))))

    k = low_fit*erf_low+hi_fit*erf_hi

    return k

######################################################################

def power_law(T, params):
    A, B = params

    k = (A*(10**(-3)))*T**(B)

    return k