
#NOTE These are used as placeholder for format strings, not empty dictionaries
width = {width}
height = {height}
depth = {depth}
unit = {unit}
material = {material}

empty_dict = {}

with Transaction():
    cg = ExtAPI.DataModel.Project.Model.AddConstructionGeometry()
    
    solid = cg.AddSolid()
    dims = [width,height,depth]
    solid.X2, solid.Y2, solid.Z2 = [Quantity(d, unit) for d in dims]
    
    solid.AddGeometry()
    
    block = Model.Geometry.Children[0]
    Model.Materials.Import(material)
    block.Material = "Structural Steel"
    geo_bod = block.Children[0].GetGeoBody()
    faces = geo_bod.Faces
    
    x_centroids, y_centroids, z_centroids = [list(col) for col in zip(*[face.Centroid for face in faces])]
    
    tol = 1e-4
    
    fixed_face = [face for face in faces if (abs(face.Centroid[2] - min(z_centroids)) < tol)].pop()
    force_face = [face for face in faces if (abs(face.Centroid[2] - max(z_centroids)) < tol)].pop()
    
    an = Model.Analyses[0]
    sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    
    sel.Ids = [fixed_face.Id]
    ExtAPI.SelectionManager.AddSelection(sel)
    an.AddFixedSupport()
    ExtAPI.SelectionManager.ClearSelection()
    
    sel.Ids = [force_face.Id]
    ExtAPI.SelectionManager.AddSelection(sel)
    force = an.AddForce()
    ExtAPI.SelectionManager.ClearSelection()
    
    force.DefineBy =  LoadDefineBy.Components
    force.YComponent.Inputs[0].DiscreteValues = [Quantity(1, "s")]
    force.YComponent.Output.DiscreteValues = [Quantity(-1000, "N")]
    
    Model.Mesh.ElementSize = Quantity(10,"mm")
    Model.Mesh.GenerateMesh()

Model.Analyses[0].Solve()

seqv = an.Solution.AddEquivalentStress()
ydef = an.Solution.AddDirectionalDeformation()
ydef.NormalOrientation =  NormalOrientationType.YAxis

an.Solution.EvaluateAllResults()