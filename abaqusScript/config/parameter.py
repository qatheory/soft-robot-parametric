import csv
import sys
import os

def getParameters():
    with open('parameters.csv', 'r') as file:
        reader = list(csv.reader(file))
        parameters = {
            "base_length": float(reader[0][0]),
            "base_thickness": float(reader[1][0]),
            "wall_length": None,
            "wall_height": float(reader[3][0]),
            "wall_boundariesThickness_head": float(reader[4][0]),
            "wall_boundariesThickness_tail": float(reader[5][0]),
            "chamber_size": float(reader[6][0]),
            "chamber_fisrtLength": float(reader[7][0]),
            "chamber_lastLength": float(reader[8][0]),
            "chamber_space": float(reader[9][0]),
            "chamber_height": float(reader[10][0]),
            "chamber_num": int(reader[11][0]),
            "chamber_wallThickness": float(reader[12][0]),
            "chamber_tunnelWidth": float(reader[13][0]),
            "chamber_tunnelHeight": float(reader[14][0]),
            "chamber_upperCoverThickness": float(reader[15][0]),
            "chamber_underCoverThickness": float(reader[16][0]),
            "skin_thickness": float(reader[17][0]),
            "pressure": float(reader[18][0]),
            "seedSize": float(reader[19][0]),
        }
        # print(parameters["chamber_num"])
        # print(parameters["chamber_size"])
        # print(parameters["chamber_space"])
        # print(parameters["chamber_wallThickness"])
        # print(parameters["base_length"])
        # print(parameters["chamber_num"] *
        #       parameters["chamber_size"]+(parameters["chamber_num"] - 1)*parameters["chamber_size"])
        return parameters


def setParameters(calculatedParameter):
    parametersFile = open("parameters.csv", "w")
    for key in calculatedParameter:
        parametersFile.write(str(str(calculatedParameter[key]) + "\n"))
    parametersFile.close()
    getParameters()
