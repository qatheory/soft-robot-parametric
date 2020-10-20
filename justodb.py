from abaqus import *
from abaqusConstants import *
from odbAccess import *

myOdb = visualization.openOdb(path=str('Job-{}'.format(n + 1)) + '.odb')
centerNSet = myOdb.rootAssembly.instances['MERGED-BODY-1'].nodeSets["SET-NODE"]
frame = myOdb.steps['Step-Pressure'].frames[-1]

# Retrieve Y-displacement at the center of the plate.

dispField = frame.fieldOutputs['U']
dispSubField = dispField.getSubset(region=centerNSet)
# disp = dispSubField.values[0].data[0]
# disp = dispSubField.values[0].data[1]
disp = dispSubField.values[0].magnitude
session.viewports['Viewport: 1'].setValues(displayedObject=myOdb)
f = open("C:\My Workspace\Abaqus\AutoParametric\displacement_data.csv", "a")
f.write(str(str(disp) + "\n"))
f.close()