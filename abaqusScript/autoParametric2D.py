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
autoComputeMode = getWarningReply(
    message='Tinh toan tu dong dua tren thong so da cai dat?',
    buttons=(YES, NO))
fields = (
    ('Chieu day nap:', '3.5'),
    ('Chieu cao:', '12'),
    ('Do day dau tay gap:', '6.5'),
    ('Do day cuoi tay gap:', '4'),
    ('Chieu dai cac khoang:', '5'),
    ('Chieu dai khoang dau:', '10'),
    ('Chieu dai khoang cuoi:', '15.0'),
    ('Khoang cach giua cac khoang:', '1'),
    ('Chieu cao cac ranh:', '9'),
    ('So luong khoang giua:', '10'),
    ('Do day tuong bao cac khoang:', '1.5'),
    ('Do day dinh khoang:', '2'),
    ('Do day lop giay:', '0.1'),
    ('Ap suat:', '0.01'),
)
#Ibase_thickness, Iwall_height, Iwall_boundariesThickness_head, Iwall_boundariesThickness_tail, Ichamber_size, Ichamber_fisrtLength, Ichamber_lastLength, Ichamber_space, Ichamber_height, Ichamber_num, Ichamber_wallThickness, Ichamber_upperCoverThickness, Iskin_thickness, Ipressure = 0
if autoComputeMode == NO:
    Ibase_thickness, Iwall_height, Iwall_boundariesThickness_head, Iwall_boundariesThickness_tail, Ichamber_size, Ichamber_fisrtLength, Ichamber_lastLength, Ichamber_space, Ichamber_height, Ichamber_num, Ichamber_wallThickness, Ichamber_upperCoverThickness, Iskin_thickness, Ipressure = getInputs(
        fields=fields,
        label='Thong so tay gap:',
        dialogTitle='Tao tay gap',
    )
infoFields = (
    ('So luong CPU duoc phep hoat dong:', '2'),
    ('So luong GPU duoc phep hoat dong:', '1'),
    ('% RAM duoc phep su dung:', '90'),
)
ICPUs, IGPUs, IRAMs = getInputs(
    fields=infoFields,
    label='Thong so cau hinh:',
    dialogTitle='Cau hinh mo phong',
)
result_dir, result_name = getInputs(
    fields=(("Vi tri luu ket qua:", "D:\\"), ("Ten file:",
                                              "displacement_data")),
    label='Nhap duong dan den vi tri luu ket qua:',
    dialogTitle='Cau hinh luu tru',
)

resultFile = open(str(result_dir + result_name + ".csv"), "w")

instanceNum = 5
if autoComputeMode == NO:
    instanceNum = 1

for n in range(instanceNum):
    mdb.Model(name='Model-{}'.format(n + 1), modelType=STANDARD_EXPLICIT)

    base_length = None
    base_thickness = 2.5
    wall_length = None
    wall_height = 12
    wall_boundariesThickness_head = 6.5
    wall_boundariesThickness_tail = 4
    chamber_size = 5 + n
    chamber_fisrtLength = 10.0
    chamber_lastLength = 15.0
    chamber_space = 1
    chamber_height = 9
    chamber_num = 3
    chamber_wallThickness = 1
    chamber_tunnelWidth = 2
    chamber_tunnelHeight = 0
    chamber_upperCoverThickness = 2
    chamber_underCoverThickness = 1

    chamber_baseHeight = wall_height - chamber_height
    skin_thickness = 0.1
    pressure = 0.01

    seedSize = 3

    if autoComputeMode == NO:
        base_length = None
        base_thickness = float(Ibase_thickness)
        wall_length = None
        wall_height = float(Iwall_height)
        wall_boundariesThickness_head = float(Iwall_boundariesThickness_head)
        wall_boundariesThickness_tail = float(Iwall_boundariesThickness_tail)
        chamber_size = float(Ichamber_size)
        chamber_fisrtLength = float(Ichamber_fisrtLength)
        chamber_lastLength = float(Ichamber_lastLength)
        chamber_space = float(Ichamber_space)
        chamber_height = float(Ichamber_height)
        chamber_num = int(Ichamber_num)
        chamber_wallThickness = float(Ichamber_wallThickness)
        chamber_upperCoverThickness = float(Ichamber_upperCoverThickness)
        chamber_tunnelHeight = 0
        chamber_baseHeight = wall_height - chamber_height
        skin_thickness = float(Iskin_thickness)
        pressure = float(Ipressure)

    CPUs = int(ICPUs)
    GPUs = int(IGPUs)
    ram = int(IRAMs)

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
    mdb.models[str('Model-{}'.format(n + 1))].HomogeneousSolidSection(
        name='Sec-Paper', material='Paper', thickness=None)

    mainBodySketch = mdb.models[str(
        'Model-{}'.format(n + 1))].ConstrainedSketch(name='__profile__',
                                                     sheetSize=200.0)

    #Out boundaries

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

    # Inner boundaries
    mainBodySketch.Line(point1=(0.0, 0.0),
                        point2=(wall_boundariesThickness_head, 0.0))
    mainBodySketch.Line(point1=(wall_boundariesThickness_head, 0.0),
                        point2=(wall_boundariesThickness_head,
                                wall_height - chamber_upperCoverThickness))
    mainBodySketch.Line(point1=(wall_boundariesThickness_head,
                                wall_height - chamber_upperCoverThickness),
                        point2=(chamber_fisrtLength - chamber_wallThickness,
                                wall_height - chamber_upperCoverThickness))
    mainBodySketch.Line(point1=(chamber_fisrtLength - chamber_wallThickness,
                                wall_height - chamber_upperCoverThickness),
                        point2=(chamber_fisrtLength - chamber_wallThickness,
                                chamber_tunnelHeight))

    for i in range(chamber_num):
        mainBodySketch.Line(
            point1=(chamber_fisrtLength - chamber_wallThickness +
                    chamber_size * i + chamber_space * i,
                    chamber_tunnelHeight),
            point2=(chamber_fisrtLength + chamber_wallThickness +
                    chamber_size * i + chamber_space * (i + 1),
                    chamber_tunnelHeight))
        mainBodySketch.Line(
            point1=(chamber_fisrtLength + chamber_wallThickness +
                    chamber_size * i + chamber_space * (i + 1),
                    chamber_tunnelHeight),
            point2=(chamber_fisrtLength + chamber_wallThickness +
                    chamber_size * i + chamber_space * (i + 1),
                    wall_height - chamber_upperCoverThickness))
        mainBodySketch.Line(
            point1=(chamber_fisrtLength + chamber_wallThickness +
                    chamber_size * i + chamber_space * (i + 1),
                    wall_height - chamber_upperCoverThickness),
            point2=(chamber_fisrtLength - chamber_wallThickness +
                    chamber_size * (i + 1) + chamber_space * (i + 1),
                    wall_height - chamber_upperCoverThickness))
        mainBodySketch.Line(
            point1=(chamber_fisrtLength - chamber_wallThickness +
                    chamber_size * (i + 1) + chamber_space * (i + 1),
                    wall_height - chamber_upperCoverThickness),
            point2=(chamber_fisrtLength - chamber_wallThickness +
                    chamber_size * (i + 1) + chamber_space * (i + 1),
                    chamber_tunnelHeight))

    mainBodySketch.Line(
        point1=(chamber_fisrtLength - chamber_wallThickness + chamber_size *
                (chamber_num) + chamber_space * (chamber_num),
                chamber_tunnelHeight),
        point2=(base_length + chamber_wallThickness - chamber_lastLength,
                chamber_tunnelHeight))
    mainBodySketch.Line(
        point1=(base_length + chamber_wallThickness - chamber_lastLength,
                chamber_tunnelHeight),
        point2=(base_length + chamber_wallThickness - chamber_lastLength,
                wall_height - chamber_upperCoverThickness))
    mainBodySketch.Line(
        point1=(base_length + chamber_wallThickness - chamber_lastLength,
                wall_height - chamber_upperCoverThickness),
        point2=(base_length - wall_boundariesThickness_tail,
                wall_height - chamber_upperCoverThickness))
    mainBodySketch.Line(point1=(base_length - wall_boundariesThickness_tail,
                                wall_height - chamber_upperCoverThickness),
                        point2=(base_length - wall_boundariesThickness_tail,
                                0.0))
    mainBodySketch.Line(point1=(base_length - wall_boundariesThickness_tail,
                                0.0),
                        point2=(base_length, 0.0))

    mainBodySketch.setPrimaryObject(STANDALONE)

    mainBodyPart = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Main-Body', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    mainBodyPart = mdb.models[str('Model-{}'.format(n + 1))].parts['Main-Body']
    mainBodyPart.BaseShell(sketch=mainBodySketch)
    mainBodySketch.unsetPrimaryObject()
    del mdb.models[str('Model-{}'.format(n + 1))].sketches['__profile__']

    mainBodyFaces = mainBodyPart.faces.findAt(((0, 0, 0), ), )
    mainBodyRegion = mainBodyPart.Set(faces=mainBodyFaces,
                                      name='Set-Main-Body')
    mainBodyPart.SectionAssignment(region=mainBodyRegion,
                                   sectionName='Sec-Elastosil',
                                   offset=0.0,
                                   offsetType=MIDDLE_SURFACE,
                                   offsetField='',
                                   thicknessAssignment=FROM_SECTION)

    # Paper
    PaperSketch = mdb.models[str('Model-{}'.format(n + 1))].ConstrainedSketch(
        name='__profile__', sheetSize=200.0)
    PaperSketch.rectangle(point1=(0.0, 0.0),
                          point2=(base_length, skin_thickness))
    PaperPart = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Paper', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    PaperPart = mdb.models[str('Model-{}'.format(n + 1))].parts['Paper']
    PaperPart.BaseShell(sketch=PaperSketch)
    PaperFaces = PaperPart.faces.findAt(((0, 0, 0), ), )
    PaperRegion = PaperPart.Set(faces=PaperFaces, name='Set-Paper')
    PaperPart.SectionAssignment(region=PaperRegion,
                                sectionName='Sec-Paper',
                                offset=0.0,
                                offsetType=MIDDLE_SURFACE,
                                offsetField='',
                                thicknessAssignment=FROM_SECTION)

    # Base

    BaseSketchA = mdb.models[str('Model-{}'.format(n + 1))].ConstrainedSketch(
        name='__profile__', sheetSize=200.0)
    BaseSketchA.rectangle(point1=(0.0, 0.0),
                          point2=(base_length,
                                  base_thickness - skin_thickness))

    # extrude base in 3D and Deformable
    # Base-A

    BaseAPart = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Base-A', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    BaseAPart = mdb.models[str('Model-{}'.format(n + 1))].parts['Base-A']
    BaseAPart.BaseShell(sketch=BaseSketchA)

    BaseAFaces = BaseAPart.faces.findAt(((0, 0, 0), ), )
    BaseARegion = BaseAPart.Set(faces=BaseAFaces, name='Set-Base-A')
    BaseAPart.SectionAssignment(region=BaseARegion,
                                sectionName='Sec-Elastosil',
                                offset=0.0,
                                offsetType=MIDDLE_SURFACE,
                                offsetField='',
                                thicknessAssignment=FROM_SECTION)

    # Base-B

    BaseSketchB = mdb.models[str('Model-{}'.format(n + 1))].ConstrainedSketch(
        name='__profile__', sheetSize=200.0)
    BaseSketchB.rectangle(point1=(0.0, 0.0),
                          point2=(base_length, base_thickness))

    BaseBPart = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Base-B', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    BaseBPart = mdb.models[str('Model-{}'.format(n + 1))].parts['Base-B']
    BaseBPart.BaseShell(sketch=BaseSketchB)
    BaseBFaces = BaseBPart.faces.findAt(((0, 0, 0), ), )
    BaseBRegion = BaseBPart.Set(faces=BaseBFaces, name='Set-Base-B')
    BaseBPart.SectionAssignment(region=BaseBRegion,
                                sectionName='Sec-Elastosil',
                                offset=0.0,
                                offsetType=MIDDLE_SURFACE,
                                offsetField='',
                                thicknessAssignment=FROM_SECTION)
    BaseBEdge = BaseBPart.edges.findAt(
        ((base_length / 2, base_thickness, 0), ), )
    BaseBPart.Surface(side1Edges=BaseBEdge, name='Top-of-B')
    # Clean Base sketch
    del mdb.models[str('Model-{}'.format(n + 1))].sketches['__profile__']

    # create Assembly
    a = mdb.models[str('Model-{}'.format(n + 1))].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    a.Instance(name='Base-A', part=BaseAPart, dependent=ON)
    a.Instance(name='Base-B', part=BaseBPart, dependent=ON)
    a.Instance(name='Main-Body', part=mainBodyPart, dependent=ON)
    a.Instance(name='Paper', part=PaperPart, dependent=ON)
    a.translate(instanceList=('Base-A', ),
                vector=(0.0, -base_thickness + skin_thickness, 0.0))
    a.translate(instanceList=('Base-B', ),
                vector=(0.0, -(base_thickness * 2), 0.0))
    a.translate(instanceList=('Paper', ), vector=(0.0, -base_thickness, 0.0))
    SingleInstances_List = mdb.models[str(
        'Model-{}'.format(n + 1))].rootAssembly.instances.keys()
    a.InstanceFromBooleanMerge(name='Merged-Body',
                               instances=([
                                   a.instances[SingleInstances_List[i]]
                                   for i in range(len(SingleInstances_List))
                               ]),
                               originalInstances=SUPPRESS,
                               domain=GEOMETRY,
                               keepIntersections=ON)
    MergedBody = mdb.models[str('Model-{}'.format(n + 1))].parts['Merged-Body']
    #Select InnerSurface
    InnerSurfCavity = MergedBody.edges.findAt(
        ((wall_boundariesThickness_head +
          (chamber_fisrtLength - chamber_wallThickness -
           wall_boundariesThickness_head) / 2, 0.0, 0.0), ), )
    InnerSurfCavity += MergedBody.edges.findAt(
        ((base_length - wall_boundariesThickness_tail -
          (chamber_lastLength - wall_boundariesThickness_tail -
           chamber_wallThickness) / 2, 0.0, 0.0), ), )
    InnerSurfCavity += MergedBody.edges.getByBoundingBox(
        wall_boundariesThickness_head,
        wall_height - chamber_upperCoverThickness, 0.0,
        base_length - wall_boundariesThickness_tail,
        wall_height - chamber_upperCoverThickness, 0.0)
    InnerSurfCavity += MergedBody.edges.findAt(
        ((wall_boundariesThickness_head,
          (wall_height - chamber_upperCoverThickness) / 2 +
          chamber_tunnelHeight / 2, 0.0), ), )
    InnerSurfCavity += MergedBody.edges.findAt(
        ((base_length - wall_boundariesThickness_tail,
          (wall_height - chamber_upperCoverThickness) / 2 +
          chamber_tunnelHeight / 2, 0.0), ), )
    for i in range(chamber_num + 1):
        InnerSurfCavity += MergedBody.edges.findAt(
            ((chamber_fisrtLength - chamber_wallThickness +
              (chamber_space + chamber_size) * i,
              (wall_height - chamber_upperCoverThickness) / 2 +
              chamber_tunnelHeight / 2, 0.0), ), )
    for i in range(chamber_num + 1):
        InnerSurfCavity += MergedBody.edges.findAt(
            ((chamber_fisrtLength + chamber_wallThickness + chamber_space *
              (i + 1) + chamber_size * i,
              (wall_height - chamber_upperCoverThickness) / 2 +
              chamber_tunnelHeight / 2, 0.0), ), )
    for i in range(chamber_num):
        InnerSurfCavity += MergedBody.edges.findAt(
            ((chamber_fisrtLength + chamber_wallThickness + chamber_space *
              (i + 1) + chamber_size * i +
              (chamber_size - chamber_wallThickness * 2) / 2, 0.0, 0.0), ), )

    MergedBody.Surface(side1Edges=InnerSurfCavity, name='Surf-Inner Cavity')
    a.regenerate()

    # Create Gravity Step
    # mdb.models[str('Model-{}'.format(n + 1))].StaticStep(name='Step-Gravity',
    #                                                      previous='Initial',
    #                                                      nlgeom=ON)
    # Create Gravity

    # mdb.models[str('Model-{}'.format(n + 1))].Gravity(
    #     name='Gravity',
    #     createStepName='Step-Gravity',
    #     comp2=-9810.0,
    #     distributionType=UNIFORM,
    #     field='',
    #     region=None)

    # Create Fixed Boundaries

    # fixedFace = a.instances['Merged-Body-1'].edges.findAt(
    #     ((0.0, wall_height / 2, 0.0), ), )
    # fixedFaceRegion = a.Set(edges=fixedFace, name='Set-FixedFace')
    # mdb.models[str('Model-{}'.format(n + 1))].EncastreBC(
    #     name='Fixed End',
    #     createStepName='Step-Gravity',
    #     region=fixedFaceRegion,
    #     localCsys=None)
    # Create Pressure Step and Pressure Load
    InnerSurfCavityRegion = a.instances['Merged-Body-1'].surfaces[
        'Surf-Inner Cavity']
    mdb.models[str('Model-{}'.format(n + 1))].StaticStep(name='Step-Pressure',
                                                         previous='Initial',
                                                         nlgeom=ON)
    fixedFace = a.instances['Merged-Body-1'].edges.findAt(
        ((0.0, wall_height / 2, 0.0), ), )
    fixedFaceRegion = a.Set(edges=fixedFace, name='Set-FixedFace')
    mdb.models[str('Model-{}'.format(n + 1))].EncastreBC(
        name='Fixed End',
        createStepName='Step-Pressure',
        region=fixedFaceRegion,
        localCsys=None)
    mdb.models[str('Model-{}'.format(n + 1))].Pressure(
        name='Load-Pressure',
        createStepName='Step-Pressure',
        region=InnerSurfCavityRegion,
        distributionType=UNIFORM,
        field='',
        magnitude=pressure,
        amplitude=UNSET)

    # Create walls contact
    mdb.models[str('Model-{}'.format(n + 1))].ContactProperty('Chamber Walls')
    mdb.models[str('Model-{}'.format(
        n + 1))].interactionProperties['Chamber Walls'].TangentialBehavior(
            formulation=FRICTIONLESS)
    contactFaces = a.instances['Merged-Body-1'].edges.findAt(
        ((chamber_fisrtLength,
          (wall_height - chamber_upperCoverThickness) / 2 +
          chamber_baseHeight / 2, 0.0), ), )
    for i in range(chamber_num + 1):
        contactFaces += a.instances['Merged-Body-1'].edges.findAt(
            ((chamber_fisrtLength + chamber_size * i + chamber_space * i,
              (wall_height - chamber_upperCoverThickness) / 2 +
              chamber_baseHeight / 2, 0.0), ), )
    for i in range(chamber_num + 1):
        contactFaces += a.instances['Merged-Body-1'].edges.findAt(
            ((chamber_fisrtLength + chamber_size * i + chamber_space * (i + 1),
              (wall_height - chamber_upperCoverThickness) / 2 +
              chamber_baseHeight / 2, 0.0), ), )
    contactFacesRegion = a.Surface(side1Edges=contactFaces,
                                   name='Surf-Contact')
    mdb.models[str('Model-{}'.format(n + 1))].SelfContactStd(
        name='Walls',
        createStepName='Step-Pressure',
        surface=contactFacesRegion,
        interactionProperty='Chamber Walls',
        thickness=ON)

    p = mdb.models[str('Model-{}'.format(n + 1))].parts['Merged-Body']
    # e = p.edges
    # edges = e.getSequenceFromMask(mask=('[#0:3 #4 ]', ), )
    # p.Stringer(edges=edges, name='Stringer-1')
    f = p.faces
    pickedRegions = f.getByBoundingBox(
        -9999, -9999, -9999, 9999, 9999,
        9999)  #findAt(((0.0,wall_height/2,0.0)))
    p.setMeshControls(regions=pickedRegions, elemShape=TRI)
    elemType1 = mesh.ElemType(elemCode=CPS8R, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=CPS6M,
                              elemLibrary=STANDARD,
                              secondOrderAccuracy=OFF,
                              distortionControl=DEFAULT)
    p.setElementType(regions=p.sets['Set-Main-Body'],
                     elemTypes=(elemType1, elemType2))
    p.setElementType(regions=p.sets['Set-Base-A'],
                     elemTypes=(elemType1, elemType2))
    p.setElementType(regions=p.sets['Set-Base-B'],
                     elemTypes=(elemType1, elemType2))
    p.setElementType(regions=p.sets['Set-Paper'],
                     elemTypes=(elemType1, elemType2))
    p.seedPart(size=seedSize, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()
    a.regenerate()
    all_nodes = p.nodes
    end_nodes = []
    for node_count in all_nodes:
        xcoord = node_count.coordinates[0]
        ycoord = node_count.coordinates[1]
        if xcoord > base_length - 0.0001 and ycoord < (-base_thickness *
                                                       2) + 0.0001:
            end_nodes.append(node_count)
            break
    good_left_nodes = mesh.MeshNodeArray(end_nodes)
    p.Set(nodes=good_left_nodes, name='Set-Node')
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].view.setViewpoint(viewVector=(0, 0, 1),
                                                       cameraUpVector=(0, 1,
                                                                       0))
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        loads=ON,
        bcs=ON,
        interactions=ON,
        predefinedFields=OFF,
        connectors=OFF)
    jobName = 'Job-{}'.format(n + 1)
    modelName = 'Model-{}'.format(n + 1)
    gripperSimulation = mdb.Job(name=jobName,
                                model=modelName,
                                description='',
                                type=ANALYSIS,
                                atTime=None,
                                waitMinutes=0,
                                waitHours=0,
                                queue=None,
                                memory=ram,
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
                                multiprocessingMode=THREADS,
                                numCpus=CPUs,
                                numDomains=CPUs,
                                numGPUs=GPUs)
    gripperSimulation.submit()
    gripperSimulation.waitForCompletion()
    myOdb = visualization.openOdb(path=str('Job-{}'.format(n + 1)) + '.odb')
    centerNSet = myOdb.rootAssembly.instances['MERGED-BODY-1'].nodeSets[
        "SET-NODE"]
    frame = myOdb.steps['Step-Pressure'].frames[-1]

    # Retrieve Y-displacement at the center of the plate.

    dispField = frame.fieldOutputs['U']
    dispSubField = dispField.getSubset(region=centerNSet)
    # disp = dispSubField.values[0].data[0]     # Get X displacement
    # disp = dispSubField.values[0].data[1]     # Get Y displacement
    disp = dispSubField.values[0].magnitude
    session.viewports['Viewport: 1'].setValues(displayedObject=myOdb)

    resultFile.write(str(str(disp) + "\n"))
resultFile.close()