"""Desktop setup UI and serial helper. Run with Python 3.11+."""
import sys,pathlib,json,threading,queue,time,webbrowser,traceback
import tkinter as tk
from tkinter import ttk,filedialog,messagebox,simpledialog
from config import load,save,location
from actions import Actions
from platform_io import NotReady

class UI:
 def __init__(self):
  self.root=tk.Tk();self.root.title('Hackpad setup');self.root.geometry('800x640')
  self.config=load();self.questions=queue.Queue();self.entries={};self.log=tk.StringVar(value='Helper starting…')
  book=ttk.Notebook(self.root);book.pack(fill='both',expand=True)
  for group in ['urls','folders','apps','general','capcut_shortcuts']:
   outer=ttk.Frame(book);book.add(outer,text=group.replace('_',' ').title())
   canvas=tk.Canvas(outer);scroll=ttk.Scrollbar(outer,orient='vertical',command=canvas.yview);body=ttk.Frame(canvas)
   body.bind('<Configure>',lambda e,c=canvas:c.configure(scrollregion=c.bbox('all')))
   canvas.create_window((0,0),window=body,anchor='nw');canvas.configure(yscrollcommand=scroll.set);canvas.pack(side='left',fill='both',expand=True);scroll.pack(side='right',fill='y')
   values=self.config.get(group,{}) if group!='general' else {k:self.config[k] for k in ['school_username','ssh_alias','ssh_host','ssh_user','serial_port','headset_microphone','ai_model','capcut_process','latest_export','word_downloads_folder']}
   if group=='capcut_shortcuts':values={k:self.config['capcut_shortcuts'].get(k,[]) for k in ['play_pause','undo','redo','import','export','text','transition','scrub_left','scrub_right','volume_left','volume_right','trim_start_left','trim_start_right','trim_end_left','trim_end_right']}
   for row,(key,value) in enumerate(values.items()):
    ttk.Label(body,text=key.replace('_',' ')).grid(row=row,column=0,sticky='w',padx=8,pady=5)
    var=tk.StringVar(value=','.join(value) if isinstance(value,list) else value);self.entries[(group,key)]=var
    ttk.Entry(body,textvariable=var,width=58).grid(row=row,column=1,padx=4)
    if group in ('folders','apps') or key in ('latest_export','word_downloads_folder'):
     ttk.Button(body,text='Choose…',command=lambda v=var,g=('folders' if key=='word_downloads_folder' else group):self.browse(v,g)).grid(row=row,column=2)
  bar=ttk.Frame(self.root);bar.pack(fill='x');ttk.Button(bar,text='Import settings',command=self.import_settings).pack(side='left');ttk.Button(bar,text='Save settings',command=self.store).pack(side='left');ttk.Button(bar,text='Set AI key privately',command=self.key).pack(side='left')
  self.browser_enabled=tk.BooleanVar(value=self.config.get('browser_attach_enabled',False))
  ttk.Checkbutton(self.root,text='Use separate helper browser for attachments (sign-in required)',variable=self.browser_enabled).pack(anchor='w')
  ttk.Label(self.root,textvariable=self.log,wraplength=760).pack(fill='x',padx=8,pady=8)
  self.root.after(100,self.poll)
 def import_settings(self):
  path=filedialog.askopenfilename(title='Import your private settings.json',filetypes=[('JSON','*.json')])
  if not path:return
  try:
   d=load(path)
   for (group,k),v in self.entries.items():
    value=d.get(k,'') if group=='general' else d.get(group,{}).get(k,'')
    v.set(','.join(value) if isinstance(value,list) else value)
   self.browser_enabled.set(bool(d.get('browser_attach_enabled',False)))
   save(d);self.config=d;self.log.set('Imported private settings. Folder paths can be chosen with Choose…')
  except Exception as e:messagebox.showerror('Import failed',str(e))
 def browse(self,var,group):
  p=filedialog.askdirectory() if group=='folders' else filedialog.askopenfilename()
  if p:var.set(p)
 def store(self):
  d=load()
  for (group,k),v in self.entries.items():
   if group=='general':d[k]=v.get()
   elif group=='capcut_shortcuts':d[group][k]=[x.strip() for x in v.get().split(',') if x.strip()]
   else:d[group][k]=v.get()
  d['browser_attach_enabled']=self.browser_enabled.get();save(d);self.config=d;self.log.set('Saved. Leave unknown settings blank; those actions will show Setup Needed.')
 def key(self):
  value=simpledialog.askstring('API key','OpenAI API key (saved in your OS credential store):',show='*')
  if value:
   import keyring
   keyring.set_password(self.config['ai_key_service'],'api_key',value)
 def ask(self,kind,value):
  reply=queue.Queue();self.questions.put((kind,value,reply));return reply.get()
 def draft(self,d):
  win=tk.Toplevel(self.root);win.title('Prepared ChatGPT draft — send it yourself')
  field=tk.Text(win,width=85,height=12);field.pack();field.insert('1.0',d['prompt'])
  def copy():self.root.clipboard_clear();self.root.clipboard_append(field.get('1.0','end-1c'))
  ttk.Button(win,text='Open same conversation',command=lambda:webbrowser.open(d['url'])).pack()
  ttk.Button(win,text='Copy draft',command=copy).pack()
  if d['image']:
   from platform_io import reveal
   ttk.Button(win,text='Show screenshot to attach',command=lambda:reveal(d['image'])).pack()
  ttk.Label(win,text='Attach the screenshot, paste the draft, then press Send in ChatGPT.').pack()
 def poll(self):
  try:
   while True:
    kind,v,q=self.questions.get_nowait();r=None
    if kind=='file':r=filedialog.askopenfilename(title=v)
    elif kind=='text':r=simpledialog.askstring('Hackpad',v)
    elif kind=='message':messagebox.showinfo('Hackpad',v)
    elif kind=='draft':self.draft(v)
    elif kind=='setup':self.root.deiconify();self.root.lift()
    elif kind=='log':self.log.set(v)
    q.put(r)
  except queue.Empty:pass
  self.root.after(100,self.poll)
 def report(self,text):self.questions.put(('log',text,queue.Queue()))

class Bridge:
 def __init__(self,ui):
  self.ui=ui;self.actions=Actions(ui.config,ui.ask);self.jobs=queue.Queue(maxsize=24);self.results=queue.Queue();self.epoch=0;self.generation=0;self.busy=False;self.lock=threading.Lock()
  threading.Thread(target=self.worker,daemon=True).start()
 def worker(self):
  while True:
   epoch,m=self.jobs.get()
   with self.lock:
    if epoch!=self.epoch:continue
    self.actions.cancelled.clear();self.actions.config=self.ui.config;self.busy=True
   try:
    if m.get('focus_pid'):
     from platform_io import foreground
     if foreground()[0]!=m['focus_pid']:raise NotReady('Focus changed; turn again')
    result=self.actions.dispatch(m)
   except NotReady as e:result=str(e)
   except Exception as e:result='Action error; see helper';self.ui.report(type(e).__name__+': '+str(e))
   finally:
    with self.lock:self.busy=False
   with self.lock:
    if epoch==self.epoch:self.results.put({'type':'result','version':1,'id':m['id'],'generation':m['generation'],'text':result})
 def cancel(self):
  with self.lock:self.epoch+=1;self.actions.cancelled.set()
 def ports(self):
  from serial.tools import list_ports
  chosen=self.ui.config.get('serial_port')
  return [chosen] if chosen else [p.device for p in list_ports.comports() if p.vid in (0x2886,0x239A,0x2E8A)]
 def run(self):
  import serial
  while True:
   for port in self.ports():
    try:
     with serial.Serial(port,115200,timeout=.1,write_timeout=.5) as s:
      self.session(s)
    except Exception as e:
     self.cancel();self.ui.report('Waiting for Hackpad: '+str(e))
   time.sleep(1)
 def session(self,s):
  rx=b'';seen=set();last_hello=time.monotonic();last_status=0;verified=False
  while True:
   data=s.read(512)
   if data:rx+=data
   if len(rx)>8192:raise ValueError('Oversized serial message')
   while b'\n' in rx:
    line,rx=rx.split(b'\n',1)
    try:m=json.loads(line)
    except ValueError:continue
    if not isinstance(m,dict) or m.get('version')!=1:continue
    if m.get('type')=='hello' and m.get('device')=='hackpad':
     verified=True;last_hello=time.monotonic();self.generation=m.get('generation',0)
     s.write(b'{"type":"ack","version":1}\n')
     self.ui.report('Connected on '+s.port)
    if m.get('type')=='action' and verified:
     if not isinstance(m.get('id'),int) or m['id'] in seen:continue
     if not isinstance(m.get('action'),str) or not isinstance(m.get('generation'),int):continue
     seen.add(m['id'])
     if len(seen)>2048:seen=set(sorted(seen)[-1024:])
     if m['action']=='cancel':self.cancel();continue
     actual='windows' if sys.platform=='win32' else 'mac'
     if m.get('os')!=actual:
      s.write((json.dumps({'type':'result','version':1,'id':m['id'],'generation':m['generation'],'text':'Wrong OS: '+actual})+'\n').encode());continue
     if m['action']=='gaming.volume':
      from platform_io import foreground
      m['focus_pid']=foreground()[0]
     if (self.busy or not self.jobs.empty()) and m['action'] not in ('gaming.volume',):
      s.write((json.dumps({'type':'result','version':1,'id':m['id'],'generation':m['generation'],'text':'Busy - finish/cancel'})+'\n').encode());continue
     try:self.jobs.put_nowait((self.epoch,m))
     except queue.Full:
      s.write((json.dumps({'type':'result','version':1,'id':m['id'],'generation':m['generation'],'text':'Busy - retry'})+'\n').encode())
   while not self.results.empty():s.write((json.dumps(self.results.get())+'\n').encode())
   now=time.monotonic()
   if verified and now-last_status>1:
    try:
     from windows_audio import snapshot
     status=snapshot(self.ui.config) if sys.platform=='win32' else {'app':'Mac','volume':None,'mic':None}
    except Exception:status={'app':'Unavailable','volume':None,'mic':None}
    status.update(type='status',version=1);s.write((json.dumps(status)+'\n').encode());last_status=now
   if now-last_hello>4:self.cancel();raise TimeoutError('Device disconnected')

if __name__=='__main__':
 ui=UI();bridge=Bridge(ui);threading.Thread(target=bridge.run,daemon=True).start();ui.root.mainloop()
