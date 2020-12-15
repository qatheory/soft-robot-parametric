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


class Sketch(object):
    def __init__(self, name, transform=None):
        self.name = "{}_sketch".format(name)
        self.transform = transform
        self.createSketch(transform)
        self.lineLastPosition = (0.0, 0.0)

    def createSketch(self, transform):
        if (transform == None):
            currentModel.ConstrainedSketch(
                name=self.name, sheetSize=200.0)
        else:
            currentModel.ConstrainedSketch(
                name=self.name, sheetSize=200.0, transform=transform)
        print("sketch {} created".format(self.name))
        return currentModel.sketches[self.name]
        # return "sketch created

    def get(self):
        return currentModel.sketches[self.name]
        # return "sketch {} here".format(self.sketchName)

    def rectangle(self, p1, p2):
        self.get().rectangle(point1=(p1[0], p1[1]), point2=(p2[0], p2[1]))

    def line(self, x1, y1, x2, y2):
        self.get().Line(point1=(x1, y1), point2=(x2, y2))
        self.lineLastPosition = (x2, y2)
        # print("Drawed line from ({},{}) to ({},{}) on sketch {}".format(
        #     x1, y1, x2, y2, self.sketchName))
        return

    def lineTo(self, x2, y2):
        self.get().Line(point1=self.lineLastPosition, point2=(x2, y2))
        self.lineLastPosition = (x2, y2)
        # print("Drawed line from ({},{}) to ({},{}) on sketch {}".format(
        #     self.lineLastPosition[0], self.lineLastPosition[1], x2, y2, self.sketchName))
        return

    def refreshLineLastPosition(self, x=0.0, y=0.0):
        self.lineLastPosition = (x, y)
        return


class Object(object):
    def __init__(self, name):
        self.position = [0.0, 0.0, 0.0]
        self.part = None
        self.name = name
        # self.sketchName = "{}_sketch".format(name)
        self.partName = "{}_part".format(name)
        self.set = "{}_set".format(name)
        self.sketch = Sketch(name)
        self.createPart()
        self.lineLastPosition = (0, 0)

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def move(self, pos):
        print("moved")
        return

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

    def selectSurface(self, surface="bottom"):
        if(surface == "top"):
            baseFace = self.getPart().faces.findAt(
                ((self.length/2, self.thickness, self.width/2),),)
            self.getPart().Surface(side1Faces=baseFace, name='Top of {}'.format(self.name))

        elif(surface == "bottom"):
            baseFace = self.getPart().faces.findAt(
                ((self.length/2, 0.0, self.width/2),),)
            self.getPart().Surface(side1Faces=baseFace, name='Bottom of {}'.format(self.name))

        else:
            print("chua chon mat phang cho part {}".format(self.name))
        return

    def selectSurfaceByPos(self, x, y, z):
        baseFace = self.getPart().faces.findAt(((x, y, z),),)
        self.getPart().Surface(side1Faces=baseFace, name='Surface at {},{},{}'.format(x, y, z))
        return

    def drawSketch(self):
        self.sketch.get().rectangle(
            point1=(0.0, 0.0), point2=(self.length, self.thickness))
        return

    def buildPart(self):
        self.getPart().BaseSolidExtrude(
            sketch=self.sketch.get(), depth=self.width)
        return


class Main(Object):
    def __init__(self, name, length=0.0, wide=0.0, height=0.0, chamberNum=3, chamberSize=0.0, chamberHeight=0.0, space=0.0, heightSpace=0.0, chamberThickness=0.0, innerHeight=0.0):
        super(Main, self).__init__(name)
        self.length = length
        self.wide = wide
        self.height = height
        self.chamberNum = chamberNum
        self.chamberSize = chamberSize
        self.chamberHeight = chamberHeight
        self.chamberThickness = chamberThickness
        self.innerHeight = innerHeight
        self.space = space
        # self.heightSpace = heightSpace
        self.drawSketch()
        self.buildPart()

    def drawSketch(self):
        self.sketch.lineTo(0, self.height)
        for i in range(1, self.chamberNum):
            self.sketch.lineTo(self.chamberSize*i +
                               self.space*(i-1), self.height)
            self.sketch.lineTo(self.chamberSize*i + self.space*(i-1),
                               self.height-self.chamberHeight)
            if i != self.chamberNum:
                self.sketch.lineTo(self.chamberSize*i + self.space*i,
                                   self.height-self.chamberHeight)
                self.sketch.lineTo(self.chamberSize*i + self.space*i,
                                   self.height)
        self.sketch.lineTo(self.chamberSize*(self.chamberNum) +
                           self.space*(self.chamberNum-1), self.height)
        self.sketch.lineTo(self.chamberSize*(self.chamberNum) +
                           self.space*(self.chamberNum-1), 0.0)
        self.sketch.lineTo(0.0, 0.0)
        return

    def buildPart(self):
        self.getPart().BaseSolidExtrude(
            sketch=self.sketch.get(), depth=self.wide)
        return

    def scalePosition(self, x, y):
        return (x-self.length/2, y-self.height/2)

    def extrudeCut(self):
        extrudeCutFace = self.getPart().faces.findAt(
            ((self.length/2, 0.0, self.wide/2),),)
        extrudeCutEdge = self.getPart().edges.findAt(
            ((self.length/2, 0.0, 0.0),),)
        surfaceName = 'Bottom of {}'.format(self.name)
        self.getPart().Surface(side1Faces=extrudeCutFace, name=surfaceName)
        transform = self.getPart().MakeSketchTransform(sketchPlane=self.getPart().surfaces[surfaceName].faces[0], sketchUpEdge=self.getPart().edges[34],
                                                       sketchPlaneSide=SIDE1, sketchOrientation=TOP, origin=(0.0, 0.0, 0.0))
        cutSketch = Sketch("wallCutSketch", transform)
        for i in range(self.chamberNum):
            cutSketch.get().rectangle((self.chamberThickness+self.chamberSize*i+self.space*i, self.chamberThickness),
                                      (self.chamberSize*(i+1) + self.space*i - self.chamberThickness, self.wide - self.chamberThickness))
        self.getPart().CutExtrude(sketchPlane=self.getPart().surfaces[surfaceName].faces[0],
                                  sketchPlaneSide=SIDE1, sketchUpEdge=self.getPart().edges[34], sketchOrientation=TOP, sketch=cutSketch.get(), depth=6)
# Process code


Elastosil = Material("Elastosil", 1.13e-09, "elastosil")
Paper = Material("Paper", 7.5e-10, "paper")

ElastosilSection = Section("Sec-Elastosil", Elastosil, "solid")
PaperSection = Section("Sec-Paper", Paper, "shell", 0.1)

BaseA = Base("Base-A", 100, 50, 5)
BaseA.assignSection(ElastosilSection)
BaseA.selectSurface("top")
BaseB = Base("Base-B", 40, 20, 5)
BaseB.assignSection(ElastosilSection)
BaseB.selectSurface()
MainBody = Main("Main", 95, 10, 10, 5, 15, 7, 5, 0.0, 1)
MainBody.extrudeCut()
