from abaqus import *
from abaqusConstants import *
from odbAccess import *

# set viewport
session.Viewport(name='Viewport: 1',
                 origin=(0.0, 0.0),
                 width=265.680816650391,
                 height=126.907554626465)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
instanceNum = 1
for n in range(instanceNum):
    mdb.Model(name='Model-{}'.format(n + 1), modelType=STANDARD_EXPLICIT)
    extrude_width = 10.0
    base_width = 5.0
    base_length = None
    base_thickness = 2.5
    wall_length = None
    wall_height = 12
    wall_boundariesThickness_head = 6.5
    wall_boundariesThickness_tail = 4
    chamber_size = 5 + n * 0.05  # chieu rong khoang
    chamber_fisrtLength = 10.0
    chamber_lastLength = 15.0
    chamber_space = 1
    chamber_height = 9
    chamber_num = 3  # so khoang +2
    chamber_wallThickness = 0.5  # chieu day thanh
    chamber_tunnelWidth = 2
    chamber_tunnelHeight = 0
    chamber_upperCoverThickness = 2
    chamber_underCoverThickness = 0.5
    
    daythanh_khoang1 = 1
    distance_chamber_1 = 5
    dai_khoang1 = 6
    cao_khoanng = 6


    chamber_baseHeight = wall_height - chamber_height
    skin_thickness = 0.1
    pressure = 0.01

    # Mesh

    seedSize = 3

    ###

    # CPUs = int(ICPUs)
    # GPUs = int(IGPUs)
    # ram = int(IRAMs)
    CPUs = 4
    GPUs = 1
    ram = 90
    if base_length == None:
        base_length = chamber_fisrtLength + chamber_lastLength + chamber_size * chamber_num + chamber_space * (
            chamber_num + 1)
        wall_length = base_length

    # import CAE library Abaqus
   
    from caeModules import *
    from driverUtils import executeOnCaeStartup

    # Create material
    mdb.models[str('Model-{}'.format(n + 1))].Material(name='Paper')
    mdb.models[str('Model-{}'.format(n + 1))].materials['Paper'].Density(
        table=((7.5e-10, ), ))
    mdb.models[str(
        'Model-{}'.format(n + 1))].materials['Paper'].Elastic(table=((6500.0,
                                                                      0.2), ))
    mdb.models[str('Model-{}'.format(n + 1))].Material(name='Elastosil')
    mdb.models[str('Model-{}'.format(n + 1))].materials['Elastosil'].Density(
        table=((1.13e-09, ), ))
    mdb.models[str(
        'Model-{}'.format(n + 1))].materials['Elastosil'].Hyperelastic(
            materialType=ISOTROPIC,
            testData=OFF,
            type=YEOH,
            volumetricResponse=VOLUMETRIC_DATA,
            table=((0.11, 0.02, 0.0, 0.0, 0.0, 0.0), ))
    mdb.models[str('Model-{}'.format(n + 1))].HomogeneousSolidSection(
        name='Sec-Elastosil', material='Elastosil', thickness=None)
    mdb.models[str('Model-{}'.format(n + 1))].HomogeneousShellSection(
        name='Sec-Paper',
        preIntegrate=OFF,
        material='Paper',
        thicknessType=UNIFORM,
        thickness=0.1,
        thicknessField='',
        idealization=NO_IDEALIZATION,
        poissonDefinition=DEFAULT,
        thicknessModulus=None,
        temperature=GRADIENT,
        useDensity=OFF,
        integrationRule=SIMPSON,
        numIntPts=5)

    # create sketch for base
    baseSketch = mdb.models[str('Model-{}'.format(n + 1))].ConstrainedSketch(
        name='__profile__', sheetSize=200.0)
    baseSketch.rectangle(point1=(0.0, 0.0), point2=(base_length, base_thickness))

    # extrude base in 3D and Deformable
    # Base-A
    baseABlock = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Base-A', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    baseABlock = mdb.models[str('Model-{}'.format(n + 1))].parts['Base-A']
    baseABlock.BaseSolidExtrude(sketch=baseSketch, depth=extrude_width)

    # Assign section Base_A

    baseACell = baseABlock.cells.findAt(((0.0, 0.0, 0.0), ), )
    baseARegion = baseABlock.Set(cells=baseACell, name='Set-Base-A')
    baseABlock.SectionAssignment(region=baseARegion,
                                 sectionName='Sec-Elastosil',
                                 offset=0.0,
                                 offsetType=MIDDLE_SURFACE,
                                 offsetField='',
                                 thicknessAssignment=FROM_SECTION)

    # Base-B

    baseBBlock = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Base-B', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    baseBBlock = mdb.models[str('Model-{}'.format(n + 1))].parts['Base-B']
    baseBBlock.BaseSolidExtrude(sketch=baseSketch, depth=extrude_width)

    # Assign section Base_B

    baseBCell = baseBBlock.cells.findAt(((0.0, 0.0, 0.0), ), )
    baseBRegion = baseBBlock.Set(cells=baseBCell, name='Set-Base-B')
    baseBBlock.SectionAssignment(region=baseBRegion,
                                 sectionName='Sec-Elastosil',
                                 offset=0.0,
                                 offsetType=MIDDLE_SURFACE,
                                 offsetField='',
                                 thicknessAssignment=FROM_SECTION)

    side1Faces = baseBBlock.faces.findAt(
        ((base_length / 2, base_width / 2, base_thickness), ), )
    baseBBlock.Surface(side1Faces=side1Faces, name='Top of B')

    # Mainbody_3D
    
    mainBodySketch = mdb.models[str('Model-{}'.format(n + 1))].ConstrainedSketch(
        name='__profile__',
        sheetSize=200.0)
    mainBodySketch.Line(point1=(0.0, 0.0), point2=(0.0, wall_height))
    mainBodySketch.Line(point1=(0.0, wall_height),
                        point2=(chamber_fisrtLength, wall_height))
    mainBodySketch.Line(point1=(chamber_fisrtLength, wall_height),
                        point2=(chamber_fisrtLength, chamber_baseHeight))

    for i in range(chamber_num):
        mainBodySketch.Line(
            point1=(chamber_fisrtLength + chamber_size * i + chamber_space * i,
                    chamber_baseHeight),
            point2=(chamber_fisrtLength + chamber_size * i + chamber_space *
                    (i + 1), chamber_baseHeight))
        mainBodySketch.Line(point1=(chamber_fisrtLength + chamber_size * i +
                                    chamber_space * (i + 1),
                                    chamber_baseHeight),
                            point2=(chamber_fisrtLength + chamber_size * i +
                                    chamber_space * (i + 1), wall_height))
        mainBodySketch.Line(point1=(chamber_fisrtLength + chamber_size * i +
                                    chamber_space * (i + 1), wall_height),
                            point2=(chamber_fisrtLength + chamber_size *
                                    (i + 1) + chamber_space * (i + 1),
                                    wall_height))
        mainBodySketch.Line(point1=(chamber_fisrtLength + chamber_size *
                                    (i + 1) + chamber_space * (i + 1),
                                    wall_height),
                            point2=(chamber_fisrtLength + chamber_size *
                                    (i + 1) + chamber_space * (i + 1),
                                    chamber_baseHeight))

    mainBodySketch.Line(point1=(chamber_fisrtLength + chamber_size *
                                (chamber_num) + chamber_space * (chamber_num),
                                chamber_baseHeight),
                        point2=(base_length - chamber_lastLength,
                                chamber_baseHeight))
    mainBodySketch.Line(point1=(base_length - chamber_lastLength,
                                chamber_baseHeight),
                        point2=(base_length - chamber_lastLength, wall_height))
    mainBodySketch.Line(point1=(base_length - chamber_lastLength, wall_height),
                        point2=(base_length, wall_height))
    mainBodySketch.Line(point1=(base_length, wall_height),
                        point2=(base_length, 0.0))
    mainBodySketch.Line(
        point1= (base_length,0.0),
        point2=(0.0,0.0))
    
    mainBodySketch.setPrimaryObject(STANDALONE)

    mainBodyPart = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Main-Body', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    mainBodyPart = mdb.models[str('Model-{}'.format(n + 1))].parts['Main-Body']
    mainBodyPart.BaseSolidExtrude(sketch=mainBodySketch,depth=extrude_width)
    del mdb.models[str('Model-{}'.format(n + 1))].sketches['__profile__']
    p = mdb.models['Model-1'].parts['Main-Body']
    f, e = p.faces, p.edges
    t = p.MakeSketchTransform(sketchPlane=f[19], sketchUpEdge=e[3], 
    sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(22.0, 0.0, 5.0))
    s = mdb.models[str('Model-{}'.format(n + 1))].ConstrainedSketch(name='__profile__', 
            sheetSize=90.24, gridSpacing=2.25, transform=t)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=SUPERIMPOSE)
    p = mdb.models[str('Model-{}'.format(n + 1))].parts['Main-Body']
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.rectangle(point1=(-base_length/2+distance_chamber_1, -extrude_width/2+daythanh_khoang1),
        point2=(-base_length/2+distance_chamber_1+dai_khoang1, extrude_width/2-daythanh_khoang1))
    
    p = mdb.models[str('Model-{}'.format(n + 1))].parts['Main-Body']
    f1, e1 = p.faces, p.edges
    p.CutExtrude(sketchPlane=f1[19], sketchUpEdge=e1[3], sketchPlaneSide=SIDE1, 
        sketchOrientation=RIGHT, sketch=s, depth=cao_khoanng, flipExtrudeDirection=OFF)
        
    s.unsetPrimaryObject()
    del mdb.models['Model-1'].sketches['__profile__']

     
    











    

    
    

    
    





