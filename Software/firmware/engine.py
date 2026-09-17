"""Portable menu/input state machine; identical code runs in desktop tests and CircuitPython."""
COURSES = ['math','english','philosophy','american_history','internet_literacy','sls']
COURSE_LABELS = ['Math','Eng','Phil','AMH','ILit','SLS']
ROWS = [
 [('D2L','d2l'),('MyLab','mylab'),('Desmos','desmos'),('Answer','quick_answer'),('Help','math_help'),('Add','add')],
 [('D2L','d2l'),('Khan','khan'),('Vocab','vocabulary'),('Mail','outlook'),('Answer','quick_answer'),('Add','add')],
 [('D2L','d2l'),('Book','textbook'),('Answer','quick_answer'),('Copy','copy'),('Help','help'),('Add','add')],
 [('D2L','d2l'),('Book','textbook'),('Word','word_web'),('Help','help'),('Copy','copy'),('Add','add')],
 [('D2L','d2l'),('Answer','quick_answer'),('Shot','screenshot_folder'),('File','file_folder'),('Rename','rename'),('Add','add')],
 [('D2L','d2l'),('CARES','cares'),('Answer','quick_answer'),('Mail','outlook'),('Copy','copy'),('Add','add')]]
class Engine:
 def __init__(self, emit, last_os='mac'):
  self.emit=emit; self.os=last_os; self.page='boot'; self.root=0; self.course=0
  self.index=0 if last_os=='mac' else 1; self.stack=[]; self.generation=0
  self.down={}; self.consumed=set(); self.chord=False; self.redone=False
  self.options=[]; self.title=''; self.folder_kind=''; self.trim_edge='end'
 def roots(self): return ['Courses','Creator']+(['Gaming'] if self.os=='windows' else [])+['Apps','More']
 def send(self,action,**kw):
  data={'action':action,'os':self.os,'generation':self.generation,'course':COURSES[self.course]}; data.update(kw); self.emit(data)
 def enter(self,page,title='',options=None):
  self.stack.append((self.page,self.index,self.title,self.options));self.page=page;self.index=0;self.title=title;self.options=options or [];self.generation+=1
 def back(self):
  self.send('cancel')
  if self.stack:self.page,self.index,self.title,self.options=self.stack.pop();self.generation+=1
 def labels(self):
  if self.page=='course':return [x[0] for x in ROWS[self.course]]
  if self.page=='folders':return COURSE_LABELS
  if self.page=='capcut':return ['TextFX','Import','Undo','Vol','Trim','Export']
  if self.page=='root':
   return {'Courses':COURSE_LABELS,'Creator':['CapCut','Image','Caption','Upload','',''],'Apps':['Msg','ChatGPT','Term','Web','User','Organ'], 'More':['Pi SSH','Setup','OS','','',''],'Gaming':['Fort','Valor','Discrd','Spotify','Next','Prev']}[self.roots()[self.root]]
  return []
 def key(self,k,pressed,now):
  if pressed:
   self.down[k]=(now,self.generation);self.consumed.discard(k)
   if k==3:self.redone=False
   return
  info=self.down.pop(k,None)
  if self.chord:
   if not self.down:self.chord=False;self.consumed.clear()
   return
  if not info or k in self.consumed or info[1]!=self.generation:
   self.consumed.discard(k);return
  if k==0:self.click();return
  if self.page=='capcut' and k==3 and self.redone:return
  self.tap(k)
 def tick(self,now):
  if self.page=='capcut' and 3 in self.down and not self.redone and now-self.down[3][0]>=.6:
   self.send('capcut.redo');self.redone=True
 def encoder_pressed(self,now):
  # Called after all six debounced key states have been processed.
  if 6 in self.down:
   self.chord=True;self.consumed.update([0,6]);self.down[0]=(now,self.generation);self.back()
  else:self.key(0,True,now)
 def rotate(self,delta):
  if 6 in self.down or self.chord:return
  if self.page=='boot':self.index=(self.index+delta)%2
  elif self.page=='selector':self.index=(self.index+delta)%len(self.options)
  elif self.page=='root':self.root=(self.root+delta)%len(self.roots());self.generation+=1
  elif self.page=='gaming':self.send('gaming.volume',delta=delta)
  elif self.page=='capcut':
   mode='scrub'
   if 4 in self.down:mode='volume';self.consumed.add(4)
   elif 5 in self.down:mode='trim';self.consumed.add(5)
   self.send('capcut.'+mode,delta=delta,edge=self.trim_edge)
  elif self.page=='adjust':self.send('capcut.'+self.title,delta=delta,edge=self.trim_edge)
 def click(self):
  if self.page=='boot':
   self.os=['mac','windows'][self.index];self.page='root';self.root=0;self.stack=[];self.generation+=1;self.send('os_changed')
  elif self.page=='selector':
   action=self.options[self.index][1]
   if action.startswith('adjust:'):
    self.trim_edge=action.split(':')[1];self.enter('adjust','trim')
   elif action.startswith('selector:'):self.select(action.split(':')[1])
   else:self.send(action)
  elif self.page=='root' and self.roots()[self.root]=='Gaming':self.enter('gaming','Gaming')
  elif self.page=='capcut':self.send('capcut.play_pause')
  elif self.page=='adjust':self.back()
 def select(self,kind):
  opts={'add':[('Assignment','organizer.assignment'),('Event','organizer.event')],
   'text':[('Text','capcut.text'),('Transition','capcut.transition')],
   'import':[('Selected','capcut.import_selected'),('Recent','capcut.import_recent'),('Photos','selector:photos')],
   'photos':[('Open Photos','open.photos'),('Import chosen','capcut.import_photos')],
   'trim':[('Start','adjust:start'),('End','adjust:end')]}
  self.enter('selector',kind,opts[kind])
 def tap(self,k):
  if not 1<=k<=6:return
  if self.page=='root':
   root=self.roots()[self.root]
   if root=='Courses':self.course=k-1;self.enter('course',COURSE_LABELS[self.course])
   elif root=='Creator':
    if k==1:self.enter('capcut','CapCut');self.send('open.capcut')
    elif k<=4:self.send(['','', 'open.image_ai','creator.caption','creator.upload'][k])
   elif root=='Gaming':
    self.enter('gaming','Gaming');self.send('gaming.'+['fortnite','valorant','discord','spotify','next','previous'][k-1])
   elif root=='Apps':self.send('app.'+['messages','chatgpt','terminal','browser','username','organizer'][k-1])
   elif root=='More':
    if k==1:self.send('app.ssh')
    elif k==2:self.send('app.setup')
    elif k==3:self.enter('boot','OS');self.index=0 if self.os=='mac' else 1
  elif self.page=='gaming':self.send('gaming.'+['fortnite','valorant','discord','spotify','next','previous'][k-1])
  elif self.page=='course':
   action=ROWS[self.course][k-1][1]
   if action=='add':self.select('add')
   elif action in ('screenshot_folder','file_folder'):
    self.folder_kind=action;self.send('capture.prepare',kind=action);self.enter('folders','Folder')
   else:self.send('course.'+action)
  elif self.page=='folders':self.send('folder.save',folder=COURSES[k-1],kind=self.folder_kind)
  elif self.page=='capcut':
   if k==1:self.select('text')
   elif k==2:self.select('import')
   elif k==3:self.send('capcut.undo')
   elif k==4:self.enter('adjust','volume')
   elif k==5:self.select('trim')
   elif k==6:self.send('capcut.export')
