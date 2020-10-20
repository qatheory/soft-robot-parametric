import sys
import os
dir_path = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(dir_path)
from abaqus import *
from abaqusConstants import *

# import CAE library Abaqus
from caeModules import *
from driverUtils import executeOnCaeStartup
from config.parameter import parameter
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                            sheetSize=200.0)
s.rectangle(point1=(0.0, 0.0),
            point2=(parameter["height"], parameter["width"]))
p = mdb.models['Model-1'].Part(name='Part-1',
                               dimensionality=THREE_D,
                               type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseSolidExtrude(sketch=s, depth=parameter["depth"])
