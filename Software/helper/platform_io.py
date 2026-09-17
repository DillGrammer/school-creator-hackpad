import os,sys,subprocess,pathlib,time
class NotReady(Exception):pass

def foreground():
 if sys.platform=='win32':
  import ctypes,psutil
  pid=ctypes.c_ulong();ctypes.windll.user32.GetWindowThreadProcessId(ctypes.windll.user32.GetForegroundWindow(),ctypes.byref(pid))
  return pid.value,psutil.Process(pid.value).name()
 if sys.platform=='darwin':
  from AppKit import NSWorkspace
  app=NSWorkspace.sharedWorkspace().frontmostApplication();return app.processIdentifier(),str(app.localizedName())
 raise NotReady('Mac or Windows required')
def launch(target):
 if not target:raise NotReady('Set app in Setup')
 if sys.platform=='darwin':subprocess.Popen(['open','-a',target])
 elif sys.platform=='win32':os.startfile(target)
 else:raise NotReady('Unsupported OS')
def reveal(path):
 path=str(pathlib.Path(path).resolve())
 if sys.platform=='darwin':subprocess.Popen(['open','-R',path])
 elif sys.platform=='win32':subprocess.Popen(['explorer.exe','/select,',path])
def type_text(text):
 # Unicode injection; do not use clipboard or press Enter.
 from pynput.keyboard import Controller
 Controller().type(text)
def shortcut(keys):
 import pyautogui
 if not isinstance(keys,list) or not keys or len(keys)>5:raise NotReady('Configure shortcut')
 pyautogui.hotkey(*keys)
def screenshot(config, destination):
 import mss,mss.tools
 with mss.mss() as sct:
  region=config.get('capture_region')
  if not region:
   if sys.platform=='win32':
    import ctypes
    from ctypes import wintypes
    r=wintypes.RECT();ctypes.windll.user32.GetWindowRect(ctypes.windll.user32.GetForegroundWindow(),ctypes.byref(r))
    region={'left':r.left,'top':r.top,'width':r.right-r.left,'height':r.bottom-r.top}
   elif sys.platform=='darwin':
    import Quartz
    pid,_=foreground()
    windows=Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly|Quartz.kCGWindowListExcludeDesktopElements,Quartz.kCGNullWindowID)
    for w in windows:
     if w.get('kCGWindowOwnerPID')==pid and w.get('kCGWindowLayer')==0:
      b=w['kCGWindowBounds'];region={'left':int(b['X']),'top':int(b['Y']),'width':int(b['Width']),'height':int(b['Height'])};break
  if not region:raise NotReady('Choose capture region in Setup')
  shot=sct.grab(region);mss.tools.to_png(shot.rgb,shot.size,output=str(destination))
 return pathlib.Path(destination)
def selected_files():
 # File dialogs provide an explicit selection when no supported selection source exists.
 if sys.platform=='win32':
  import win32com.client,ctypes
  hwnd=ctypes.windll.user32.GetForegroundWindow()
  for w in win32com.client.Dispatch('Shell.Application').Windows():
   try:
    if w.HWND==hwnd:return [pathlib.Path(i.Path) for i in w.Document.SelectedItems() if i.IsFileSystem]
   except Exception:continue
 return []
def ssh(alias,host="",user=""):
 if not alias:
  import re
  if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,252}",host or "") or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}",user or ""):raise NotReady("Set Pi host/user or SSH alias")
  alias=user+"@"+host
 import re
 if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.@-]{0,320}',alias or ''):raise NotReady('Set SSH alias in Setup')
 if sys.platform=='win32':subprocess.Popen(['wt.exe','ssh',alias])
 elif sys.platform=='darwin':
  # Launch an executable terminal document containing only a validated SSH alias.
  import tempfile
  fd,path=tempfile.mkstemp(prefix='hackpad-ssh-',suffix='.command')
  with os.fdopen(fd,'w') as f:f.write('#!/bin/sh\nexec ssh '+alias+'\n')
  os.chmod(path,0o700);subprocess.Popen(['open','-a','Terminal',path])
