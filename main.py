# import file path to environment
import sys
import os
dir_path = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(dir_path)
# import CAE library Abaqus
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup

# import config file
from config.parameter import parameter