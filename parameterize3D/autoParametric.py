from abaqus import *
from abaqusConstants import *

# set viewport
session.Viewport(name='Viewport: 1',
                 origin=(0.0, 0.0),
                 width=265.680816650391,
                 height=126.907554626465)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
for n in range(2):
    mdb.Model(name='Model-{}'.format(n + 1), modelType=STANDARD_EXPLICIT)
    base_length = None
    base_width = 5.0
    base_thickness = 0.5
    wall_length = None
    wall_height = 10.0
    wall_thickness = 1.0
    chamber_size = 5.0
    chamber_fisrtLength = 10.0
    chamber_lastLength = 10.0
    chamber_height = 20
    chamber_num = n + 1
    chamber_wallThickness = 1.0
    chamber_tunnelWidth = 2
    chamber_tunnelHeight = 2
    chamber_upperCoverThickness = 0.5
    chamber_underCoverThickness = 0.5
    chamber_space = 5.0
    chamber_baseHeight = wall_height - chamber_height

    pressure = 0.055

    seedSize = 3

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
    baseSketch.rectangle(point1=(0.0, 0.0), point2=(base_length, base_width))
    # extrude base in 3D and Deformable
    # Base-A
    baseABlock = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Base-A', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    baseABlock = mdb.models[str('Model-{}'.format(n + 1))].parts['Base-A']
    baseABlock.BaseSolidExtrude(sketch=baseSketch, depth=base_thickness)

    # Assign section

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
    baseBBlock.BaseSolidExtrude(sketch=baseSketch, depth=base_thickness)

    # Assign section

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

    # create sketch for wall
    wallSketch = mdb.models[str('Model-{}'.format(n + 1))].ConstrainedSketch(
        name='__profile__', sheetSize=200.0)
    wallSketch.Line(point1=(wall_length, wall_height),
                    point2=(wall_length, 0.0))
    wallSketch.Line(point1=(wall_length, 0.0), point2=(0.0, 0.0))
    wallSketch.Line(point1=(0.0, wall_height), point2=(0.0, 0.0))
    wallSketch.Line(point1=(0.0, wall_height),
                    point2=(chamber_fisrtLength, wall_height))
    wallSketch.Line(point1=(chamber_fisrtLength, wall_height),
                    point2=(chamber_fisrtLength, chamber_baseHeight))
    wallSketch.Line(point1=(chamber_fisrtLength, chamber_baseHeight),
                    point2=(chamber_fisrtLength + chamber_space,
                            chamber_baseHeight))
    for i in range(int(chamber_num)):
        wallSketch.Line(point1=(chamber_fisrtLength + chamber_size * i +
                                chamber_space * (i + 1), chamber_baseHeight),
                        point2=(chamber_fisrtLength + chamber_size * i +
                                chamber_space * (i + 1), wall_height))
        wallSketch.Line(point1=(chamber_fisrtLength + chamber_size * i +
                                chamber_space * (i + 1), wall_height),
                        point2=(chamber_fisrtLength + chamber_size * (i + 1) +
                                chamber_space * (i + 1), wall_height))
        wallSketch.Line(point1=(chamber_fisrtLength + chamber_size * (i + 1) +
                                chamber_space * (i + 1), wall_height),
                        point2=(chamber_fisrtLength + chamber_size * (i + 1) +
                                chamber_space * (i + 1), chamber_baseHeight))
        wallSketch.Line(point1=(chamber_fisrtLength + chamber_size * (i + 1) +
                                chamber_space * (i + 2), chamber_baseHeight),
                        point2=(chamber_fisrtLength + chamber_size * (i + 1) +
                                chamber_space * (i + 1), chamber_baseHeight))
    wallSketch.Line(point1=(chamber_fisrtLength + chamber_size *
                            (chamber_num + 1) + chamber_space * chamber_num,
                            chamber_baseHeight),
                    point2=(chamber_fisrtLength + chamber_size *
                            (chamber_num + 1) + chamber_space * chamber_num,
                            wall_height))
    wallSketch.Line(point1=(chamber_fisrtLength + chamber_size *
                            (chamber_num + 1) + chamber_space * chamber_num,
                            wall_height),
                    point2=(wall_length, wall_height))

    # extrude base in 3D and Deformable
    wallBlock = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Wall', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    wallBlock = mdb.models[str('Model-{}'.format(n + 1))].parts['Wall']
    wallBlock.BaseSolidExtrude(sketch=wallSketch, depth=wall_thickness)

    # front wall
    frontWallSketch = mdb.models[str(
        'Model-{}'.format(n + 1))].ConstrainedSketch(name='__profile__',
                                                     sheetSize=200.0)
    frontWallSketch.rectangle(point1=(0.0, 0.0),
                              point2=(wall_height, base_width))
    # extrude base in 3D and Deformable
    frontWallBlock = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='FrontWall', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    frontWallBlock = mdb.models[str('Model-{}'.format(n +
                                                      1))].parts['FrontWall']
    frontWallBlock.BaseSolidExtrude(sketch=frontWallSketch,
                                    depth=chamber_wallThickness)
    # COVER
    # upper cover
    upperCoverSketch = mdb.models[str(
        'Model-{}'.format(n + 1))].ConstrainedSketch(name='__profile__',
                                                     sheetSize=200.0)
    upperCoverSketch.rectangle(point1=(0.0, 0.0),
                               point2=(chamber_fisrtLength, base_width))
    for i in range(int(chamber_num)):
        upperCoverSketch.rectangle(
            point1=(chamber_fisrtLength + chamber_space * (i + 1) +
                    chamber_size * i, 0.0),
            point2=(chamber_fisrtLength + chamber_space * (i + 1) +
                    chamber_size * (i + 1), base_width))
    upperCoverSketch.rectangle(
        point1=(chamber_fisrtLength + chamber_space * (chamber_num + 1) +
                chamber_size * chamber_num, 0.0),
        point2=(chamber_fisrtLength + chamber_space * (chamber_num + 1) +
                chamber_size * chamber_num + chamber_lastLength, base_width))
    # extrude base in 3D and Deformable
    upperCoverBlock = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='UpperCover', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    upperCoverBlock = mdb.models[str('Model-{}'.format(n +
                                                       1))].parts['UpperCover']
    upperCoverBlock.BaseSolidExtrude(sketch=upperCoverSketch,
                                     depth=chamber_upperCoverThickness)

    # tunnelWall cover
    tunnelWallSketch = mdb.models[str(
        'Model-{}'.format(n + 1))].ConstrainedSketch(name='__profile__',
                                                     sheetSize=200.0)
    for i in range(int(chamber_num) + 1):
        tunnelWallSketch.rectangle(
            point1=(chamber_fisrtLength + chamber_space * i + chamber_size * i,
                    0.0),
            point2=(chamber_fisrtLength + chamber_space * (i + 1) +
                    chamber_size * i, base_width))
    # extrude base in 3D and Deformable
    tunnelWallBlock = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='TunnelWall', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    tunnelWallBlock = mdb.models[str('Model-{}'.format(n +
                                                       1))].parts['TunnelWall']
    tunnelWallBlock.BaseSolidExtrude(sketch=tunnelWallSketch,
                                     depth=chamber_baseHeight)

    # tunnel
    tunnelSketch = mdb.models[str('Model-{}'.format(n + 1))].ConstrainedSketch(
        name='__profile__', sheetSize=200.0)
    tunnelSketch.rectangle(point1=(0.0, 0.0),
                           point2=(base_length - chamber_wallThickness * 2,
                                   chamber_tunnelWidth))
    # extrude base in 3D and Deformable
    tunnelBlock = mdb.models[str('Model-{}'.format(n + 1))].Part(
        name='Tunnel', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    tunnelBlock = mdb.models[str('Model-{}'.format(n + 1))].parts['Tunnel']
    tunnelBlock.BaseSolidExtrude(sketch=tunnelSketch,
                                 depth=chamber_tunnelHeight)

    # Chamber tunnel
    # chamberTunnelSketch = mdb.models[str(
    #     'Model-{}'.format(n + 1))].ConstrainedSketch(name='__profile__',
    #                                                  sheetSize=200.0)
    # chamberTunnelSketch.Line(point1=(0.0, 0.0), point2=(wall_height, 0.0))
    # chamberTunnelSketch.Line(point1=(wall_height, 0.0),
    #                          point2=(wall_height, base_width))
    # chamberTunnelSketch.Line(point1=(wall_height, base_width),
    #                          point2=(0.0, base_width))
    # chamberTunnelSketch.Line(point1=(0.0, base_width),
    #                          point2=(0.0,
    #                                  base_width / 2 + chamber_tunnelWidth / 2))
    # chamberTunnelSketch.Line(point1=(0.0,
    #                                  base_width / 2 + chamber_tunnelWidth / 2),
    #                          point2=(chamber_tunnelHeight,
    #                                  base_width / 2 + chamber_tunnelWidth / 2))
    # chamberTunnelSketch.Line(point1=(chamber_tunnelHeight,
    #                                  base_width / 2 + chamber_tunnelWidth / 2),
    #                          point2=(chamber_tunnelHeight,
    #                                  base_width / 2 - chamber_tunnelWidth / 2))
    # chamberTunnelSketch.Line(point1=(chamber_tunnelHeight,
    #                                  base_width / 2 - chamber_tunnelWidth / 2),
    #                          point2=(0.0,
    #                                  base_width / 2 - chamber_tunnelWidth / 2))
    # chamberTunnelSketch.Line(point1=(0.0,
    #                                  base_width / 2 - chamber_tunnelWidth / 2),
    #                          point2=(0.0, 0.0))

    # # extrude base in 3D and Deformable
    # chamberTunnelBlock = mdb.models[str('Model-{}'.format(n + 1))].Part(
    #     name='ChamberTunnel', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    # chamberTunnelBlock = mdb.models[str(
    #     'Model-{}'.format(n + 1))].parts['ChamberTunnel']
    # chamberTunnelBlock.BaseSolidExtrude(sketch=chamberTunnelSketch,
    #                                     depth=chamber_wallThickness)

    # clean sketch
    del mdb.models[str('Model-{}'.format(n + 1))].sketches['__profile__']
    # create Assembly
    a = mdb.models[str('Model-{}'.format(n + 1))].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    # import parts into assembly

    a.Instance(name='Base-A', part=baseABlock, dependent=ON)
    a.Instance(name='Base-B', part=baseBBlock, dependent=ON)
    a.Instance(name='Wall-1', part=wallBlock, dependent=ON)
    a.Instance(name='Wall-2', part=wallBlock, dependent=ON)
    a.Instance(name='FrontWall-1', part=frontWallBlock, dependent=ON)
    a.Instance(name='FrontWall-2', part=frontWallBlock, dependent=ON)
    a.Instance(name='UpperCover', part=upperCoverBlock, dependent=ON)
    a.Instance(name='TunnelWall', part=tunnelWallBlock, dependent=ON)

    a.translate(instanceList=('Base-B', ),
                vector=(0.0, 0.0, -base_thickness * 2))
    a.translate(instanceList=('Base-A', ), vector=(0.0, 0.0, -base_thickness))
    a.Instance(name='ChamberTunnel_front', part=frontWallBlock, dependent=ON)
    a.Instance(name='ChamberTunnel_back', part=frontWallBlock, dependent=ON)
    a.rotate(instanceList=('Wall-1', 'Wall-2'),
             axisPoint=(0.0, 0.0, 0.0),
             axisDirection=(1.0, 0.0, 0.0),
             angle=90.0)
    a.translate(instanceList=('Wall-1', ), vector=(0.0, wall_thickness, 0.0))
    a.translate(instanceList=('Wall-2', ), vector=(0.0, base_width, 0.0))
    a.rotate(instanceList=('FrontWall-1', 'FrontWall-2'),
             axisPoint=(0.0, 0.0, 0.0),
             axisDirection=(0.0, 1.0, 0.0),
             angle=-90.0)
    a.translate(instanceList=('FrontWall-1', ),
                vector=(chamber_wallThickness, 0.0, 0.0))
    a.translate(instanceList=('FrontWall-2', ), vector=(base_length, 0.0, 0.0))
    a.translate(instanceList=('UpperCover', ),
                vector=(0.0, 0.0, wall_height - chamber_upperCoverThickness))
    a.translate(instanceList=('tunnelWall', ), vector=(0.0, 0.0, 0.0))
    a.rotate(instanceList=('ChamberTunnel_front', ),
             axisPoint=(0.0, 0.0, 0.0),
             axisDirection=(0.0, 1.0, 0.0),
             angle=-90.0)
    a.rotate(instanceList=('ChamberTunnel_back', ),
             axisPoint=(0.0, 0.0, 0.0),
             axisDirection=(0.0, 1.0, 0.0),
             angle=-90.0)
    a.translate(instanceList=('ChamberTunnel_front', ),
                vector=(chamber_fisrtLength, 0.0, 0.0))
    a.translate(instanceList=('ChamberTunnel_back', ),
                vector=(chamber_fisrtLength + chamber_space +
                        chamber_wallThickness, 0.0, 0.0))
    a.LinearInstancePattern(instanceList=('ChamberTunnel_front', ),
                            direction1=(1.0, 0.0, 0.0),
                            direction2=(0.0, 1.0, 0.0),
                            number1=int(chamber_num + 1),
                            number2=1,
                            spacing1=float(chamber_space + chamber_size),
                            spacing2=15.0)
    a.LinearInstancePattern(instanceList=('ChamberTunnel_back', ),
                            direction1=(1.0, 0.0, 0.0),
                            direction2=(0.0, 1.0, 0.0),
                            number1=int(chamber_num + 1),
                            number2=1,
                            spacing1=float(chamber_space + chamber_size),
                            spacing2=15.0)
    a.Instance(name='Tunnel', part=tunnelBlock, dependent=ON)
    a.translate(instanceList=('Tunnel', ),
                vector=(chamber_wallThickness,
                        base_width / 2 - chamber_tunnelWidth / 2, 0.0))
    #Merge Main body
    SingleInstances_List = mdb.models[str(
        'Model-{}'.format(n + 1))].rootAssembly.instances.keys()
    a.InstanceFromBooleanMerge(
        name='Main-Body-Uncut',
        instances=([
            a.instances[SingleInstances_List[i]]
            for i in range(2,
                           len(SingleInstances_List) - 1)
        ]),
        originalInstances=DELETE,
        domain=GEOMETRY)

    a.InstanceFromBooleanCut(
        name='Main-Body',
        instanceToBeCut=mdb.models[str(
            'Model-{}'.format(n +
                              1))].rootAssembly.instances['Main-Body-Uncut-1'],
        cuttingInstances=(a.instances['Tunnel'], ),
        originalInstances=DELETE)

    MainBodyBlock = mdb.models[str('Model-{}'.format(n +
                                                     1))].parts['Main-Body']
    MainBodyCell = MainBodyBlock.cells.findAt(
        ((0.0, 0.0, 0.0), ), )  #.getSequenceFromMask(mask=('[#1 ]', ), )
    MainBodyRegion = MainBodyBlock.Set(cells=MainBodyCell,
                                       name='Set-Main-Body')
    MainBodyBlock.SectionAssignment(region=MainBodyRegion,
                                    sectionName='Sec-Elastosil',
                                    offset=0.0,
                                    offsetType=MIDDLE_SURFACE,
                                    offsetField='',
                                    thicknessAssignment=FROM_SECTION)

    SingleInstances_List = mdb.models[str(
        'Model-{}'.format(n + 1))].rootAssembly.instances.keys()

    # Merge parts
    a.InstanceFromBooleanMerge(name='Merged-Body',
                               instances=([
                                   a.instances[SingleInstances_List[i]]
                                   for i in range(len(SingleInstances_List))
                               ]),
                               originalInstances=DELETE,
                               domain=GEOMETRY,
                               keepIntersections=ON)

    MergedBody = mdb.models[str('Model-{}'.format(n + 1))].parts['Merged-Body']
    PaperSurface = MergedBody.faces.findAt(
        ((base_length / 2, base_width / 2, -base_thickness), ), )
    MergedBody.Skin(faces=PaperSurface, name='Skin-Paper')

    PaperRegion = MergedBody.Set(skinFaces=(('Skin-Paper', PaperSurface), ),
                                 name='Set-Skin')
    MergedBody.SectionAssignment(region=PaperRegion,
                                 sectionName='Sec-Paper',
                                 offset=0.0,
                                 offsetType=MIDDLE_SURFACE,
                                 offsetField='',
                                 thicknessAssignment=FROM_SECTION)
    InnerSurfCavity = MergedBody.faces.getByBoundingBox(
        chamber_wallThickness, wall_thickness, 0.0,
        base_length - chamber_wallThickness, base_width - wall_thickness,
        chamber_tunnelHeight)
    InnerSurfCavity += MergedBody.faces.getByBoundingBox(
        chamber_wallThickness, wall_thickness, 0.0,
        base_length - chamber_wallThickness, wall_thickness,
        wall_height - chamber_upperCoverThickness)
    InnerSurfCavity += MergedBody.faces.getByBoundingBox(
        chamber_wallThickness, base_width - wall_thickness, 0.0,
        base_length - chamber_wallThickness, base_width - wall_thickness,
        wall_height - chamber_upperCoverThickness)
    InnerSurfCavity += MergedBody.faces.getByBoundingBox(
        chamber_wallThickness, wall_thickness,
        wall_height - chamber_upperCoverThickness,
        base_length - chamber_wallThickness, base_width - wall_thickness,
        wall_height - chamber_upperCoverThickness)
    InnerSurfCavity += MergedBody.faces.findAt(
        ((chamber_wallThickness, base_width / 2,
          (wall_height - chamber_upperCoverThickness) / 2 +
          chamber_tunnelHeight / 2), ), )
    InnerSurfCavity += MergedBody.faces.findAt(
        ((base_length - chamber_wallThickness, base_width / 2,
          (wall_height - chamber_upperCoverThickness) / 2 +
          chamber_tunnelHeight / 2), ), )
    for i in range(chamber_num + 1):
        InnerSurfCavity += MergedBody.faces.findAt(
            ((chamber_fisrtLength - chamber_wallThickness +
              (chamber_space + chamber_size) * i, base_width / 2,
              (wall_height - chamber_upperCoverThickness) / 2 +
              chamber_tunnelHeight / 2), ), )
    for i in range(chamber_num + 1):
        InnerSurfCavity += MergedBody.faces.findAt(
            ((chamber_fisrtLength + chamber_wallThickness + chamber_space *
              (i + 1) + chamber_size * i, base_width / 2,
              (wall_height - chamber_upperCoverThickness) / 2 +
              chamber_tunnelHeight / 2), ), )
    MergedBody.Surface(side1Faces=InnerSurfCavity, name='Surf-Inner Cavity')

    mdb.models[str('Model-{}'.format(n + 1))].StaticStep(name='Step-Gravity',
                                                         previous='Initial',
                                                         nlgeom=ON)
    mdb.models[str('Model-{}'.format(n + 1))].Gravity(
        name='Gravity',
        createStepName='Step-Gravity',
        comp3=-9810.0,
        distributionType=UNIFORM,
        field='',
        region=None)
    fixedFace = a.instances['Merged-Body-1'].faces.findAt(
        ((0.0, base_width / 2, wall_height / 2), ), )
    fixedFaceRegion = a.Set(faces=fixedFace, name='Set-FixedFace')
    mdb.models[str('Model-{}'.format(n + 1))].EncastreBC(
        name='Fixed End',
        createStepName='Step-Gravity',
        region=fixedFaceRegion,
        localCsys=None)
    InnerSurfCavityRegion = a.instances['Merged-Body-1'].surfaces[
        'Surf-Inner Cavity']
    mdb.models[str('Model-{}'.format(n + 1))].StaticStep(
        name='Step-Pressure', previous='Step-Gravity')
    mdb.models[str('Model-{}'.format(n + 1))].Pressure(
        name='Load-Pressure',
        createStepName='Step-Pressure',
        region=InnerSurfCavityRegion,
        distributionType=UNIFORM,
        field='',
        magnitude=pressure,
        amplitude=UNSET)

    mdb.models[str('Model-{}'.format(n + 1))].ContactProperty('Chamber Walls')
    mdb.models[str('Model-{}'.format(
        n + 1))].interactionProperties['Chamber Walls'].TangentialBehavior(
            formulation=FRICTIONLESS)
    contactFaces = a.instances['Merged-Body-1'].faces.findAt(
        ((chamber_fisrtLength, base_width / 2,
          (wall_height - chamber_upperCoverThickness) / 2 +
          chamber_tunnelHeight / 2), ), )
    for i in range(chamber_num + 1):
        contactFaces += a.instances['Merged-Body-1'].faces.findAt(
            ((chamber_fisrtLength + chamber_size * i + chamber_space * i,
              base_width / 2, (wall_height - chamber_upperCoverThickness) / 2 +
              chamber_tunnelHeight / 2), ), )
    for i in range(chamber_num + 1):
        contactFaces += a.instances['Merged-Body-1'].faces.findAt(
            ((chamber_fisrtLength + chamber_size * i + chamber_space *
              (i + 1), base_width / 2,
              (wall_height - chamber_upperCoverThickness) / 2 +
              chamber_tunnelHeight / 2), ), )
    contactFacesRegion = a.Surface(side1Faces=contactFaces,
                                   name='Surf-Contact')
    mdb.models[str('Model-{}'.format(n + 1))].SelfContactStd(
        name='Walls',
        createStepName='Step-Pressure',
        surface=contactFacesRegion,
        interactionProperty='Chamber Walls',
        thickness=ON)
    # MESH
    a.regenerate()
    p1 = mdb.models[str('Model-{}'.format(n + 1))].parts['Merged-Body']
    regionV = p1.cells.getByBoundingBox(-9999, -9999, -9999, 9999, 9999, 9999)
    # regionV += p1.vertices.findAt(
    #     ((0.0, base_width / 2, -base_thickness / 2), ), )
    # regionV += p1.vertices.findAt(
    #     ((0.0, base_width / 2, -base_thickness * 3 / 2), ), )
    #getByBoundingBox(-999, -999, -999, 999, 999,999)  #getSequenceFromMask(mask=('[#7 ]', ), )
    # pickedRegions = (region, )
    p1.setMeshControls(regions=regionV, elemShape=TET, technique=FREE)
    elemType1 = mesh.ElemType(elemCode=C3D20R, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=C3D15, elemLibrary=STANDARD)
    elemType3 = mesh.ElemType(elemCode=C3D10H, elemLibrary=STANDARD)
    p1.setElementType(regions=p1.sets['Set-Main-Body'],
                      elemTypes=(elemType1, elemType2, elemType3))
    p1.setElementType(regions=p1.sets['Set-Base-A'],
                      elemTypes=(elemType1, elemType2, elemType3))
    p1.setElementType(regions=p1.sets['Set-Base-B'],
                      elemTypes=(elemType1, elemType2, elemType3))
    p1.seedPart(size=seedSize, deviationFactor=0.1, minSizeFactor=0.1)
    p1.generateMesh()
    elemType1 = mesh.ElemType(elemCode=S8R, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=STRI65, elemLibrary=STANDARD)
    pickedRegions = p1.sets['Set-Skin']
    p1.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))

    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        loads=ON,
        bcs=ON,
        interactions=ON,
        predefinedFields=OFF,
        connectors=OFF)
    mdb.Job(name=str('Job-{}'.format(n + 1)),
            model=str('Model-{}'.format(n + 1)),
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
    mdb.jobs[str('Job-{}'.format(n + 1))].submit(consistencyChecking=OFF)
