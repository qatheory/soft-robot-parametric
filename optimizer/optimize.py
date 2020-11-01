
import csv
import subprocess
from config.parameter import setParameters, getParameters


def optimize(baseLength):

    # Predefined base length
    base_length = baseLength

    result = []

    # Optimize parameters
    chamberSpaceOptimizeTimes = 2
    chamberWallThicknessOptimizeTimes = 2
    reOptimizeTimes = 2
    minChamberSize = 2
    minChamberSpace = 0.5
    minChamberWallThickness = 0.5
    limitChamberNum = 2
    maxChamberNum = 2

    # Calculate block size which contain a chamber and a chamber space
    minBlockLength = minChamberSize + minChamberSpace
    limitLength = base_length

    # Calculate posible instances of block will fit the base length
    if (limitLength // minBlockLength >= limitChamberNum):
        maxChamberNum = limitChamberNum
    else:
        maxChamberNum = limitLength // minBlockLength

    # Calculate chamber space length depend on number of chamber
    for chamber_num in range(1, int(maxChamberNum)+1):
        maxChamberSpace = base_length / (2*(chamber_num+2) - 1)

        # Create a list of chamber space values for model
        listChamberSpaceValues = [minChamberSpace]
        chamberSpaceRange = maxChamberSpace
        if(chamberSpaceOptimizeTimes > 1):
            chamberSpaceRange = (maxChamberSpace-minChamberSpace) / (chamberSpaceOptimizeTimes-1)
            for i in range(1, chamberSpaceOptimizeTimes):
                listChamberSpaceValues.append(minChamberSpace + (chamberSpaceRange * i))

        # Calculate chamber wall thickess length depend on chamber size
        for chamber_space in listChamberSpaceValues:
            chamber_size=(base_length - (chamber_num + 1)
                            * chamber_space)/(chamber_num + 2)

            # max chamber wall thickess should be in a third of chamber size
            maxChamberWallThickness=chamber_size / 3

            # Create a list of chamber wall thickess values for model
            chamberWallThicknessRange=maxChamberWallThickness
            listChamberWallThicknessValues=[minChamberWallThickness]
            if(chamberWallThicknessOptimizeTimes > 1):
                chamberWallThicknessRange=(
                    maxChamberWallThickness-minChamberWallThickness)/(chamberWallThicknessOptimizeTimes-1)
                for i in range(1, chamberWallThicknessOptimizeTimes):
                    listChamberWallThicknessValues.append(minChamberWallThickness + (
                        maxChamberWallThickness-minChamberWallThickness)/(chamberWallThicknessOptimizeTimes-1) * i)

            for chamber_wallThickness in listChamberWallThicknessValues:
                # Define all parameter using in model
                parameters={
                    "base_length": baseLength,
                    "base_thickness": 2.5,
                    "wall_length": None,
                    "wall_height": 12,
                    "wall_boundariesThickness_head": chamber_wallThickness,
                    "wall_boundariesThickness_tail": chamber_wallThickness,
                    "chamber_size": chamber_size,
                    "chamber_fisrtLength": chamber_size,
                    "chamber_lastLength": chamber_size,
                    "chamber_space": chamber_space,
                    "chamber_height": 9,
                    "chamber_num": chamber_num,
                    "chamber_wallThickness": chamber_wallThickness,
                    "chamber_tunnelWidth": 2,
                    "chamber_tunnelHeight": 0,
                    "chamber_upperCoverThickness": 2,
                    "chamber_underCoverThickness": 0.5,
                    "skin_thickness": 0.1,
                    "pressure": 0.01,
                    "seedSize": 3,
                }
                setParameters(parameters)
                subprocess.run(
                    ["abaqus", "cae", "noGUI=./abaqusScript/autoParametric2DnoGUI.py"], shell=True)
                print("*********************")
                with open('transpose_output.csv', 'r') as file:
                    reader=csv.reader(file)
                    for row in reader:
                        for col in row:
                            print(float(col))
                            result.append({
                                "num": chamber_num,
                                "size": chamber_size,
                                "space": chamber_space,
                                "wallThickness": chamber_wallThickness,
                                "chamberSpaceRange": chamberSpaceRange,
                                "chamberWallThicknessRange": chamberWallThicknessRange,
                                "value": col
                            })
    optimizeInstances = []
    bestResult=max(result, key=lambda x: x["value"])
    print(bestResult)
    listSpaceOptimizeValues = []
    chamber_num = bestResult["num"]
    for i in range(1, reOptimizeTimes+1):
        listSpaceOptimizeValues.append(bestResult["space"] + bestResult["chamberSpaceRange"]/(reOptimizeTimes +1) * i)
        listSpaceOptimizeValues.append(
            bestResult["space"] - bestResult["chamberSpaceRange"]/(reOptimizeTimes + 1) * i)
    for chamber_space in listSpaceOptimizeValues:
        chamber_size = (base_length - (chamber_num + 1)
                        * chamber_space)/(chamber_num + 2)

        # max chamber wall thickess should be in a third of chamber size
        maxChamberWallThickness = chamber_size / 3

        # Create a list of chamber wall thickess values for model
        chamberWallThicknessRange = maxChamberWallThickness
        listChamberWallThicknessValues = [minChamberWallThickness]
        if(chamberWallThicknessOptimizeTimes > 1):
            chamberWallThicknessRange = (
                maxChamberWallThickness-minChamberWallThickness)/(chamberWallThicknessOptimizeTimes-1)
            for i in range(1, chamberWallThicknessOptimizeTimes):
                listChamberWallThicknessValues.append(minChamberWallThickness + (
                    maxChamberWallThickness-minChamberWallThickness)/(chamberWallThicknessOptimizeTimes-1) * i)

        for chamber_wallThickness in listChamberWallThicknessValues:
            # Define all parameter using in model
            parameters = {
                "base_length": baseLength,
                "base_thickness": 2.5,
                "wall_length": None,
                "wall_height": 12,
                "wall_boundariesThickness_head": chamber_wallThickness,
                "wall_boundariesThickness_tail": chamber_wallThickness,
                "chamber_size": chamber_size,
                "chamber_fisrtLength": chamber_size,
                "chamber_lastLength": chamber_size,
                "chamber_space": chamber_space,
                "chamber_height": 9,
                "chamber_num": chamber_num,
                "chamber_wallThickness": chamber_wallThickness,
                "chamber_tunnelWidth": 2,
                "chamber_tunnelHeight": 0,
                "chamber_upperCoverThickness": 2,
                "chamber_underCoverThickness": 0.5,
                "skin_thickness": 0.1,
                "pressure": 0.01,
                "seedSize": 3,
            }
            setParameters(parameters)
            subprocess.run(
                ["abaqus", "cae", "noGUI=./abaqusScript/autoParametric2DnoGUI.py"], shell=True )
            print("*********************")
            with open('transpose_output.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    for col in row:
                        print(float(col))
                        optimizeInstances.append({
                            "num": chamber_num,
                            "size": chamber_size,
                            "space": chamber_space,
                            "wallThickness": chamber_wallThickness,
                            "chamberSpaceRange": chamberSpaceRange,
                            "chamberWallThicknessRange": chamberWallThicknessRange,
                            "value": col
                        })
    bestOptimize = max(optimizeInstances, key=lambda x: x["value"])
    print(bestOptimize)


    
