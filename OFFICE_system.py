#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: TSP
"""

import TSP_SMARTX_CONFIG_simple as config

###############################################################################
#                                    CONSTANTS                                #
###############################################################################


LIFETIME_LIGHT =                    25e3 # units : hours

DUTY_CYCLE_SA =     0
POWER_HUB_MEAN = 2.5
POWER_NODE_MEAN =     0.025
POWER_SENSOR_MEAN =     0.25

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

G_START_FSOLVE =                   0.234

###############################################################################
#                                    FUNCTIONS                                #
###############################################################################


def get_E_RawMaterials(scenario):
    
    if (scenario == 'LOW'):
        Erm = 0
        
    elif(scenario == 'BENCHMARK'):
        Erm = 0
        
    elif(scenario == 'HIGH'):
        Erm = 0
        
    else:
        raise NameError
            
    return Erm*1e6 # units : J

def get_E_Embodied(ARGS, scenario):
    
    number_os, number_nodes, number_hubs = ARGS
    
    if (scenario == 'LOW'):
        
        Eem_os = E_EM_OS_LOW 
        Eem_nodes = E_EM_BULB_LOW
        Eem_hubs = E_EM_HUB_LOW 
        
    elif(scenario == 'BENCHMARK'):
        
        Eem_os = E_EM_OS_TYPICAL 
        Eem_nodes = E_EM_BULB_TYPICAL 
        Eem_hubs = E_EM_HUB_TYPICAL 
        
    elif(scenario == 'HIGH'):
    
        Eem_os = E_EM_OS_HIGH 
        Eem_nodes = E_EM_BULB_HIGH
        Eem_hubs = E_EM_HUB_HIGH 
        
    else:
        raise NameError
            
    Eem = number_os*Eem_os + number_nodes*Eem_nodes + number_hubs*Eem_hubs # units : MJ
    
    return Eem*1e6 # units = J

def get_E_Operation(ARGS, scenario):
    "Output = energy in JOULES for ONE year"
    
    number_os, number_nodes, number_hubs = ARGS
    
    if (scenario == 'LOW'):
        Eop_os = POWER_SENSOR_MEAN*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ 
        Eop_nodes = POWER_NODE_MEAN*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        Eop_hubs = (DUTY_CYCLE_SA*POWER_HUB_MEAN + (1-DUTY_CYCLE_SA)*POWER_HUB_MEAN)*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        
    elif(scenario == 'BENCHMARK'):
        Eop_os = POWER_SENSOR_MEAN*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        Eop_nodes = POWER_NODE_MEAN*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        Eop_hubs = (DUTY_CYCLE_SA*POWER_HUB_MEAN + (1-DUTY_CYCLE_SA)*POWER_HUB_MEAN)*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        
    elif(scenario == 'HIGH'):
        Eop_os = POWER_SENSOR_MEAN*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        Eop_nodes = POWER_NODE_MEAN*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        Eop_hubs = (DUTY_CYCLE_SA*POWER_HUB_MEAN + (1-DUTY_CYCLE_SA)*POWER_HUB_MEAN)*config.CONVERSION_YEAR_to_HOURS/1000*config.CONVERSION_kWh_to_MJ
        
    else:
        raise NameError

    Eop = number_os*Eop_os + number_nodes*Eop_nodes + number_hubs*Eop_hubs # units : MJ
    
    return Eop*1e6 # units = J

def get_E_Maintenance(T_replacement, ARGS, scenario):
    
    number_os, number_nodes, number_hubs = ARGS
    
    if (scenario == 'LOW'):
        Em = number_nodes*0/T_replacement
        
    elif(scenario == 'BENCHMARK'):
        Em = number_nodes*0/T_replacement
        
    elif(scenario == 'HIGH'):
        Em = number_nodes*0/T_replacement
        
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