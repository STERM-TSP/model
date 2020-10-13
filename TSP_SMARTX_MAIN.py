#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: TSP
"""
###############################################################################

import sys

#import TSP_SMARTX_CONFIG as config
import TSP_SMARTX_CONFIG_simple as config

###############################################################################

### Systems definition

## PARAMS = (system_ID, 
#            baseline_power, 
#            specific alpha_0, 
#            PTT, 
#            beta, 
#            lifetime_system, 
#            color, 
#            args)

# PHILIPS HUE

HUE_system_LED = config.SmartSystem('PHILIPS-HUE-LED',      \
                                    9,                      \
                                    [0.17, 0.70, 0.35],\
                                    [[1, -1]],              \
                                    (1000/365.25)/24,                  \
                                    5,                      \
                                    ['peachpuff'],          \
                                    [2, 8, 1])

# SMART METER
SMTR_system = config.SmartSystem('SMART-METER',             \
                                 524,                       \
                                 [0.03, 0.08, 0.15], \
                                 [[1, 0.5], [0, -1]],                 \
                                 24/24,                         \
                                 15,                        \
                                 ['peachpuff'],             \
                                 None)


# OFFICE LIGHTNING
OFFICE_LIGHT_system = config.SmartSystem('OFFICE-LIGHTNING',             \
                                 100,                       \
                                 [0.2, 0.35, 0.5], \
                                 [[1, -1]],                 \
                                 (2500*0.6/365.25)/24,                         \
                                 15,                        \
                                 ['peachpuff'],             \
                                 [1, 4, 0])

###############################################################################

# SYSTEM SELECTION
System_sel = OFFICE_LIGHT_system

###############################################################################

### Defines the baseline power of the whole system considered

if (System_sel.system_ID == 'PHILIPS-HUE-LED' or System_sel.system_ID == 'PHILIPS-HUE-CFL' or System_sel.system_ID == 'PHILIPS-HUE-INC'):

    bps = System_sel.baseline_power*System_sel.args[1] #baseline_power PER BULB times the number of bulbs in the system ! 
    System_sel.setBaselinePowerSystem(bps)
    
    name_str = '{}#OS {}#BULBS {}#HUBS'.format(System_sel.args[0], System_sel.args[1], System_sel.args[2])
    System_sel.setSetupNameDetails(name_str)
    
elif(System_sel.system_ID == 'SMART-METER'):
    
    bps = System_sel.baseline_power 
    System_sel.setBaselinePowerSystem(bps)
    
    name_str = '{}#LINKY'.format(1)
    System_sel.setSetupNameDetails(name_str)
    
elif(System_sel.system_ID == 'OFFICE-LIGHTNING'):
    
    bps = System_sel.baseline_power
    System_sel.setBaselinePowerSystem(bps)
    
    name_str = '{}#SENSOR {}#NODES {}#HUBS MODULE'.format(System_sel.args[0], System_sel.args[1], System_sel.args[2])
    System_sel.setSetupNameDetails(name_str)
    
elif(System_sel.system_ID == 'other'):

    # other systems can be added here
    print('\n Please add another system or select another existing system ! \n')
    sys.exit(2)
    
else:
    raise NameError

###############################################################################

### PLOT special cases of alpha
    
config.plotSpecificAlpha(System_sel)

###############################################################################

## PLOT the evolution of TPB depending on the number of bulbs in the system

if (System_sel.system_ID == 'PHILIPS-HUE-LED' or System_sel.system_ID == 'PHILIPS-HUE-CFL' or System_sel.system_ID == 'PHILIPS-HUE-INC'):

    config.plotBulbsImpactHUE(System_sel)

###############################################################################

### PLOT TPB for a range of alpha
### PLOT potential savings depending on alpha
### CHECK if fsolve did its job properly
    
config.plotTPB_AlphaRange(System_sel)

