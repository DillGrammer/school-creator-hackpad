"""Create the matched Hackpad enclosure in Autodesk Fusion.
Prepared design; do not treat exports as print-verified until fit checks are complete.
All dimensions below are millimetres. Fusion's internal length unit is cm.
"""
import adsk.core, adsk.fusion, math, pathlib, traceback, json
OUT=pathlib.Path(__file__).resolve().parent.parent
W,H=86.5,88.5
CLEARANCE,WALL,FLOOR=.4,2.4,2.4
PCB_BOTTOM,PCB_THICKNESS=14.5,1.6
PLATE_THICKNESS,SWITCH_PLATE_HEIGHT=1.5,5.0
CONTROL_HEIGHT=14.0
INSERT_PILOT,INSERT_LENGTH=4.6,4.0 # Assumes M3 x OD5 x L4 kit inserts; test fit required.
HOLES=[(4.5,4.5),(82,29.5),(4.5,84),(82,84)]
KEYS=[(x,y) for y in (43.5,76) for x in (15.5,43.25,71)]
NEW=adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN=adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT=adsk.fusion.FeatureOperations.CutFeatureOperation

def pt(x,y,z=0):return adsk.core.Point3D.create(x/10,-y/10,z/10)
def val(v):return adsk.core.ValueInput.createByReal(v/10)
def sketch(comp,z,name):
 pi=comp.constructionPlanes.createInput();pi.setByOffset(comp.xYConstructionPlane,val(z));plane=comp.constructionPlanes.add(pi)
 sk=comp.sketches.add(plane);sk.name=name;return sk

def rect(sk,x1,y1,x2,y2):sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(x1,y1),pt(x2,y2))
def rounded(sk,x1,y1,x2,y2,r):
 ls=sk.sketchCurves.sketchLines;ar=sk.sketchCurves.sketchArcs
 for a,b in [((x1+r,y1),(x2-r,y1)),((x2,y1+r),(x2,y2-r)),((x2-r,y2),(x1+r,y2)),((x1,y2-r),(x1,y1+r))]:ls.addByTwoPoints(pt(*a),pt(*b))
 for center,start in [((x2-r,y1+r),(x2-r,y1)),((x2-r,y2-r),(x2,y2-r)),((x1+r,y2-r),(x1+r,y2)),((x1+r,y1+r),(x1,y1+r))]:ar.addByCenterStartSweep(pt(*center),pt(*start),-math.pi/2)
def extrude(comp,sk,height,op,name):
 inp=comp.features.extrudeFeatures.createInput(sk.profiles.item(0),op);inp.setDistanceExtent(False,val(height));feat=comp.features.extrudeFeatures.add(inp);feat.name=name;sk.isVisible=False;return feat

def box(comp,x1,y1,x2,y2,z,height,op,name,r=0):
 sk=sketch(comp,z,name+' sketch');rounded(sk,x1,y1,x2,y2,r) if r else rect(sk,x1,y1,x2,y2);return extrude(comp,sk,height,op,name)
def cyl(comp,x,y,z,r,height,op,name):
 sk=sketch(comp,z,name+' sketch');sk.sketchCurves.sketchCircles.addByCenterRadius(pt(x,y),r/10);return extrude(comp,sk,height,op,name)
def component(root,name):
 c=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component;c.name=name;return c

def run(context):
 app=adsk.core.Application.get();ui=app.userInterface
 try:
  design=adsk.fusion.Design.cast(app.activeProduct)
  if not design or design.rootComponent.bRepBodies.count or design.rootComponent.occurrences.count:
   app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
   design=adsk.fusion.Design.cast(app.activeProduct)
  design.designIntent=adsk.fusion.DesignIntentTypes.HybridDesignIntentType
  design.designType=adsk.fusion.DesignTypes.ParametricDesignType
  root=design.rootComponent
  base=component(root,'Base');top=component(root,'Cover')
  bt=PCB_BOTTOM+PCB_THICKNESS;ptop=bt+5;pb=ptop-1.5;ht=bt+14;seat=ptop-3;e=2.8
  box(base,-e,-e,W+e,H+e,0,pb,NEW,'Base outer shell',4)
  box(base,-.4,-.4,W+.4,H+.4,2.4,pb,CUT,'Base cavity',1)
  for i,(x,y) in enumerate(HOLES):
   cyl(base,x,y,2.4,4,PCB_BOTTOM-2.4,JOIN,'Support '+str(i+1))
   cyl(base,x,y,1.7,1.7,PCB_BOTTOM,CUT,'Screw clearance '+str(i+1))
   cyl(base,x,y,PCB_BOTTOM-4.2,2.3,4.3,CUT,'Insert pilot '+str(i+1))
  box(base,68.5,-e-1,82.5,1,bt-1,8,CUT,'USB opening')
  box(top,-e,-e,W+e,H+e,pb,1.5,NEW,'MX plate',4)
  box(top,-e,-e,W+e,33.5,ptop,ht-ptop,JOIN,'Control hood',4)
  box(top,-.4,-.4,W+.4,31.1,pb-.1,ht-1.5-pb+.1,CUT,'Hood cavity',1)
  for i,(x,y) in enumerate(HOLES):
   ceiling=ht if y<33 else ptop
   cyl(top,x,y,bt,4,ceiling-bt,JOIN,'PCB clamp '+str(i+1))
   cyl(top,x,y,bt-.1,1.7,ceiling-bt+.2,CUT,'M3 through '+str(i+1))
   cyl(top,x,y,seat,3.3,ceiling-seat+.1,CUT,'Screw well '+str(i+1))
  for i,(x,y) in enumerate(KEYS):box(top,x-7.1,y-7.1,x+7.1,y+7.1,pb-.1,1.7,CUT,'MX opening '+str(i+1))
  cyl(top,15.75,16,ht-1.6,3.75,1.7,CUT,'Encoder shaft')
  box(top,25.6,9.6,64.4,22.4,ht-1.6,1.7,CUT,'OLED window')
  box(top,68.5,-e-1,82.5,1,pb-.1,bt+7-pb+.1,CUT,'USB cover clearance')
  report={}
  for comp in [base,top]:
   if comp.bRepBodies.count!=1:raise RuntimeError(comp.name+' is not one body')
   b=comp.bRepBodies.item(0);bb=b.boundingBox
   report[comp.name]={'volume_mm3':b.volume*1000,'solid':b.isSolid,'size_mm':[(bb.maxPoint.x-bb.minPoint.x)*10,(bb.maxPoint.y-bb.minPoint.y)*10,(bb.maxPoint.z-bb.minPoint.z)*10]}
   if not b.isSolid:raise RuntimeError('Non-solid body')
  # Optional knob retains the separately verified precise solid, named explicitly.
  knob=component(root,'Optional knob - imported solid')
  opts=app.importManager.createSTEPImportOptions(str(OUT/'Knob.step'))
  app.importManager.importToTarget(opts,knob)
  occurrence=root.occurrences.itemByName(knob.name+':1')
  transform=adsk.core.Matrix3D.create()
  transform.translation=adsk.core.Vector3D.create(1.575,-1.6,3.09)
  occurrence.transform2=transform
  if design.snapshots.hasPendingSnapshot:design.snapshots.add()
  bounds=occurrence.preciseBoundingBox
  assert abs(bounds.minPoint.z*10-30.9)<.001
  assert abs((bounds.minPoint.x+bounds.maxPoint.x)*5-15.75)<.001
  assert abs((bounds.minPoint.y+bounds.maxPoint.y)*5+16)<.001
  report['knob_bounds_mm']={'min':[bounds.minPoint.x*10,bounds.minPoint.y*10,bounds.minPoint.z*10],'max':[bounds.maxPoint.x*10,bounds.maxPoint.y*10,bounds.maxPoint.z*10]}
  report['coordinate_mapping']='CAD (x,-y,z) from KiCad top-view (x,y)'
  report['knob_bottom_mm']=30.9
  report['knob_to_hood_clearance_mm']=0.8
  report['timeline_features']=design.timeline.count
  cam=app.activeViewport.camera
  cam.eye=adsk.core.Point3D.create(15,-20,20);cam.target=adsk.core.Point3D.create(4.325,-4.425,1.5);cam.upVector=adsk.core.Vector3D.create(0,0,1);cam.isFitView=True;app.activeViewport.camera=cam
  app.activeViewport.fit()
  export=design.exportManager
  if not export.execute(export.createFusionArchiveExportOptions(str(OUT/'Hackpad_Case.f3d'))):raise RuntimeError('Archive export failed')
  (OUT/'Fusion-checks.json').write_text(json.dumps(report,indent=2))
  app.activeViewport.saveAsImageFile(str(OUT/'Fusion-preview.png'),1600,1100)
  ui.messageBox('Hackpad_Case.f3d exported. Base and Cover have editable sketches and features.')
 except:
  (OUT/'Fusion-error.txt').write_text(traceback.format_exc());ui.messageBox(traceback.format_exc())
