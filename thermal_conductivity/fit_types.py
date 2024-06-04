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

def Nppoly(T, param):
    return T*np.polyval(param, T)
def polylog(T, param):
    return 10**np.polyval(param, np.log10(T))

def loglog_func(T, low_param, hi_param, erf_param, erf_multiplicity=15):
    """
    Description : Takes a temperature (or temp array) and fit arguments returns the estimated k value.

    Arguments : 
    - T - temperature at which to estimate the thermal conductivity.
    - low_param: in form a + bT + cT**2 ...
    
    Make sure to remove trailing zeros 
    """
    low_param = low_param[::-1] ################################### 20240531
    hi_param = hi_param[::-1] ################################### 20240531

    low_fit = Nppoly(T, low_param)
    hi_fit = polylog(T, hi_param)

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

######################################################################

def power_law(T, params):
    A, B = params

    k = (A)*T**(B)

    return k

#################################################################
# From the NIST website

def NIST1(T, params):
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

def NIST5a_2(T, params):
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

def NIST5a_3(T, params):
    lnT = np.log(T)
    x = ((lnT - params[1]) - (params[2] - lnT)) / (params[2] - params[1])
    k = 0
    for i in range(3,3+params[0]):
        k = k + params(i) * np.cos((i - 3) * np.arccos(x))
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
def lowTextrapolate(T, params):
    k = 0
    if T > params[10]:
        logtemp = np.log10(T)
        for i in range(1, 10):
            k += params[i - 1] * logtemp ** (i - 1)
        k = 10 ** k
    elif T > params[11]:
        k = params[13] * T ** params[12]
    else:
        k = params[16] * T ** params[15]
    
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