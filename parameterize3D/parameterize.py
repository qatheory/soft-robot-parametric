from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup

base_length = 50
base_width = 5.0
base_thickness = 0.5

currentModel = mdb.models["Model-1"]


class Material(object):
    def __init__(self, name, density, materialType):
        self.name = name
        self.createMaterial()
        self.setDensity(density)
        self.setElasticity(materialType)

    def createMaterial(self):
        currentModel.Material(name=self.name)
        return currentModel.materials[self.name]

    def getName(self):
        return self.name

    def getMaterial(self):
        return currentModel.materials[self.name]

    def setDensity(self, density):
        self.getMaterial().Density(
            table=((density, ), ))

    def setPaperAttribute(self):
        self.getMaterial().Elastic(table=((6500.0, 0.2), ))

    def setElastosilAttribute(self):
        self.getMaterial().Hyperelastic(materialType=ISOTROPIC, testData=OFF, type=YEOH,
                                        volumetricResponse=VOLUMETRIC_DATA, table=((0.11, 0.02, 0.0, 0.0, 0.0, 0.0), ))

    def setElasticity(self, materialType):
        if(materialType == "paper"):
            self.setPaperAttribute()
        elif(materialType == "elastosil"):
            self.setElastosilAttribute()


class Section(object):
    def __init__(self, name, material, sectionType, thickness=None):
        self.name = name
        self.createSection(material, sectionType, thickness)

    def getName(self):
        return self.name

    def getSection(self):
        return currentModel.sections[self.name]

    def createSolidSection(self, material, thickness):
        currentModel.HomogeneousSolidSection(
            name=self.name, material=material.getName(), thickness=None)

    def createShellSection(self, material, thickness):
        currentModel.HomogeneousShellSection(
            name=self.name,
            preIntegrate=OFF,
            material=material.getName(),
            thicknessType=UNIFORM,
            thickness=thickness,
            thicknessField='',
            idealization=NO_IDEALIZATION,
            poissonDefinition=DEFAULT,
            thicknessModulus=None,
            temperature=GRADIENT,
            useDensity=OFF,
            integrationRule=SIMPSON,
            numIntPts=5)

    def createSection(self, material, sectionType, thickness):
        if(sectionType == "solid"):
            self.createSolidSection(material, thickness)
        elif(sectionType == "shell"):
            self.createShellSection(material, thickness)
        else:
            return "defined that f*cking material type, please!!!!!!!!"


class Object(object):
    def __init__(self, name):
        self.position = [0.0, 0.0, 0.0]
        self.part = None
        self.name = name
        self.sketchName = "{}_sketch".format(name)
        self.partName = "{}_part".format(name)
        self.set = "{}_set".format(name)
        self.createSketch()
        self.createPart()

    def getName(self):
        print(self.name)
        return

    def setName(self, name):
        self.name = name

    def move(self, pos):
        print("moved")
        return

    def createSketch(self):
        currentModel.ConstrainedSketch(name=self.sketchName, sheetSize=200.0)
        print("sketch created")
        return currentModel.sketches[self.sketchName]
        # return "sketch created"

    def getSketch(self):
        print("sketch {} here".format(self.sketchName))
        return currentModel.sketches[self.sketchName]
        # return "sketch {} here".format(self.sketchName)

    def createPart(self):
        currentModel.Part(
            name=self.partName, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        return(currentModel.parts[self.partName])

    def getPart(self):
        return(currentModel.parts[self.partName])

    def assignSection(self, section):
        objectCell = self.getPart().cells.findAt((tuple(self.position), ), )
        objectRegion = self.getPart().Set(cells=objectCell, name=self.set)
        self.getPart().SectionAssignment(region=objectRegion,
                                         sectionName=section.getName(),
                                         offset=0.0,
                                         offsetType=MIDDLE_SURFACE,
                                         offsetField='',
                                         thicknessAssignment=FROM_SECTION)

    def setMaterial(self, material):
        print("added material")
        return "added material"


class Base(Object):
    def __init__(self, name, length=0.0, width=0.0, thickness=0.0):
        super(Base, self).__init__(name)
        self.length = length
        self.width = width
        self.thickness = thickness
        self.name = name
        self.drawSketch()
        self.buildPart()

    def drawSketch(self):
        self.getSketch().rectangle(
            point1=(0.0, 0.0), point2=(self.length, self.width))
        return

    def buildPart(self):
        self.getPart().BaseSolidExtrude(
            sketch=self.getSketch(), depth=self.thickness)
        return

# Process code


Elastosil = Material("Elastosil", 1.13e-09, "elastosil")
Paper = Material("Paper", 7.5e-10, "paper")

ElastosilSection = Section("Sec-Elastosil", Elastosil, "solid")
PaperSection = Section("Sec-Paper", Paper, "shell", 0.1)

BaseA = Base("Base_A", 50, 50, 5)
BaseA.assignSection(ElastosilSection)
BaseB = Base("abc", 10, 5, 0.2)
BaseB.assignSection(ElastosilSection)
