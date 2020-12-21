# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 6.14-5 replay file
# Internal Version: 2015_08_18-21.37.49 135153
# Run by Admin on Mon Nov 23 13:35:56 2020
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
execfile('autoParametric2D_force.py', __main__.__dict__)
#: The model "Model-1" has been created.
#: The interaction property "IntProp-1" has been created.
#: The interaction "contact_baseC_gripper" has been created.
#: The interaction property "Chamber Walls" has been created.
#: The interaction "Walls" has been created.
#: Model: E:/NCKH/TEMP_ABAQUS/Runscript_Abaqus/soft-robot-parametric/abaqusScript/2D_Force/Job-1.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     2
#: Number of Meshes:             2
#: Number of Element Sets:       9
#: Number of Node Sets:          8
#: Number of Steps:              1
#: The model "Model-2" has been created.
#: The interaction property "IntProp-1" has been created.
#: The interaction "contact_baseC_gripper" has been created.
#: The interaction property "Chamber Walls" has been created.
#: The interaction "Walls" has been created.
#: Model: E:/NCKH/TEMP_ABAQUS/Runscript_Abaqus/soft-robot-parametric/abaqusScript/2D_Force/Job-2.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     2
#: Number of Meshes:             2
#: Number of Element Sets:       9
#: Number of Node Sets:          8
#: Number of Steps:              1
print 'RT script done'
#: RT script done
