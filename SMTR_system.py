#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: TSP
"""

import TSP_SMARTX_CONFIG as config

###############################################################################
#                                    CONSTANTS                                #
###############################################################################

#T_LIFETIME_SMTR =                  15 # units : years 
POWER_SMTR_ACTIVE_LOW =          1.6  # units : W
POWER_SMTR_ACTIVE_SPECS =          1.8  # units : W
POWER_SMTR_ACTIVE_HIGH =          3  # units : W
POWER_SMTR_SLEEP_SPECS =           1e6  # units : W
DUTY_CYCLE_SA_USUAL_SMTR =         0.0  # 0 = always ACTIVE

POWER_SMTR_DATA_COM =               0 #1.83 # units : W

EMBODIED_ENERGY_SMTR_TYPICAL =             1511.31 # units : MJ
EMBODIED_ENERGY_SMTR_LOW =             0.9*EMBODIED_ENERGY_SMTR_TYPICAL # units : MJ
EMBODIED_ENERGY_SMTR_HIGH =             1.1*EMBODIED_ENERGY_SMTR_TYPICAL # units : MJ

E_MAINT =               0 # units : MJ
E_RECYCLING =               0 # units : MJ
RAW_MAT_ENERGY_SMTR =              0#135 # units : MJ

G_START_FSOLVE =                   0.234

###############################################################################
#                                    FUNCTIONS                                #
###############################################################################


def get_E_RawMaterials(scenario):
    
    if (scenario == 'LOW'):
        Erm = RAW_MAT_ENERGY_SMTR
        
    elif(scenario == 'BENCHMARK'):
        Erm = RAW_MAT_ENERGY_SMTR
        
    elif(scenario == 'HIGH'):
        Erm = RAW_MAT_ENERGY_SMTR
        
    else:
        raise NameError
            
    return Erm*1e6 # units : J

def get_E_Embodied(scenario):
    
    if (scenario == 'LOW'):
        
        Eem = EMBODIED_ENERGY_SMTR_LOW
        
    elif(scenario == 'BENCHMARK'):
        
        Eem = EMBODIED_ENERGY_SMTR_TYPICAL
        
    elif(scenario == 'HIGH'):
    
        Eem = EMBODIED_ENERGY_SMTR_HIGH
        
    else:
        raise NameError
    
    return Eem*1e6# units : J

def get_E_Operation(scenario):
    "Output = energy in JOULES for ONE year"
    
    if (scenario == 'LOW'):
        
        Eop = (DUTY_CYCLE_SA_USUAL_SMTR*POWER_SMTR_SLEEP_SPECS + (1-DUTY_CYCLE_SA_USUAL_SMTR)*(POWER_SMTR_ACTIVE_LOW + POWER_SMTR_DATA_COM))*config.CONVERSION_YEAR_to_SEC/1e6 # units : MJ
        
    elif(scenario == 'BENCHMARK'):
        
        Eop = (DUTY_CYCLE_SA_USUAL_SMTR*POWER_SMTR_SLEEP_SPECS + (1-DUTY_CYCLE_SA_USUAL_SMTR)*(POWER_SMTR_ACTIVE_SPECS + POWER_SMTR_DATA_COM))*config.CONVERSION_YEAR_to_SEC/1e6 # units : MJ
        
    elif(scenario == 'HIGH'):
    
        Eop = (DUTY_CYCLE_SA_USUAL_SMTR*POWER_SMTR_SLEEP_SPECS + (1-DUTY_CYCLE_SA_USUAL_SMTR)*(POWER_SMTR_ACTIVE_HIGH + POWER_SMTR_DATA_COM))*config.CONVERSION_YEAR_to_SEC/1e6 # units : MJ
        
    else:
        raise NameError
        
    return Eop*1e6 # units : J

def get_E_Maintenance(T_replacement, ARGS, scenario):
    
    if (scenario == 'LOW'):
        Em = EMBODIED_ENERGY_SMTR_LOW/T_replacement
        
    elif(scenario == 'BENCHMARK'):
        Em = EMBODIED_ENERGY_SMTR_TYPICAL/T_replacement
        
    elif(scenario == 'HIGH'):
        Em = EMBODIED_ENERGY_SMTR_HIGH/T_replacement
        
    else:
        raise NameError
        
    Em = Em*1 # energy "equivalent" over one year
    
    if (T_replacement < 0): Em = 0
    
    return Em*1e6 # units : J

def get_E_EoL(scenario):
    
    if (scenario == 'LOW'):
        Er = 0
        
    elif(scenario == 'BENCHMARK'):
        Er = 0
        
    elif(scenario == 'HIGH'):
        Er = 0
        
    else:
        raise NameError
        
    return Er*1e6 # units : J