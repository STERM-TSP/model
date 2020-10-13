#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: TSP
"""
###############################################################################
#                                      IMPORT                                 #
###############################################################################

import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as opt
import sys
from tqdm import tqdm
       
import HUE_system as HUE
import SMTR_system as SMTR
import OFFICE_system as OFFICE
### import new system files here ...

###############################################################################
#                                    CONSTANTS                                #
###############################################################################

### CONVERSION ###

CONVERSION_Wh_to_J =                3.6e3                                             # units : J/Wh
CONVERSION_kWh_to_J =               CONVERSION_Wh_to_J*1e3                            # units : J/kWh
CONVERSION_kWh_to_MJ =              CONVERSION_Wh_to_J/1e3                            # units : MJ/kWh

CONVERSION_DAY_to_SEC =             24*60*60

CONVERSION_YEAR_to_DAYS =           365.25                                            # units : days
CONVERSION_YEAR_to_HOURS =          24*CONVERSION_YEAR_to_DAYS                        # units : hours
CONVERSION_YEAR_to_SEC =            CONVERSION_YEAR_to_DAYS*CONVERSION_DAY_to_SEC     # units : seconds

### CONSTANTS
ELEC_TO_PRIMARY_ENERGY =            3                                                 # units : /

T_PB_INFINITY =                     1e3                                              # units : years

### PARAMETERS
TIME_HORIZON =                      50                                                # units : years

###############################################################################
#                                    FUNCTIONS                                #
###############################################################################

class SmartSystem:
    
     def __init__(self, system_ID, baseline_power, alpha0, PTT, beta, lifetime_system, color, args):
         self.system_ID = system_ID
         self.baseline_power = baseline_power
         
         self.alpha0 = alpha0
         self.PTT = PTT
         
         self.beta = beta
         self.lifetime_system = lifetime_system
         
         self.color_all = color
         self.args = args
         
         self.baseline_power_system = -1
         self.setup = 'empty'
         
     def setBaselinePowerSystem(self, bps):
         self.baseline_power_system =  bps
         
     def setSetupNameDetails(self, name_str):
         self.setup = name_str
         

###############################################################################

def plotSpecificAlpha(System_sel):
    "PLOT TPB for specific cases of alpha0"
    
    number_of_coeff = len(System_sel.alpha0)
    
    sys_coeff_ID = []
    
    for current_alpha0 in range(number_of_coeff):
        
        sys_coeff_ID.append(System_sel.system_ID + '\n\u03B1='+str(System_sel.alpha0[current_alpha0]*100) + '%')
    
    t_pb_all = [] 
    uncert_all = [] 
    
    for current_alpha0 in range(number_of_coeff):
        
        t_pb, uncert, _ , _, _ = get_TPB(System_sel, System_sel.alpha0[current_alpha0], True)
    
        t_pb_all.append(t_pb)
        uncert_all.append([t_pb - uncert[0], uncert[1] - t_pb])
        
        print("*** $\u03B1_0$ = {}% | \u03B2 = {} hours/day \n<-> {} hours less utilization needed \n<-> {} W power saved\n".format(System_sel.alpha0[current_alpha0]*100, round(System_sel.beta*24, 1), round(System_sel.alpha0[current_alpha0]*System_sel.beta*24, 1), round(System_sel.alpha0[current_alpha0]*System_sel.beta*System_sel.baseline_power_system, 1)))
    
    fig, ax = plt.subplots(1)
    
    plt.bar(np.asarray(sys_coeff_ID), np.asarray(t_pb_all), color=System_sel.color_all)
    plt.errorbar(np.asarray(sys_coeff_ID), np.asarray(t_pb_all), yerr =  np.transpose(np.asarray(uncert_all)), label='Uncertainty', fmt = 'none', capsize = 6, ecolor = 'black', elinewidth = 1, capthick = 2) #xerr = lumin_techno, yerr = [10, 10, 10]
    
    #plt.fill_between(np.asarray(sys_coeff_ID), 0, System_sel.lifetime_system, alpha=0.1, edgecolor='#1B2ACC', facecolor='magenta',linewidth=1, linestyle='dashdot', antialiased=True, label='System\'s lifetime')
    plt.hlines(System_sel.lifetime_system, sys_coeff_ID[0], sys_coeff_ID[-1], colors='magenta', linestyles='dashed', label='System\'s lifetime (= {} years)'.format(System_sel.lifetime_system), alpha=0.2)
    
    
    plt.yscale('log')
    plt.ylim([1e-3, TIME_HORIZON])
    ax.set_axisbelow(True)
    plt.grid(color='lightgray', linestyle='dashed')
    
    plt.title('Payback time - Project : {}\nSetup = {}\n\u03B2 = {}\n'.format(System_sel.system_ID, System_sel.setup, round(System_sel.beta, 2)))
    plt.ylabel('Payback Time [years]')
    plt.xlabel('System ID')
    
    plt.grid(alpha=0.2)
    plt.legend()

###############################################################################

def plotBulbsImpactHUE(System_sel):
    "PLOT the evolution of TPB depending on the number of bulbs in the system"
    
    memory_bps = System_sel.baseline_power_system
    memory_args = System_sel.args
    
    bulbs_range = [1, 51] #maximum 50 nodes connected to a HUE hub
    bulbs = range(bulbs_range[0], bulbs_range[1])
    
    t_pb_usual = []
    t_pb_up = []
    t_pb_dn = []
    
    coeff_index = 1
    
    for bulb in bulbs:   
        
        System_sel.setBaselinePowerSystem(System_sel.baseline_power*bulb)
        System_sel.args = [System_sel.args[0], bulb, System_sel.args[2]]
    
        t_pb, uncert, _ , _, _ = get_TPB(System_sel, System_sel.alpha0[coeff_index], False)
        
        t_pb_usual.append(t_pb)
        t_pb_up.append(uncert[1])
        t_pb_dn.append(uncert[0])
    
    plt.figure()
    
    plt.plot(bulbs, t_pb_usual, label='Typical')
    plt.plot(bulbs, t_pb_up, 'r', alpha=0.5, label='Upper boundary')
    plt.plot(bulbs, t_pb_dn, 'g', alpha=0.5, label='Lower boundary')
    
    plt.hlines(System_sel.lifetime_system, bulbs[0], bulbs[-1], colors='magenta', linestyles='dashed', label='System\'s lifetime (= {} years)'.format(System_sel.lifetime_system), alpha=0.2)
        
    plt.yscale('log')
    plt.ylim([0, TIME_HORIZON])
    
    plt.title('Evolution of the payback time depending on the number of smart bulbs per hub\nSystem = {} - $\u03B1_0$ = {} - \u03B2 = {}\n'.format(System_sel.system_ID, System_sel.alpha0[coeff_index], round(System_sel.beta, 2)))
    plt.ylabel('T_PB [years]')
    plt.xlabel('Number of smart bulbs [/]')
    plt.xlim([0, bulbs_range[1]])
    
    plt.grid(alpha=0.2)
    plt.legend()
    
    # restore default parameters
    System_sel.setBaselinePowerSystem(memory_bps)
    System_sel.args = memory_args

###############################################################################

def plotTPB_AlphaRange(System_sel):
    "PLOT TPB for a range of alpha0 \
     PLOT potential savingsfor a range of alpha0 \
     CHECK if fsolve did its job properly"
     
    ### PLOT TPB for a range of alpha0

    alpha0_range = [0, 1]
    alpha0 = np.arange(alpha0_range[0], alpha0_range[1], 0.001) #0.0001
    
    t_pb_usual = []
    t_pb_up = []
    t_pb_dn = []
    
    t_pb_solved_all = []
    
    savings_b = []
    savings_w = []
    Esmart_atLT = []
    
    G_all = []
    
    for current_alpha0 in tqdm(range(len(alpha0))):    

            t_pb, uncert, t_pb_solved, savings, G = get_TPB(System_sel, alpha0[current_alpha0], False)

            t_pb_usual.append(t_pb)
            t_pb_up.append(uncert[1])
            t_pb_dn.append(uncert[0])
            
            t_pb_solved_all.append(t_pb_solved)
            
            savings_b.append(savings[0])
            savings_w.append(savings[1])
            Esmart_atLT.append(savings[2])
            
            G_all.append(G)
            
    plt.figure()
    
    plt.plot(alpha0*100, t_pb_usual, label='Typical')
    plt.plot(alpha0*100, t_pb_up, 'r', alpha=0.5, label='Upper boundary')
    plt.plot(alpha0*100, t_pb_dn, 'g', alpha=0.5, label='Lower boundary')

    plt.plot(alpha0*100, t_pb_solved_all, '--', color='blue', alpha=0.4, label='Influence of a varying \u03B1 \non the typical scenario')

    plt.hlines(System_sel.lifetime_system, alpha0[0]*100, alpha0[-1]*100, colors='magenta', linestyles='dashed', label='System\'s lifetime (= {} years)'.format(System_sel.lifetime_system), alpha=0.2)

    alpha0_wsavings  = alpha0[np.where(np.asarray(savings_w)>=0)[0][0]]*100 if len(np.where(np.asarray(savings_w)>=0)[0]) != 0 else alpha0[-1]*100
    plt.vlines(alpha0_wsavings, 0, TIME_HORIZON, colors='black', linestyles='dashed', label='W-savings boundary', alpha=0.2)

    plt.fill_between(alpha0*100, t_pb_dn, t_pb_up, alpha=0.1, facecolor='grey', antialiased=True)

    plt.yscale('log')
    plt.ylim([0, TIME_HORIZON])
    plt.xlim([0, alpha0_range[1]*100])

    plt.title('Evolution of the payback time depending on \u03B1\nSystem = {}\n\u03B2 = {} | Setup = {}\nPTT = {}'.format(System_sel.system_ID, round(System_sel.beta, 2), System_sel.setup, System_sel.PTT))
    plt.ylabel('$T_{PB}$ [years]')
    plt.xlabel('$\u03B1_0$ [%]')
    
    plt.grid(alpha=0.2)
    plt.legend()
    
    ### PLOT potential savings depending on alpha0

    fig, ax1 = plt.subplots()
    
    ax1.plot(alpha0*100, savings_b, alpha=0.5, label='Best case savings (Benchmarck, \u03B1 constant)')
    ax1.plot(alpha0*100, savings_w, '--', color='blue', alpha=0.5, label='Worst case savings (Benchmarck, \u03B1 varying)')
    ax1.hlines(0, alpha0[0]*100, alpha0[-1]*100, colors='olive', linestyles='dashed', label='No savings', alpha=0.4)
        
    ax1.fill_between(alpha0*100, savings_w, savings_b, alpha=0.1, facecolor='grey', antialiased=True)

    ax1.vlines(alpha0_wsavings, 0, max(savings_b), colors='black', linestyles='dashed', label='W-savings boundary', alpha=0.2)

    #plt.yscale('log')
    ax1.set_ylim([min(savings_w), max(savings_b)])

    ax1.set_title('Evolution of potential savings at the end of system\'s lifetime depending on \u03B1\nSystem = {}\n\u03B2 = {}\nSetup = {}'.format(System_sel.system_ID, round(System_sel.beta, 2), System_sel.setup))
    ax1.set_ylabel('Savings [%]')
    ax1.set_xlabel('$\u03B1_0$ [%]')
    
    ax2 = ax1.twinx()
    y1, y2 = ax1.get_ylim()
    ax2.set_ylim(y1/100*Esmart_atLT[0]/1e6, y2/100*Esmart_atLT[0]/1e6)
    ax2.figure.canvas.draw()
    ax2.set_ylabel('Savings [MJ]')

    ax1.grid(alpha=0.2)
    ax1.legend()
    
#    plt.figure()
#    plt.plot(alpha0*100, np.asarray(G_all)/1e6, 'x')
#    plt.plot(alpha0*100, np.asarray(savings_w)/100*Esmart_atLT[0]/1e6, '--', color='blue', alpha=0.5, label='Worst case savings (Benchmarck, \u03B1 varying. (\u03C4={} years))'.format(System_sel.PTT[1]))
        
    ### Check FSOLVE results on the range of alpha0
    if (1):
        diff_solved = np.diff(t_pb_solved_all)
        monotone_decr = max(diff_solved) > 0.0
        
        if (monotone_decr):
            raise ValueError("[CRITICAL ERROR] : please enter another value for G_START_FSOLVE ... \n")
        
    #    plt.figure()
    #    plt.title('Influence of a varying \u03B1 \non the payback time, typical scenario')
    #    plt.ylabel('T_PB [years]')
    #    plt.xlabel('$\u03B1_0$ [%]')
    #    plt.plot(alpha0*100, t_pb_solved_all, alpha=0.6, color='grey')
    #    plt.yscale('log')
        #plt.ylim([0, config.TIME_HORIZON])    
    
###############################################################################
         
def TPB(Erm, Eem, Er, P_saved, Pm, Pop):
    "This function returns the payback time. \
     - units output = years \
     - Exxx units = Joules whereas Pxxx units = Watts"
    
    num = Erm + Eem + Er
    denom = ELEC_TO_PRIMARY_ENERGY*CONVERSION_YEAR_to_SEC*P_saved - ELEC_TO_PRIMARY_ENERGY*CONVERSION_YEAR_to_SEC*Pop - CONVERSION_YEAR_to_SEC*Pm
    
    if (denom <= 0):
        t_pb = T_PB_INFINITY

    else:
        t_pb = num/denom

    return t_pb

###############################################################################
    
def G(t, Erm, Eem, Er, beta, alpha0, baseline_power_system, Pm, Pop, PTT):
    "This function returns the NET gains a time t. \
      - units output = Joules, Primary Energy \
      - t and tau have to be given in the same units \
      - Exxx units = Joules whereas Pxxx units = Watts "
    
    #g = ELEC_TO_PRIMARY_ENERGY*CONVERSION_YEAR_to_SEC*baseline_power_system*beta*alpha0*(phi*t + tau*theta*(1-np.exp(-t/tau))) - ELEC_TO_PRIMARY_ENERGY*CONVERSION_YEAR_to_SEC*Pop*t - CONVERSION_YEAR_to_SEC*Pm*t - Eem - Erm - Er

    g = E_saved_f(PTT, t, alpha0, beta, baseline_power_system) - E_smart(Erm, Eem, Er, Pop, Pm, t)

    return g

###############################################################################

def E_saved_f(PTT, time, alpha0, beta, baseline_power_system): 
    "This function returns ONLY the energy saved by the introduction of the smart layer. \
      - units output = Joules, Primary Energy" 
      
    if (type(time) == int): 
        time = [time]
    
    time = np.asarray(time)
    
    E_s = []
    PTT_array = np.asarray(PTT)
    
    limit = np.cumsum(PTT_array[:,1][0:-1])
    limit = np.append(0, limit)
    limit = np.append(limit, TIME_HORIZON)
    
    weight = []

    for t in time:
        for ind in range(len(limit)-1):
            if ((t - limit[ind]) >= 0) and ((t - limit[ind+1]) <= 0):
                weight.append((t - limit[ind]))
            elif ((t - limit[ind]) >= 0) and ((t - limit[ind+1]) >= 0):
                weight.append(1*abs(PTT_array[ind,1]))
            elif ((t - limit[ind]) <= 0) and ((t - limit[ind+1]) <= 0):
                weight.append(0)
        
        coef = weight*PTT_array[:, 0]
        weight = []

        E_s.append(np.sum(ELEC_TO_PRIMARY_ENERGY*CONVERSION_YEAR_to_SEC*beta*baseline_power_system*alpha0*coef))
        
    if (len(time)==1):
        E_s = E_s[0]
        
    return np.asarray(E_s)

###############################################################################

def E_smart(Erm, Eem, Er, Pop, Pm, t):
    "This function returns ONLY the energy of the smart layer at a time t. \
      - units input = t [years] \
      - units output = Joules, Primary Energy" 
    
    E_smart = (Erm + Er + Eem) + (ELEC_TO_PRIMARY_ENERGY*Pop + Pm)*CONVERSION_YEAR_to_SEC*t
    
    return E_smart

###############################################################################

def alpha_t(time, alpha0, PTT): 
    "This function returns the value of alpha through time. \
      - units output = / " 
    # Time and tau have to be given with the same units
    
    time = np.asarray(time)
    
    alpha = []
    PTT_array = np.asarray(PTT)
    
    limit = np.cumsum(PTT_array[:,1][0:-1])
    limit = np.append(limit, TIME_HORIZON)
    
    for t in time:
        if (len(PTT) == 1):
            alpha.append(alpha0*PTT_array[0, 0])
        elif (t < limit[0]):
            alpha.append(alpha0*PTT_array[0, 0])
        elif(t > limit[0]):
            alpha.append(alpha0*PTT_array[np.where(t > limit)[-1][-1]+1, 0])
    
    return np.asarray(alpha)

###############################################################################
    
def plot_EC(axes, title, days, E_em, E_op, E_saved, t_pb, lifetime_system, savings, alpha0, PTT, beta, baseline_power_system):
    "Plot energy curves for given parameters"
    
    axes.plot(days, np.asarray(E_em)/1e6, 'r', alpha=0.2, linewidth= 1, label='Embodied energy')
    axes.plot(days, np.asarray(E_op)/1e6, 'b', alpha=0.2, linewidth= 1, label='Use-phase energy')
    axes.plot(days, np.asarray(E_op + E_em)/1e6, 'k', linewidth= 1, label='Energy for the smart layer')
    axes.plot(days, np.asarray(E_saved)/1e6, 'g-', linewidth= 1, label='Energy saved thanks to the smartness\n\u03B1 constant')
    
    axes.vlines(t_pb, 0, max(E_saved)/1e6, colors='olive', linestyles='dashed', label='T_PB', alpha=0.4)
    axes.vlines(lifetime_system, 0, max(E_saved)/1e6, colors='magenta', linestyles='dashed', label='T_lifetime (= {} years)\nb-savings = {}% | w-savings = {}%)'.format(lifetime_system, savings[0], savings[1]), alpha=0.4)

    axes.plot(days, E_saved_f(PTT, days, alpha0, beta, baseline_power_system)/1e6, label='Energy saved thanks to the smartness\n\u03B1 changes with time')

    axes.set_ylim([0, max(E_saved)/1e6])
    axes.set_ylabel('Energy [MJ]')
    
    Esmart_at_lifetime = savings[2]/1e6
    ax2 = axes.twinx()
    y1, y2 = axes.get_ylim()
    ax2.set_ylim(y1/Esmart_at_lifetime*100, y2/Esmart_at_lifetime*100)
    ax2.figure.canvas.draw()
    ax2.set_ylabel('Relative share w.r.t. $E_{smart}$ at system\'s lifetime [%]')
    
    axes.set_title(title + ' - T_PB = {} days  = {} years'.format(round(t_pb*CONVERSION_YEAR_to_DAYS), round(t_pb, 2)))
    axes.grid(alpha=0.2)
        
    if (t_pb > lifetime_system): axes.text(0, 0, 'PAYBACK TIME IS GREATER THAN SYSTEM LIFETIME !', fontsize=12, bbox=dict(facecolor='red', alpha=0.7))

###############################################################################

def get_TPB(System_sel, alpha0, plot_energy_curves):
    "This is the main function. It returns the payback time for the given parameters. \
      - units output = [years, years, years, %]. "
    
    ### Params
    system_ID = System_sel.system_ID
    PTT = System_sel.PTT
    beta = System_sel.beta
    baseline_power_system = System_sel.baseline_power_system
    lifetime_system = System_sel.lifetime_system
    ARGS = System_sel.args
    
    P_saved = baseline_power_system*alpha0*beta # W = J/s
    
    #TIME_HORIZON = lifetime_system*1.2

    if (system_ID == 'PHILIPS-HUE-LED' or system_ID == 'PHILIPS-HUE-CFL' or system_ID == 'PHILIPS-HUE-INC'):
        
        G_start_fsolve = HUE.G_START_FSOLVE
                
        Erm = HUE.get_E_RawMaterials('BENCHMARK')
        Erm_DN = HUE.get_E_RawMaterials('LOW')
        Erm_UP = HUE.get_E_RawMaterials('HIGH')
        
        Eem =  HUE.get_E_Embodied(ARGS, 'BENCHMARK')
        Eem_DN = HUE.get_E_Embodied(ARGS, 'LOW')
        Eem_UP =  HUE.get_E_Embodied(ARGS, 'HIGH')
        
        Pop = HUE.get_E_Operation(ARGS, 'BENCHMARK')/CONVERSION_YEAR_to_SEC
        Pop_DN = HUE.get_E_Operation(ARGS, 'LOW')/CONVERSION_YEAR_to_SEC
        Pop_UP = HUE.get_E_Operation(ARGS, 'HIGH')/CONVERSION_YEAR_to_SEC
        
        if (system_ID == 'PHILIPS-HUE-LED'):
            T_replacement = HUE.LIFETIME_LED/(beta*CONVERSION_YEAR_to_HOURS*(1-alpha0))
        elif (system_ID == 'PHILIPS-HUE-CFL'):
            T_replacement = HUE.LIFETIME_CFL/(beta*CONVERSION_YEAR_to_HOURS*(1-alpha0))
        elif (system_ID == 'PHILIPS-HUE-INC'):
            T_replacement = HUE.LIFETIME_INC/(beta*CONVERSION_YEAR_to_HOURS*(1-alpha0))
        else:
            raise NameError
            
        T_replacement = -1
            
        Pm = HUE.get_E_Maintenance(T_replacement, ARGS, 'BENCHMARK')/CONVERSION_YEAR_to_SEC
        Pm_DN = HUE.get_E_Maintenance(T_replacement, ARGS, 'LOW')/CONVERSION_YEAR_to_SEC
        Pm_UP = HUE.get_E_Maintenance(T_replacement, ARGS, 'HIGH')/CONVERSION_YEAR_to_SEC
                
        Er = HUE.get_E_EoL('BENCHMARK')
        Er_DN = HUE.get_E_EoL('LOW')
        Er_UP = HUE.get_E_EoL('HIGH')
        
        
    elif(system_ID == 'SMART-METER'):
        
        if (ARGS != None): raise TypeError
        
        G_start_fsolve = SMTR.G_START_FSOLVE
        
        Erm = SMTR.get_E_RawMaterials('BENCHMARK')
        Erm_DN = SMTR.get_E_RawMaterials('LOW')
        Erm_UP = SMTR.get_E_RawMaterials('HIGH')
    
        Eem =  SMTR.get_E_Embodied('BENCHMARK')
        Eem_DN = SMTR.get_E_Embodied('LOW')
        Eem_UP = SMTR.get_E_Embodied('HIGH')
        
        Pop = SMTR.get_E_Operation('BENCHMARK')/CONVERSION_YEAR_to_SEC
        Pop_DN = SMTR.get_E_Operation('LOW')/CONVERSION_YEAR_to_SEC
        Pop_UP = SMTR.get_E_Operation('HIGH')/CONVERSION_YEAR_to_SEC
            
        T_replacement = 1e6 # years
        
        Pm = SMTR.get_E_Maintenance(T_replacement, ARGS, 'BENCHMARK')/CONVERSION_YEAR_to_SEC
        Pm_DN = SMTR.get_E_Maintenance(T_replacement, ARGS, 'LOW')/CONVERSION_YEAR_to_SEC
        Pm_UP = SMTR.get_E_Maintenance(T_replacement, ARGS, 'HIGH')/CONVERSION_YEAR_to_SEC
        
        Er = SMTR.get_E_EoL('BENCHMARK')
        Er_DN = SMTR.get_E_EoL('LOW')
        Er_UP = SMTR.get_E_EoL('HIGH')
    
    elif(system_ID == 'OFFICE-LIGHTNING'):
        
        G_start_fsolve = OFFICE.G_START_FSOLVE
        
        Erm = OFFICE.get_E_RawMaterials('BENCHMARK')
        Erm_DN = OFFICE.get_E_RawMaterials('LOW')
        Erm_UP = OFFICE.get_E_RawMaterials('HIGH')
    
        Eem =  OFFICE.get_E_Embodied(ARGS, 'BENCHMARK')
        Eem_DN = OFFICE.get_E_Embodied(ARGS, 'LOW')
        Eem_UP = OFFICE.get_E_Embodied(ARGS, 'HIGH')
        
        Pop = OFFICE.get_E_Operation(ARGS, 'BENCHMARK')/CONVERSION_YEAR_to_SEC
        Pop_DN = OFFICE.get_E_Operation(ARGS, 'LOW')/CONVERSION_YEAR_to_SEC
        Pop_UP = OFFICE.get_E_Operation(ARGS, 'HIGH')/CONVERSION_YEAR_to_SEC
        
        T_replacement = OFFICE.LIFETIME_LIGHT/(beta*CONVERSION_YEAR_to_HOURS*(1-alpha0))
        
        Pm = OFFICE.get_E_Maintenance(T_replacement, ARGS, 'BENCHMARK')/CONVERSION_YEAR_to_SEC
        Pm_DN = OFFICE.get_E_Maintenance(T_replacement, ARGS, 'LOW')/CONVERSION_YEAR_to_SEC
        Pm_UP = OFFICE.get_E_Maintenance(T_replacement, ARGS, 'HIGH')/CONVERSION_YEAR_to_SEC
        
        Er = OFFICE.get_E_EoL('BENCHMARK')
        Er_DN = OFFICE.get_E_EoL('LOW')
        Er_UP = OFFICE.get_E_EoL('HIGH')
    
    elif(system_ID == 'other'):
        
        # other systems can be added here
        print('\n Please add another system CONFIG or select another existing system CONFIG ! \n')
        sys.exit(2)
        
    else:
        raise NameError
        
    t_pb = TPB(Erm, Eem, Er, P_saved, Pm, Pop) # units : years
            
    # uncertainty
    uncert = []
    
    t_pb_DN = TPB(Erm_DN, Eem_DN, Er_DN, P_saved, Pm_DN, Pop_DN)

    t_pb_UP = TPB(Erm_UP, Eem_UP, Er_UP, P_saved, Pm_UP, Pop_UP)
    
    uncert.append(t_pb_DN)
    uncert.append(t_pb_UP)

    time_gains = np.linspace(0, TIME_HORIZON, 1000)
    gains_tau = G(time_gains, Erm, Eem, Er, beta, alpha0, baseline_power_system, Pm, Pop, PTT)

    t_pb_solved = opt.fsolve(G, G_start_fsolve, args=(Erm, Eem, Er, beta, alpha0, baseline_power_system, Pm, Pop, PTT))
    t_pb_solved = T_PB_INFINITY if (max(gains_tau) < 0) else t_pb_solved[0]

    number_of_days = int(CONVERSION_YEAR_to_DAYS*TIME_HORIZON)
#    days =  np.asarray(range(0, number_of_days))/CONVERSION_YEAR_to_DAYS
    days = np.linspace(0, TIME_HORIZON, number_of_days)
    
    def list_E(Erm, Eem, Er, Pm, Pop): 
            
        E_em = np.linspace(Eem + Erm + Er, Eem + Erm + Er + Pm*CONVERSION_YEAR_to_SEC*TIME_HORIZON, number_of_days)
        E_op = np.linspace(0, ELEC_TO_PRIMARY_ENERGY*Pop*CONVERSION_YEAR_to_SEC*TIME_HORIZON, number_of_days)
        E_saved = np.linspace(0, ELEC_TO_PRIMARY_ENERGY*P_saved*CONVERSION_YEAR_to_SEC*TIME_HORIZON, number_of_days)
        
        E_smart_atLT = E_smart(Erm, Eem, Er, Pop, Pm, lifetime_system)
        
        bsavings = np.around(G(lifetime_system, Erm, Eem, Er, beta, alpha0, baseline_power_system, Pm, Pop, [[1, -1]])/E_smart_atLT*100, 2)
        wsavings = np.around(G(lifetime_system, Erm, Eem, Er, beta, alpha0, baseline_power_system, Pm, Pop, PTT)/E_smart_atLT*100, 2)
        
        return E_em, E_op, E_saved, [bsavings, wsavings, E_smart_atLT]
        
    E_em, E_op, E_saved, savings = list_E(Erm, Eem, Er, Pm, Pop)
    E_em_DN, E_op_DN, E_saved_DN, savings_DN = list_E(Erm_DN, Eem_DN, Er_DN, Pm_DN, Pop_DN)
    E_em_UP, E_op_UP, E_saved_UP, savings_UP = list_E(Erm_UP, Eem_UP, Er_UP, Pm_UP, Pop_UP)
        
    if (plot_energy_curves):
        
        ########### Energy curves
        if(0):
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
            fig.suptitle('Energy curves for {}\n$\u03B1_0$ = {}% - \u03B2 = {}\n'.format(system_ID, alpha0*100, round(beta, 2)))
            
            plot_EC(ax1, 'Lower boundary', days, E_em_DN, E_op_DN, E_saved_DN, t_pb_DN, lifetime_system, savings_DN, alpha0, PTT, beta, baseline_power_system)
            ax1.set_xlim([0, TIME_HORIZON])
    
            #ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
            plot_EC(ax2, 'Typical', days, E_em, E_op, E_saved, t_pb, lifetime_system, savings, alpha0, PTT, beta, baseline_power_system)
            #if (system_ID == 'PHILIPS-HUE-LED'): plt.vlines(T_life_bulb*CONVERSION_YEAR_to_DAYS, 0, max(E_saved)/1e6, colors='orange', linestyles='dashed', label='T_life_bulbFF (= {} years)'.format(round(T_life_bulb, 2)), alpha=0.4)
            
            plot_EC(ax3, 'Upper boundary', days, E_em_UP, E_op_UP, E_saved_UP, t_pb_UP, lifetime_system, savings_UP, alpha0, PTT, beta, baseline_power_system)
            ax3.set_xlabel('Time [years]')

        ########### plot energy curves only for typical scenario
        fig, ax1 = plt.subplots()
        title = 'Energy curves for {}\n$\u03B1_0$ = {}% - \u03B2 = {}\nTypical'.format(system_ID, alpha0*100, round(beta, 2))
        plot_EC(ax1, title, days, E_em, E_op, E_saved, t_pb, lifetime_system, savings, alpha0, PTT, beta, baseline_power_system)
        
        ax1.set_xlabel('Time [years]')
        #ax2 = ax1.twinx()
        #ax2.set_ylabel('Share of the total smart layer energy (over lifetime) [%]')
        ax1.legend()
        
        
        ########### Evolution of G(t) and alpha(t)
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        fig.suptitle('Influence of a varying \u03B1\n$\u03B1_0$ = {}%\n'.format(alpha0*100)) #fontsize=16
        
        # G(t)
        ax1.plot(time_gains, gains_tau/1e6, label='Net gains')
        if (system_ID == 'PHILIPS-HUE-LED' and T_replacement > 0): ax1.vlines(T_replacement, 0, max(gains_tau)/1e6, colors='black', linestyles='dashed', label='T_replacement (= {} years)'.format(round(T_replacement, 2)), alpha=0.4)
        ax1.vlines(lifetime_system, min(gains_tau)/1e6, max(gains_tau)/1e6, colors='magenta', linestyles='dashed', label='T_lifetime (= {} years)'.format(lifetime_system), alpha=0.4)

        ax1.set_xlim([0, TIME_HORIZON])
        ax1.set_ylabel('Gains [MJ]')
        ax1.set_title('Evolution of G(t) for the typical scenario')
        
        ax1.grid(alpha=0.2)
        ax1.legend()
        
        # alpha(t)
        ax2.plot(days, alpha_t(days, alpha0, PTT), label='Discontinuous $\u03B1$')
        ax2.hlines(alpha0, min(time_gains), max(time_gains), colors='grey', linestyles='dashed', label='$\u03B1_0$', alpha=0.5)

        ax2.set_ylabel('$\u03B1$ [/]')
        ax2.set_xlabel('Time [years]')
        ax2.set_title('Evolution of $\u03B1(t)$')

        ax2.grid(alpha=0.2)
        ax2.legend()

    return t_pb, uncert, t_pb_solved, savings, G(lifetime_system, Erm, Eem, Er, beta, alpha0, baseline_power_system, Pm, Pop, PTT)

# end of script