# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 6.14-5 replay file
# Internal Version: 2015_08_18-21.37.49 135153
# Run by Admin on Mon Nov 23 13:44:43 2020
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(1.11979, 1.1169), width=164.833, 
    height=110.796)
session.viewports['Viewport: 1'].makeCurrent()
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
execfile('autoParametric2DnoGUI.py', __main__.__dict__)
#: The model "Model-1" has been created.
#: The interaction property "Chamber Walls" has been created.
#: The interaction "Walls" has been created.
#: Model: E:/NCKH/TEMP_ABAQUS/Runscript_Abaqus/soft-robot-parametric/abaqusScript/Job-1.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     1
#: Number of Meshes:             1
#: Number of Element Sets:       7
#: Number of Node Sets:          7
#: Number of Steps:              1
print 'RT script done'
#: RT script done
