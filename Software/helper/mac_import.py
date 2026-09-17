"""Complete CapCut's native macOS import picker, with window/control checks.
The helper owns this automation at runtime; integration is not yet live-tested.
"""
import pathlib,time
from platform_io import NotReady,shortcut
from word_copy import SafariWord

class ImportPicker(SafariWord):
 def __init__(self,cancelled):
  import ApplicationServices as AX
  from AppKit import NSWorkspace
  self.ax=AX;self.workspace=NSWorkspace.sharedWorkspace();self.cancelled=cancelled
  app=self.workspace.frontmostApplication()
  if app.bundleIdentifier()!='com.lemon.lvoverseas':raise NotReady('Focus CapCut first')
  if not AX.AXIsProcessTrusted():raise NotReady('Allow helper Accessibility in System Settings')
  self.pid=app.processIdentifier();self.app=AX.AXUIElementCreateApplication(self.pid)
 def guard(self):
  if self.cancelled.is_set():raise NotReady('Cancelled')
  if self.workspace.frontmostApplication().processIdentifier()!=self.pid:raise NotReady('CapCut lost focus; retry')
 def identifier(self,name):
  deadline=time.monotonic()+5
  while time.monotonic()<deadline:
   self.guard();found=self.find(self.app,lambda e:self.attr(e,'AXIdentifier')==name)
   if len(found)==1:return found[0]
   self.cancelled.wait(.1)
  raise NotReady('Import dialog not ready: '+name)
 def fill(self,path):
  path=pathlib.Path(path).resolve()
  if not path.is_file():raise NotReady('Selected media no longer exists')
  self.identifier('open-panel')
  shortcut(['command','shift','g'])
  field=self.identifier('PathTextField')
  if self.ax.AXUIElementSetAttributeValue(field,'AXValue',str(path))!=0:raise NotReady('Cannot enter media path')
  shortcut(['enter'])
  panel=self.identifier('open-panel')
  deadline=time.monotonic()+5
  while time.monotonic()<deadline:
   self.guard()
   matches=self.find(panel,lambda e:self.attr(e,'AXSelected') and path.name in (self.attr(e,'AXTitle'),self.attr(e,'AXDescription'),self.attr(e,'AXIdentifier')))
   if len(matches)==1:
    self.press('Import',panel,'AXButton')
    deadline=time.monotonic()+10
    while time.monotonic()<deadline:
     self.guard()
     if not self.find(self.app,lambda e:self.attr(e,'AXIdentifier')=='open-panel'):return
     self.cancelled.wait(.1)
    raise NotReady('Import dialog did not close')
   self.cancelled.wait(.1)
  raise NotReady('Media selection could not be verified')

def complete_import(path,cancelled):ImportPicker(cancelled).fill(path)
