#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: TSP
"""

import TSP_SMARTX_CONFIG_simple as config

###############################################################################
#                                    CONSTANTS                                #
###############################################################################

### DUTY CYCLE ###
DUTY_CYCLE_SA_LOW =             0.99        # units : [/] sleep time over active time
DUTY_CYCLE_SA_MEAS =                0        # units : [/] sleep time over active time

### PHILIPS HUE SYSTEM ###
POWER_HUE_HUB_SLEEP_SPECS =         0.10        # units : W        | source : Philips HUE website, datasheet
POWER_HUE_HUB_ACTIVE_SPECS =        1.25        # units : W        | source : Philips HUE website, datasheet
POWER_HUE_HUB_SLEEP_MEAS =          1e6    #-float('inf')# units : W        | source : measurements DMM7510
POWER_HUE_HUB_ACTIVE_MEAS =         1.29        # units : W        | source : measurements DMM7510

POWER_HUE_LIGHT_SLEEP_LOW =             0.4         # units : W        | source : Philips HUE website, datasheet
POWER_HUE_LIGHT_SLEEP_TYPICAL =         0.5         # units : W        | source : Philips HUE website, datasheet
POWER_HUE_LIGHT_SLEEP_HIGH =            0.5         # units : W        | source : Philips HUE website, datasheet

E_EM_OS_LOW =    7.092 # units : MJ
E_EM_OS_TYPICAL = 9.59
E_EM_OS_HIGH = 11.61

E_EM_BULB_LOW = 4.32
E_EM_BULB_TYPICAL = 11.94
E_EM_BULB_HIGH = 13.45

E_EM_HUB_LOW = 26.57
E_EM_HUB_TYPICAL = 39.21
E_EM_HUB_HIGH = 57.82

E_MAINT = 0

E_RECYCLING = 0

E_RAW_MATERIALS = 0


AAA_BATTERY_POWER_CAPACITY =        1.87        # units : Wh

LIFETIME_LED =                      25e3  # units hours
LIFETIME_CFL =                      10e3  # units hours
LIFETIME_INC =                      1e3  # units hours

G_START_FSOLVE =                   0.234

###############################################################################
#                                    FUNCTIONS                                #
###############################################################################

def get_E_RawMaterials(scenario):
    
    if (scenario == 'LOW'):
        Erm = E_RAW_MATERIALS
        
    elif(scenario == 'BENCHMARK'):
        Erm = E_RAW_MATERIALS
        
    elif(scenario == 'HIGH'):
        Erm = E_RAW_MATERIALS
        
    else:
        raise NameError
    
    return Erm*1e6 # units = J

def get_E_Embodied(ARGS, scenario):
    
    number_os, number_bulbs, number_hubs = ARGS
    
    if (scenario == 'LOW'):
        
        Eem_os = E_EM_OS_LOW 
        Eem_bulbs = E_EM_BULB_LOW
        Eem_hubs = E_EM_HUB_LOW 
        
    elif(scenario == 'BENCHMARK'):
        
        Eem_os = E_EM_OS_TYPICAL 
        Eem_bulbs = E_EM_BULB_TYPICAL
        Eem_hubs = E_EM_HUB_TYPICAL 
        
    elif(scenario == 'HIGH'):
    
        Eem_os = E_EM_OS_HIGH 
        Eem_bulbs = E_EM_BULB_HIGH
        Eem_hubs = E_EM_HUB_HIGH 
        
    else:
        raise NameError
            
    Eem = number_os*Eem_os + number_bulbs*Eem_bulbs + number_hubs*Eem_hubs # units : MJ
    
    return Eem*1e6 # units = J
    
def get_E_Operation(ARGS, scenario):
    "Output = energy in JOULES for ONE year"
    
    number_os, number_bulbs, number_hubs = ARGS
    
    if (scenario == 'LOW'):
        Eop_os = 0
        Eop_bulbs = POWER_HUE_LIGHT_SLEEP_LOW*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        Eop_hubs = (DUTY_CYCLE_SA_LOW*POWER_HUE_HUB_SLEEP_SPECS + (1-DUTY_CYCLE_SA_LOW)*POWER_HUE_HUB_ACTIVE_SPECS)*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        
    elif(scenario == 'BENCHMARK'):
        Eop_os = 0
        Eop_bulbs = POWER_HUE_LIGHT_SLEEP_TYPICAL*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        Eop_hubs = (DUTY_CYCLE_SA_MEAS*POWER_HUE_HUB_SLEEP_MEAS + (1-DUTY_CYCLE_SA_MEAS)*POWER_HUE_HUB_ACTIVE_MEAS)*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        
    elif(scenario == 'HIGH'):
        Eop_os = 0
        Eop_bulbs = POWER_HUE_LIGHT_SLEEP_HIGH*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        Eop_hubs = (DUTY_CYCLE_SA_MEAS*POWER_HUE_HUB_SLEEP_MEAS + (1-DUTY_CYCLE_SA_MEAS)*POWER_HUE_HUB_ACTIVE_MEAS)*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        
    else:
        raise NameError

    Eop = number_os*Eop_os + number_bulbs*Eop_bulbs + number_hubs*Eop_hubs # units : MJ
    
    return Eop*1e6 # units = J

def get_E_Maintenance(T_replacement, ARGS, scenario):
    
    number_os, number_bulbs, number_hubs = ARGS
    
    if (scenario == 'LOW'):
        Em = number_bulbs*E_EM_BULB_LOW/T_replacement
        
    elif(scenario == 'BENCHMARK'):
        Em = number_bulbs*E_EM_BULB_TYPICAL/T_replacement
        
    elif(scenario == 'HIGH'):
        Em = number_bulbs*E_EM_BULB_HIGH/T_replacement
        
    else:
        raise NameError
    
    Em = Em*1 # energy "equivalent" over one year
    
    if (T_replacement < 0): Em = 0
    
    return Em*1e6 # units : J


def get_E_EoL(scenario):
    
    if (scenario == 'LOW'):
        Er = E_RECYCLING
        
    elif(scenario == 'BENCHMARK'):
        Er = E_RECYCLING
        
    elif(scenario == 'HIGH'):
        Er = E_RECYCLING
        
    else:
        raise NameError
        
    return Er*1e6 # units : J