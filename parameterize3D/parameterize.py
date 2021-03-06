from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup

base_length = 50
base_width = 5.0
base_thickness = 0.5

currentModel = mdb.models["Model-1"]


class RootAssembly(object):
    def __init__(self):
        self.assembly = currentModel.rootAssembly

    def getAssembly(self):
        return self.assembly

    def createSet(self, surface, name):
        # fixedFace = a.instances['Merged-Body-1'].faces.findAt(
        #     ((0.0, base_width / 2, wall_height / 2), ), )
        return self.assembly.Set(name=name, faces=surface)

    def createFace(self, instance, x, y, z, name):
        return self.assembly.instances[instance.getName()].faces.findAt(((x, y, z), ), )

    def selectFace(self, instance, surface):
        return self.assembly.instances[instance.getName()].surfaces[surface]


Assembly = RootAssembly()
assembly = Assembly.getAssembly()


class Instances(object):
    def __init__(self, name, part, create=True):
        self.name = name
        self.position = (0.0, 0.0, 0.0)
        if(create == True):
            self.createInstance(name, part)

    def createInstance(self, name, part):
        assembly.Instance(name=name, part=part.getPart(), dependent=ON)

    def translate(self, vector):
        assembly.translate(instanceList=(self.name, ), vector=vector)

    def rotate(self, vector, angle):
        point1 = (0.0, 0.0, 0.0)
        point2 = (0.0, 0.0, 0.0)
        if vector == "x":
            point2 = (1.0, 0.0, 0.0)
        if vector == "y":
            point2 = (0.0, 1.0, 0.0)
        if vector == "z":
            point2 = (0.0, 0.0, 1.0)
        self.get().rotate(instanceList=(self.name, ),
                          axisPoint=point1,
                          axisDirection=point2,
                          angle=angle)

    def get(self):
        return assembly.instances[self.name]

    def getName(self):
        return self.name


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


class Step(object):
    def __init__(self, name, previousStep='Initial', nlgeom=ON):
        self.name = name
        self.previousStep = previousStep
        if(self.previousStep != 'Initial'):
            self.previousStep = previousStep.getName()
        self.nlgeom = nlgeom
        self.createStep()

    def createStep(self):
        currentModel.StaticStep(name=self.name,
                                previous=self.previousStep,
                                nlgeom=self.nlgeom)

    def getName(self):
        return self.name

    def addGravity(self):
        currentModel.Gravity(
            name='Gravity',
            createStepName=self.getName(),
            comp2=-9810.0,
            distributionType=UNIFORM,
            field='',
            region=None)

    def addPressure(self, faces, value):
        currentModel.Pressure(
            name='Load-Pressure',
            createStepName=self.name,
            region=faces,
            distributionType=UNIFORM,
            field='',
            magnitude=value,
            amplitude=UNSET)

    def addBC(self, region):
        currentModel.EncastreBC(
            name='Fixed End',
            createStepName=self.getName(),
            region=region,
            localCsys=None)

    def createContact(self, name, part, instance):
        parameters = part.getParameters()
        currentModel.ContactProperty(name)
        currentModel.interactionProperties[name].TangentialBehavior(
            formulation=FRICTIONLESS)
        contactSurfaces = instance.get().faces.findAt(
            ((parameters["chamberSize"], (parameters["height"] - parameters["chamberHeight"]) / 2 + parameters["chamberHeight"],
              parameters["wide"]/2), ), )
        for i in range(2, parameters["chamberNum"]):
            contactSurfaces += instance.get().faces.findAt(
                ((parameters["chamberSize"]*i + parameters["space"]*(i-1), (parameters["height"] - parameters["chamberHeight"]) / 2 + parameters["chamberHeight"],
                  parameters["wide"]/2), ), )
        for i in range(1, parameters["chamberNum"]):
            contactSurfaces += instance.get().faces.findAt(
                (((parameters["chamberSize"]+parameters["space"])*i, (parameters["height"] - parameters["chamberHeight"]) / 2 + parameters["chamberHeight"],
                  parameters["wide"]/2), ), )
        print(contactSurfaces)
        contactFacesRegion = assembly.Surface(side1Faces=contactSurfaces,
                                              name='Surf-Contact')
        currentModel.SelfContactStd(
            name=name,
            createStepName=self.name,
            surface=contactFacesRegion,
            interactionProperty=name,
            thickness=ON)


class Object(object):
    def __init__(self, name):
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

    def getPartName(self):
        return self.partName

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
        objectCell = self.getPart().cells.findAt(((0.0, 0.0, 0.0), ), )
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

    def selectSurfaceByPos(self, x, y, z):
        return self.getPart().faces.findAt(((x, y, z),),)

    def createSurfaceByPos(self, x, y, z, name=None):
        baseFace = self.getPart().faces.findAt(((x, y, z),),)
        surfaceName = 'Surface at {},{},{}'.format(x, y, z)
        if(name != None):
            surfaceName = name
        self.getPart().Surface(side1Faces=baseFace, name=surfaceName)
        return self.getPart().surfaces[surfaceName]


class BasePart(Object):
    def __init__(self, name, length=0.0, width=0.0, thickness=0.0):
        super(BasePart, self).__init__(name)
        self.length = length
        self.width = width
        self.thickness = thickness
        self.name = name
        self.drawSketch()
        self.buildPart()

    # def setPosInAssembly(self):
    def getParameters(self):
        return {"length": self.length, "width": self.width, "thickness": self.thickness}

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

    def drawSketch(self):
        self.sketch.get().rectangle(
            point1=(0.0, 0.0), point2=(self.length, self.thickness))
        return

    def buildPart(self):
        self.getPart().BaseSolidExtrude(
            sketch=self.sketch.get(), depth=self.width)
        return


class MainPart(Object):
    def __init__(self, name, length=0.0, wide=0.0, height=0.0, chamberNum=3, chamberSize=0.0, chamberHeight=0.0, space=0.0, heightSpace=0.0, chamberThickness=0.0, innerHeight=0.0, tunnelWidth=0.0, tunnelHeight=0.0):
        super(MainPart, self).__init__(name)
        self.length = length
        self.wide = wide
        self.height = height
        self.chamberNum = chamberNum
        self.chamberSize = chamberSize
        self.chamberHeight = chamberHeight
        self.chamberThickness = chamberThickness
        self.innerHeight = innerHeight
        self.space = space
        self.tunnelWidth = tunnelWidth
        self.tunnelHeight = tunnelHeight
        self.tunnelLength = length - chamberThickness*2 - chamberSize*2
        # self.heightSpace = heightSpace
        self.drawSketch()
        self.buildPart()
        self.extrudeCut()

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
        # extrudeCutFace = self.getPart().faces.findAt(
        #     ((self.length/2, 0.0, self.wide/2),),)
        # surfaceName = 'Bottom of {}'.format(self.name)
        # self.getPart().Surface(side1Faces=extrudeCutFace, name=surfaceName)

        chamberCutPlane = self.getPart().faces.findAt(((0.001, 0, 0.001),),)[0]
        chamberCutEdge = self.getPart().edges.findAt(
            ((self.length/2, 0, self.wide),),)[0]
        chamberCutTransform = self.getPart().MakeSketchTransform(sketchPlane=chamberCutPlane, sketchUpEdge=chamberCutEdge,
                                                                 sketchPlaneSide=SIDE1, sketchOrientation=TOP, origin=(0.0, 0.0, 0.0))
        cutChamberSketch = Sketch("wallCutSketch", chamberCutTransform)
        for i in range(self.chamberNum):
            cutChamberSketch.get().rectangle((self.chamberThickness+self.chamberSize*i+self.space*i, self.chamberThickness),
                                             (self.chamberSize*(i+1) + self.space*i - self.chamberThickness, self.wide - self.chamberThickness))
        self.getPart().CutExtrude(sketchPlane=chamberCutPlane,
                                  sketchPlaneSide=SIDE1, sketchUpEdge=chamberCutEdge, sketchOrientation=TOP, sketch=cutChamberSketch.get(), depth=self.innerHeight)

        tunnelCutPlane = self.getPart().faces.findAt(((0.001, 0, 0.001),),)[0]
        tunnelCutEdge = self.getPart().edges.findAt(
            ((self.length/2, 0, self.wide),),)[0]
        print(tunnelCutEdge)
        tunnelCutTransform = self.getPart().MakeSketchTransform(sketchPlane=tunnelCutPlane, sketchUpEdge=tunnelCutEdge,
                                                                sketchPlaneSide=SIDE1, sketchOrientation=TOP, origin=(0.0, 0.0, 0.0))
        cutTunnelSketch = Sketch("MainTunnelSketch", tunnelCutTransform)
        cutTunnelSketch.get().rectangle((self.chamberThickness, self.wide/2-self.tunnelWidth/2),
                                        (self.length - self.chamberThickness*3, self.wide/2+self.tunnelWidth/2))
        self.getPart().CutExtrude(sketchPlane=tunnelCutPlane,
                                  sketchPlaneSide=SIDE1, sketchUpEdge=tunnelCutEdge, sketchOrientation=TOP, sketch=cutTunnelSketch.get(), depth=self.tunnelHeight)

    def getParameters(self):
        return {
            "length": self.length,
            "wide": self.wide,
            "height": self.height,
            "chamberNum": self.chamberNum,
            "chamberSize": self.chamberSize,
            "chamberHeight": self.chamberHeight,
            "chamberThickness": self.chamberThickness,
            "innerHeight": self.innerHeight,
            "space": self.space,
            "tunnelWidth": self.tunnelWidth,
            "tunnelHeight": self.tunnelHeight,
            "tunnelLength": self.tunnelLength
        }


class GripperPart(Object):
    def __init__(self, name, bodyPart, instances=[], original=SUPPRESS, keepIntersections=ON):
        super(GripperPart, self).__init__(name)
        self.parameters = bodyPart.getParameters()
        self.createMergedPart(instances, original, keepIntersections)
        self.innerCavity = "{}_Cavity".format(name)

    def createMergedPart(self, instances, original, keepIntersections):
        # print(list(map(lambda instance: instance.getName(), instances)))
        assembly.InstanceFromBooleanMerge(
            name=self.partName,
            instances=(
                list(map(lambda instance: instance.get(), instances))),
            originalInstances=original,
            keepIntersections=keepIntersections,
            domain=GEOMETRY)

    def setPaperSkin(self, paperSurface, section):

        self.getPart().Skin(faces=paperSurface, name='Skin-Paper')
        paperRegion = self.getPart().Set(skinFaces=(('Skin-Paper', paperSurface), ),
                                         name='Set-Skin')
        self.getPart().SectionAssignment(region=paperRegion,
                                         sectionName=section.getName(),
                                         offset=0.0,
                                         offsetType=MIDDLE_SURFACE,
                                         offsetField='',
                                         thicknessAssignment=FROM_SECTION)

    def defineInstance(self, part):
        return Instances("{}-1".format(self.partName), part)

    def getParameters(self):
        return self.parameters

    def getInnerCavitySurfaces(self):
        print(self.parameters["chamberThickness"])
        InnerSurfCavity = self.getPart().faces.getByBoundingBox(
            self.parameters["chamberThickness"], 0.0, self.parameters["chamberThickness"],
            self.parameters["length"] -
            self.parameters["chamberThickness"], self.parameters["tunnelHeight"], self.parameters["wide"] -
            self.parameters["chamberThickness"])
        InnerSurfCavity += self.getPart().faces.getByBoundingBox(
            self.parameters["chamberThickness"], 0.0, self.parameters["chamberThickness"],
            self.parameters["length"] -
            self.parameters["chamberThickness"], self.parameters["innerHeight"], self.parameters["wide"] - self.parameters["chamberThickness"])
        self.getPart().Surface(side1Faces=InnerSurfCavity,
                               name=self.innerCavity)
        return self.getPart().surfaces[self.innerCavity]

    def getInnerCavity(self):
        return self.innerCavity

    def mesh(self, seedSize):
        region = self.getPart().cells.getByBoundingBox(-9999, -
                                                       9999, -9999, 9999, 9999, 9999)
        self.getPart().setMeshControls(regions=region, elemShape=TET, technique=FREE)
        elemType1 = mesh.ElemType(elemCode=C3D20R, elemLibrary=STANDARD)
        elemType2 = mesh.ElemType(elemCode=C3D15, elemLibrary=STANDARD)
        elemType3 = mesh.ElemType(elemCode=C3D10H, elemLibrary=STANDARD)
        self.getPart().setElementType(regions=self.getPart().sets['Main_set'],
                                      elemTypes=(elemType1, elemType2, elemType3))
        self.getPart().setElementType(regions=self.getPart().sets['Base-A_set'],
                                      elemTypes=(elemType1, elemType2, elemType3))
        self.getPart().setElementType(regions=self.getPart().sets['Base-B_set'],
                                      elemTypes=(elemType1, elemType2, elemType3))
        self.getPart().seedPart(size=seedSize, deviationFactor=0.1, minSizeFactor=0.1)
        self.getPart().generateMesh()
        elemType4 = mesh.ElemType(elemCode=S8R, elemLibrary=STANDARD)
        elemType5 = mesh.ElemType(elemCode=STRI65, elemLibrary=STANDARD)
        skinRegions = self.getPart().sets['Set-Skin']
        self.getPart().setElementType(regions=skinRegions, elemTypes=(elemType4, elemType5))
# Process code


Elastosil = Material("Elastosil", 1.13e-09, "elastosil")
Paper = Material("Paper", 7.5e-10, "paper")

ElastosilSection = Section("Sec-Elastosil", Elastosil, "solid")
PaperSection = Section("Sec-Paper", Paper, "shell", 0.1)

BaseA = BasePart("Base-A", 95, 10, 1)
BaseA.assignSection(ElastosilSection)
BaseB = BasePart("Base-B", 95, 10, 1)
BaseB.assignSection(ElastosilSection)

Main = MainPart("Main", 31, 10, 10, 2, 15, 7, 2, 0.0, 1, 9, 5, 1)
Main.assignSection(ElastosilSection)
Base1 = Instances("Base-1", BaseA)
Base1.translate((0.0, -BaseA.getParameters()["thickness"], 0.0))
Base2 = Instances("Base-2", BaseB)
Base2.translate((0.0, -BaseB.getParameters()["thickness"]*2, 0.0))
Main1 = Instances("Main-1", Main)

Gripper = GripperPart("Gripper", Main, [Base1, Base2, Main1])

paperSurface = Gripper.selectSurfaceByPos(Main.getParameters(
)["length"] / 2, -BaseA.getParameters()["thickness"], Main.getParameters(
)["wide"] / 2)

Gripper.setPaperSkin(paperSurface, PaperSection)
GripperInstance = Gripper.defineInstance(Gripper)

GravityStep = Step("gravity")
GravityStep.addGravity()
GripperInnerCavity = Gripper.getInnerCavitySurfaces()

fixedFace = Assembly.createFace(GripperInstance, 0.0, Main.getParameters(
)["height"]/2, Main.getParameters()["wide"]/2, "BCFaceFixed")
fixedSet = Assembly.createSet(fixedFace, "fixedSet")

GravityStep.addBC(fixedSet)

PressureStep = Step("pressure", GravityStep)
InnerCavitySurface = Assembly.selectFace(
    GripperInstance, Gripper.getInnerCavity())
PressureStep.addPressure(InnerCavitySurface, 0.05)
PressureStep.createContact("Chamber Walls", Main, GripperInstance)
assembly.regenerate()
Gripper.mesh(5)
mdb.Job(name="Job",
        model=currentModel,
        description='',
        type=ANALYSIS,
        atTime=None,
        waitMinutes=0,
        waitHours=0,
        queue=None,
        memory=90,
        memoryUnits=PERCENTAGE,
        getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE,
        nodalOutputPrecision=SINGLE,
        echoPrint=OFF,
        modelPrint=OFF,
        contactPrint=OFF,
        historyPrint=OFF,
        userSubroutine='',
        scratch='',
        resultsFormat=ODB,
        multiprocessingMode=DEFAULT,
        numCpus=1,
        numGPUs=0)
mdb.jobs["Job"].submit(consistencyChecking=OFF)
