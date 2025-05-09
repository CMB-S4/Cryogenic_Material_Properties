## Author: Henry Nachman


"""
This file contains the functions that are used to fit the thermal conductivity data.
Some words are said about each functions here - a more detailed account can be found in the documentation.

Each function generally has the following arguments:
- T - temperature or array of temperatures at which to estimate the thermal conductivity.
- param_dictionary - dictionary containing the parameters for the polynomial fit.

This is the most general fit format.
Some special functions have their own arguments.


"""
import numpy as np
from scipy.special import erf


def get_func_type(key):
    fit_type_dict = {"polylog":         polylog,
                     "3 order polylog": polylog,
                     "Nppoly":          Nppoly,
                     "loglog":          loglog_func,
                     "comppoly":        loglog_func,
                     "TchebyLnT":       NIST5a_3,
                     "NIST-copperfit":  NIST5a_2,
                     "lowTextrapolate": lowTextrapolate,
                     "NIST-experf":     NIST_experf,
                     "powerlaw":       power_law,
                     "OFHC_RRR_Wc":     OFHC_RRR_Wc,
                     "RRadebaugh_koT": RRadebaugh_koT,
                     "RRadebaugh_logkexp": RRadebaugh_logkexp}
    return fit_type_dict[key]

######################################################################
# The following functions are actively used to fit the data.
# These functions are also those found in the compilation files.
######################################################################
def koT_function(T, koT, orders, weights):
    """
    Description : Fits a polynomial to the T vs k/T data.
    Arguments :
    - T - temperature at which to estimate the thermal conductivity.
    - koT - k/T data to fit.
    - orders - order of the polynomial to fit.
    """
    low_fit_xs = np.linspace(np.min(T), np.max(T), 100)
    lofit_full = np.polyfit(T, koT, orders, full=True, w=weights)
    low_fit, residuals_lo, rank_lo, sing_vals_lo, rcond_lo = lofit_full
    low_poly1d = np.poly1d(low_fit)
    return low_fit_xs, low_fit

def logk_function(logT, logk, orders, weights):
    """
    Description : Fits a polynomial to the logT vs logk data.
    Arguments :
    - logT - log10(T) data to fit.
    - logk - log10(k) data to fit.
    - orders - order of the polynomial to fit.
    """
    fit_T = np.linspace(np.min(logT), np.max(logT), 100)
    fit_full = np.polyfit(logT, logk, orders, full=True, w=weights)
    fit, residuals_hi, rank_hi, sing_vals_hi, rcond_hi =  fit_full
    # hi_poly1d = np.poly1d(fit)
    return fit_T, fit

def Nppoly(T, param_dictionary):
    """
    Description : Fits the data in a linear space with a polynomial + 1 order
    Description : k = T*polynomial(T)
                : k = T*(a + bT + cT**2 ...)
    Arguments :
    - T - temperature(s) at which to estimate the thermal conductivity.
    - param_dictionary - dictionary containing the parameters for the polynomial fit.
    """
    param = param_dictionary["low_param"]
    return T*np.polyval(param, T)

def polylog(T, param_dictionary):
    """
    Description : Fits the data in a log10 space 
    Description : Fit Type k = 10**polynomial(log10(T)) (or) k = 10*(a + b*log10(T) + c*log10(T)**2 ...)
    
    Arguments :
    - T - temperature(s) at which to estimate the thermal conductivity.
    - param_dictionary - dictionary containing the parameters for the polynomial fit.
    """
    if len(param_dictionary["hi_param"])!=0:
        param = param_dictionary["hi_param"]
    else:
        param = param_dictionary["low_param"]
    return 10**np.polyval(param, np.log10(T))

def loglog_func(T, param_dictionary, erf_multiplicity=15): #**kwargs
    """
    Description : Fits the data to a compound fit and joins them with an error function.
    Description : Fits the low temp data with the Nppoly function and the high temp data with the polylog function.

    Arguments : 
    - T - temperature at which to estimate the thermal conductivity.
    - low_param: in form a + bT + cT**2 ...
    
    Make sure to remove trailing zeros 
    """
    low_param = param_dictionary["low_param"]
    hi_param  = param_dictionary["hi_param"]
    erf_param = param_dictionary["erf_param"]

    low_param = low_param[::-1] ################################### 20240531
    hi_param = hi_param[::-1] ################################### 20240531
    low_fit = Nppoly(T, param_dictionary)
    hi_fit = polylog(T, param_dictionary)
    
    if erf_param==0:
        erf_hi = 0
        erf_low = 1
    elif erf_param==-1:
        erf_low = 0
        erf_hi = 1
    else:
        erf_low = 0.5*(1-erf(erf_multiplicity*(np.log10((T)/erf_param))))
        erf_hi = 0.5*(1+erf(erf_multiplicity*(np.log10(T/erf_param))))

    k = low_fit*erf_low+hi_fit*erf_hi

    return k

def power_law(T, param_dictionary):
    """
    Description : Fits to a power law function.
    Description : k = A*T^B (or) k = A*T**B
    
    Arguments : 
    - T - temperature at which to estimate the thermal conductivity.
    - low_param: in form a + bT + cT**2 ...
    
    """
    params = param_dictionary["low_param"]
    A, B = params

    k = (A)*T**(B)

    return k

def NIST_experf(T, param_dictionary):
    """
    Description : A 6 parameter fit to data containing exponential and error function terms. Taken from the NIST website.

    Arguments :
    - T - temperature at which to estimate the thermal conductivity.
    - param_dictionary - dictionary containing the parameters for the polynomial fit.
    """
    params = param_dictionary["low_param"]
    logT = np.log10(T)
    a, b, c, d, e, f = params[0], params[1], params[2], params[3], params[4], params[5]
    k_val = (a + b*logT)*((1-erf(2*(logT-c)))/(2))+(d+e*(np.exp(-1*logT/f)))*((1+erf(2*(logT-c)))/(2))
    k = 10**k_val
    return k

# New OFHC fit from Ray Radebaugh - Designed to fit any OFHC copper given a RRR value
def OFHC_RRR_Wc(T,RRR_list,param):
    """
    Description : A complex fit developed by Ray Radebaugh to fit the thermal conductivity of OFHC copper.
    Arguments :
    - T - temperature at which to estimate the thermal conductivity.
    - RRR_list - list of RRR values to fit the data to.
    - param - dictionary containing the parameters for the polynomial fit.
    """
    t = T
    RRR = RRR_list[0]
    params = param["low_param"]
    def w_0(t,RRR,params):
        return (params[0]/((RRR-1)*t))
    def w_c(t,param):
        return (params[9]*np.log(t/params[10])*np.exp(-((np.log(t/params[11])/params[12])**2)) + params[13]*np.log(t/params[14])*np.exp(-((np.log(t/params[15])/params[16])**2)) + params[17]*np.log(t/params[18])*np.exp(-((np.log(t/params[19])/params[20])**2)))
    def w_i_with_w_c(t,params,w_c):
        q = params[1]*(t**params[2])
        r = params[1]*params[3]*(t**(params[2]+params[4]))*np.exp(-((params[5]/t)**params[6]))
        s = 1+r
        p = q/s
        return (p + w_c)
    def w_i0(RRR,w_i,w_0):
        return ((params[7]*((RRR-1)**params[8])*w_i*w_0)/(w_i+w_0))
    w_0 = w_0(t,RRR,params)
    w_c = w_c(t,params)
    w_i = w_i_with_w_c(t,params,w_c)
    w_i0 = w_i0(RRR,w_i,w_0)
    return (1/(w_0+w_i+w_i0))

##################################################################
# The following functions were taken from an existing Excel spreadsheet.
# containing some useful fits to data. 
# While these functions have largely been replaced by the functions above, they are still included here for completeness.
##################################################################
def NIST5a_2(T, param_dictionary):
    params = param_dictionary["low_param"]
    if len(params)<=8:
        params = np.append(params, [0])
    k = params[0] + params[2] * T ** (0.5) + params[4] * T + params[6] * T ** (1.5) + params[8] * T ** (2)
    k = k / (1 + params[1] * T ** (0.5) + params[3] * T + params[5] * T ** (1.5) + params[7] * T ** (2))
    k = 10 ** k
    return k
"""
Case 2  'NIST formulation for OFHC Copper
    Conductivity = IParameters(1) + IParameters(3) * temp ^ (0.5) + IParameters(5) * temp + IParameters(7) * temp ^ (1.5) + IParameters(9) * temp ^ (2#)
    Conductivity = Conductivity / (1 + IParameters(2) * temp ^ (0.5) + IParameters(4) * temp + IParameters(6) * temp ^ (1.5) + IParameters(8) * temp ^ (2#))
    Conductivity = 10 ^ Conductivity

"""

def NIST5a_3(T, param_dictionary):
    params = param_dictionary["low_param"]
    lnT = np.log(T)
    x = ((lnT - params[1]) - (params[2] - lnT)) / (params[2] - params[1])
    k = 0
    for i in range(3,3+int(params[0])):
        k = k + params[i] * np.cos((i - 3) * np.arccos(x))
    k = np.exp(k)
    return k
"""
Case 3  'Tcheby polynomial in ln(T) giving ln(g), a=# parameters, b=low temp, c= high temp, d...=parameters
    x = Log(temp) / Log(2.71828)
    x = ((x - IParameters(2)) - (IParameters(3) - x)) / (IParameters(3) - IParameters(2))
    For I = 4 To 3 + IParameters(1)
        Conductivity = Conductivity + IParameters(I) * Cos((I - 4) * Application.WorksheetFunction.Acos(x))
    Next I
    Conductivity = 2.71828 ^ Conductivity
    
"""
def lowTextrapolate(T, param_dictionary):
    params = param_dictionary["low_param"]
    k = []
    
    if np.size(T) == 1:
        k_plus = 0
        if T > params[0]:
            logtemp = np.log10(T)
            for n in range(1, len(params)):
                k_plus += params[n - 1] * logtemp ** (n - 1)
            k = np.append(k, 10 ** (k_plus))
        elif T > params[1]:
            k = np.append(k, params[3] * T ** params[2])
        else:
            # k = params[16] * T ** params[15]
            k = np.append(k, -1*T)
        k = float(k)
    else:
        for i in range(len(T)):
            k_plus = 0
            if T[i] > params[0]:
                logtemp = np.log10(T[i])
                for n in range(1, len(params)):
                    k_plus += params[n - 1] * logtemp ** (n - 1)
                k = np.append(k, 10 ** (k_plus))
            elif T[i] > params[1]:
                k = np.append(k, params[3] * T[i] ** params[2])
            else:
                # k = params[16] * T ** params[15]
                k = np.append(k, -1*T[i])
    return k

"""
Case 4 'Extrapolation to lower temp, either by using a*T^1.8, or better with data
    'column j:temp to start transition
    'column k:temp to end transition
    'column l:power
    'column m:coefficient
    'column n:estimate of lower validity
    'column o:power
    'column p:coefficient
       
    
    If (temp > IParameters(10)) Then
        logtemp = Log(temp) / Log(10#)
        For I = 1 To 9
            Conductivity = Conductivity + IParameters(I) * logtemp ^ (I - 1)
        Next I
        Conductivity = 10 ^ Conductivity
    ElseIf (temp > IParameters(11)) Then
        Conductivity = IParameters(13) * temp ^ IParameters(12)
    Else
        Conductivity = IParameters(16) * temp ^ IParameters(15)
    End If
    
"""

#################################################################
# All of the remaining functions were taken from the NIST website or previous
# versions of fit compilation files. They are not actively used, but are included here for completeness.
#################################################################
# From the NIST website

def NIST1(T, params):
    """
    Description : k = T*polynomial(log10(T))
                : k = T*(a + b*log10(T) + c*log10(T)**2 ...)
    """
    k = 10**np.polyval(params, np.log10(T))
    return k


#################################################################
# From Ray Radebaugh
def RRadebaugh1(T, low_param, hi_param, erf_param):
    low_param = np.flip(low_param)
    hi_param = np.flip(hi_param)
    k = loglog_func(T, low_param, hi_param, erf_param)
    return k

def RRadebaugh3(T, low_param, hi_param, erf_param):
    low_param = np.flip(low_param)
    hi_param = np.flip(hi_param)

    k = loglog_func(T, low_param, hi_param, erf_param, erf_multiplicity=10)
    return k

def RRadebaugh2(T, low_param, hi_param, erf_param):
    low_param = np.flip(low_param)
    hi_param = np.flip(hi_param)

    print(np.poly1d(low_param))
    print(np.poly1d(hi_param))

    low_fit = T*np.polyval(low_param, T)
    hi_fit = 10**np.polyval(hi_param, np.log10(T))
    print(low_fit, hi_fit)
    if erf_param==0:
        erf_hi = 0
        erf_low = 1
    elif erf_param==-1:
        erf_low = 0
        erf_hi = 1
    else:
        erf_multiplicity = 1/7
        erf_low = 0.5*(1-erf(erf_multiplicity*(T -erf_param)))
        erf_hi = 0.5*(1+erf(erf_multiplicity*(T - erf_param)))

    k = low_fit*erf_low+hi_fit*erf_hi
    return k

def RRadebaugh3(T, low_param, hi_param, erf_param):
    h = hi_param[-1]
    low_param = np.flip(low_param)
    hi_param = np.flip(hi_param[:-1])

    low_fit = T*np.polyval(low_param, T)
    hi_fit = np.polyval(hi_param, np.log10(T)) + h*np.exp(np.log10(T))
    hi_fit = 10**hi_fit

    if erf_param==0:
        erf_hi = 0
        erf_low = 1
    elif erf_param==-1:
        erf_low = 0
        erf_hi = 1
    else:
        erf_multiplicity = 1/7
        erf_low = 0.5*(1-erf(erf_multiplicity*(T -erf_param)))
        erf_hi = 0.5*(1+erf(erf_multiplicity*(T - erf_param)))

    k = low_fit*erf_low+hi_fit*erf_hi
    return k

def RRadebaugh_koT(T, param_dictionary):
    """
    Description : Fits the data in a linear space with a polynomial + 1 order
    Description : k = T*polynomial(T)
                : k = T*(a + bT + cT**2 ...)
    Arguments :
    - T - temperature(s) at which to estimate the thermal conductivity.
    - param_dictionary - dictionary containing the parameters for the polynomial fit.
    """
    param = param_dictionary["low_param"]
    return T*(np.polyval(param, T) + 1e-9*T**4)

def RRadebaugh_logkexp(T, param_dictionary):
    """
    Description : Fits the data in a log10 space 
    Description : Fit Type k = 10**polynomial(log10(T)) (or) k = 10*(a + b*log10(T) + c*log10(T)**2 ...)
    
    Arguments :
    - T - temperature(s) at which to estimate the thermal conductivity.
    - param_dictionary - dictionary containing the parameters for the polynomial fit.
    """
    if len(param_dictionary["hi_param"])!=0:
        param = param_dictionary["hi_param"]
    else:
        param = param_dictionary["low_param"]
    return 10**(np.polyval(param[1:], np.log10(T)) + param[0]*np.exp(-np.log10(T)))
###########################################################################
# From the NIST5a Excel Spreadsheet

def NIST5a_1(T, params):
    k = 10**np.polyval(params[::-1], np.log10(T))
    return k

"""
Case 1   'NIST type formulation, see first sheet
    logtemp = Log(temp) / Log(10#)
    For I = 1 To 15
        Conductivity = Conductivity + IParameters(I) * logtemp ^ (I - 1)
    Next I
    Conductivity = 10 ^ Conductivity
"""



def NBS(temp, IParameters):
    L_0 = 0.00000002443
    beta = IParameters[1] / L_0 * 1 / IParameters[0]
    
    ln_temp_ratio_10 = np.log(temp / IParameters[10])
    ln_temp_ratio_11 = np.log(temp / IParameters[11])
    ln_temp_ratio_14 = np.log(temp / IParameters[14])
    ln_temp_ratio_15 = np.log(temp / IParameters[15])
    ln_temp_ratio_18 = np.log(temp / IParameters[18])
    ln_temp_ratio_19 = np.log(temp / IParameters[19])
    ln_temp_ratio_22 = np.log(temp / IParameters[22])

    rho_c = (IParameters[9] * ln_temp_ratio_10 * np.exp(-1 * (ln_temp_ratio_11 / IParameters[12]) ** 2) +
             IParameters[13] * ln_temp_ratio_14 * np.exp(-1 * (ln_temp_ratio_15 / IParameters[16]) ** 2) +
             IParameters[17] * ln_temp_ratio_18 * np.exp(-1 * (ln_temp_ratio_19 / IParameters[20]) ** 2) +
             IParameters[21] * np.exp(-1 * (ln_temp_ratio_22 / IParameters[23]) ** 2))

    rho_0 = beta / temp

    rho_i = (IParameters[2] * temp ** IParameters[3] / 
             (1 + IParameters[2] * IParameters[4] * temp ** (IParameters[3] + IParameters[5]) * 
              np.exp(-1 * (IParameters[6] / temp) ** IParameters[7])) + rho_c)
    
    rho_i0 = IParameters[8] * rho_i * rho_0 / (rho_i + rho_0)
    
    Conductivity = 1 / (rho_0 + rho_i + rho_i0)
    
    return Conductivity

"""
Case 5 'Classic NBS (National Bureau of Standards) equations for Al, Cu, Fe, W using measured RRR values
        'See NBSIR 84-3007 June 1984 Thermal Conductivity of Al, Cu, Fe, W
        'for temperatures from 1K to the melting point
    L_0 = 0.00000002443
    beta = IParameters(1) / L_0 * 1 / IParameters(0)
    rho_c = IParameters(9) * Ln(temp / IParameters(10)) * Exp(-1 * (Ln(temp / IParameters(11)) / IParameters(12)) ^ 2) + _
           IParameters(13) * Ln(temp / IParameters(14)) * Exp(-1 * (Ln(temp / IParameters(15)) / IParameters(16)) ^ 2) + _
           IParameters(17) * Ln(temp / IParameters(18)) * Exp(-1 * (Ln(temp / IParameters(19)) / IParameters(20)) ^ 2) + _
           IParameters(21) * Exp(-1 * (Ln(temp / IParameters(22)) / IParameters(23)) ^ 2)
    rho_0 = beta / temp
    rho_i = IParameters(2) * temp ^ IParameters(3) / (1 + IParameters(2) * IParameters(4) * temp ^ (IParameters(3) + IParameters(5)) * _
            Exp(-1 * (IParameters(6) / temp) ^ IParameters(7))) + rho_c
    rho_i0 = IParameters(8) * rho_i * rho_0 / (rho_i + rho_0)
    
    Conductivity = 1 / (rho_0 + rho_i + rho_i0)
    

"""

def NIST5a_6(temp, IParameters, sc):
    if sc == 1:
        temp = 1.18

    L_0 = 0.0000000245
    beta = IParameters[1] / L_0 / IParameters[0]

    IParameters[2] = min(IParameters[24] * (IParameters[0] ** IParameters[25]), IParameters[2])
    IParameters[4] = max(IParameters[26] * (IParameters[0] ** IParameters[27]), IParameters[4])

    ln_temp_ratio_10 = np.log(temp / IParameters[10])
    ln_temp_ratio_11 = np.log(temp / IParameters[11])
    ln_temp_ratio_14 = np.log(temp / IParameters[14])
    ln_temp_ratio_15 = np.log(temp / IParameters[15])
    ln_temp_ratio_18 = np.log(temp / IParameters[18])
    ln_temp_ratio_19 = np.log(temp / IParameters[19])
    ln_temp_ratio_22 = np.log(temp / IParameters[22])

    rho_c = (IParameters[9] * ln_temp_ratio_10 * np.exp(-1 * (ln_temp_ratio_11 / IParameters[12]) ** 2) +
             IParameters[13] * ln_temp_ratio_14 * np.exp(-1 * (ln_temp_ratio_15 / IParameters[16]) ** 2) +
             IParameters[17] * ln_temp_ratio_18 * np.exp(-1 * (ln_temp_ratio_19 / IParameters[20]) ** 2) +
             IParameters[21] * np.exp(-1 * (ln_temp_ratio_22 / IParameters[23]) ** 2))

    rho_0 = beta / temp

    rho_i = (IParameters[2] * temp ** IParameters[3] / 
             (1 + IParameters[2] * IParameters[4] * temp ** (IParameters[3] + IParameters[5]) * 
              np.exp(-1 * (IParameters[6] / temp) ** IParameters[7])) + rho_c)

    rho_i0 = IParameters[8] * rho_i * rho_0 / (rho_i + rho_0)

    if sc == 1:
        normcond = 1 / (rho_0 + rho_i + rho_i0)
        formtype = 8
        return normcond, formtype  # Simulates the "GoTo Reenter"
    else:
        Conductivity = 1 / (rho_0 + rho_i + rho_i0)
        return Conductivity
"""
Case 6 'Modified NBS approach by Adam Woodcraft: Cryogenics 45 (2005) 421–431
    
    If (sc = 1) Then temp = 1.18
    
    L_0 = 0.0000000245
    beta = IParameters(1) / L_0 * 1 / IParameters(0)
    
    IParameters(2) = Application.WorksheetFunction.Min(IParameters(24) * (IParameters(0)) ^ IParameters(25), IParameters(2))
    IParameters(4) = Application.WorksheetFunction.Max(IParameters(26) * (IParameters(0)) ^ IParameters(27), IParameters(4))
    
    rho_c = IParameters(9) * Ln(temp / IParameters(10)) * Exp(-1 * (Ln(temp / IParameters(11)) / IParameters(12)) ^ 2) + _
           IParameters(13) * Ln(temp / IParameters(14)) * Exp(-1 * (Ln(temp / IParameters(15)) / IParameters(16)) ^ 2) + _
           IParameters(17) * Ln(temp / IParameters(18)) * Exp(-1 * (Ln(temp / IParameters(19)) / IParameters(20)) ^ 2) + _
           IParameters(21) * Exp(-1 * (Ln(temp / IParameters(22)) / IParameters(23)) ^ 2)
    rho_0 = beta / temp
    rho_i = IParameters(2) * temp ^ IParameters(3) / (1 + IParameters(2) * IParameters(4) * temp ^ (IParameters(3) + IParameters(5)) * _
            Exp(-1 * (IParameters(6) / temp) ^ IParameters(7))) + rho_c
    rho_i0 = IParameters(8) * rho_i * rho_0 / (rho_i + rho_0)
    
    If (sc = 1) Then
        normcond = 1 / (rho_0 + rho_i + rho_i0)
        formtype = 8
        GoTo Reenter
    Else
        Conductivity = 1 / (rho_0 + rho_i + rho_i0)
    End If

"""
def NIST5a_7(temp, IParameters):
    if temp > IParameters[17]:
        formtype = IParameters[16]
        # Simulate the "GoTo Reenter" by returning formtype and a flag
        return None, formtype
    else:
        Conductivity = IParameters[19] * temp ** IParameters[18]
        return Conductivity, None


"""
Case 7 'First do higher temp, the continue with power-series approximation.
    If (temp > IParameters(17)) Then
        formtype = IParameters(16)
        GoTo Reenter
    Else
        Conductivity = IParameters(19) * temp ^ IParameters(18)
    End If

    

"""

def NIST5a_7(temp, IParameters, sc, normcond=None):
    if temp > IParameters[30]:
        formtype = IParameters[29]
        # Simulate the "GoTo Reenter" by returning formtype and a flag
        return None, formtype, sc, None
    elif IParameters[29] == 6:
        if sc == 0:
            sc = 1
            origtemp = temp
            formtype = 6
            # Simulate the "GoTo Reenter" by returning formtype and a flag
            return None, formtype, sc, origtemp
        else:
            temp = origtemp
            Conductivity = normcond * np.exp(IParameters[31] * (1 - 1.18 / temp))
            return Conductivity, None, sc, None
    else:
        Conductivity = IParameters[32] * np.exp(IParameters[31] * (1 - IParameters[30] / temp))
        return Conductivity, None, sc, None

"""
Case 8 'Superconducting extension
    If (temp > IParameters(30)) Then
        formtype = IParameters(29)
        GoTo Reenter
    ElseIf (IParameters(29) = 6) Then
        If (sc = 0) Then
            sc = 1
            origtemp = temp
            formtype = 6
            GoTo Reenter
        Else
            temp = origtemp
            Conductivity = normcond * Exp(IParameters(31) * (1 - 1.18 / temp))
        End If
    Else
        Conductivity = IParameters(32) * Exp(IParameters(31) * (1 - IParameters(30) / temp))
    End If  
"""