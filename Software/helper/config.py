import json,os,pathlib,sys
COURSES=['math','english','philosophy','american_history','internet_literacy','sls']
DEFAULT={
 'urls':{**{c+'.d2l':'' for c in COURSES},'math.mylab':'','math.desmos':'','english.khan':'','english.vocabulary':'','philosophy.textbook':'','american_history.textbook':'','word_web':'','sls.cares':'','outlook':'','organizer':'','math.help':'','philosophy.help':'','american_history.help':'','chatgpt':'https://chatgpt.com/','image_ai':'https://chatgpt.com/','tiktok_upload':'','instagram_upload':''},
 'folders':{**{c:'' for c in COURSES},'fitness':'','recent':'','logs':''},
 'apps':{'messages':'','browser':'','terminal':'','photos':'','capcut':'','fortnite':'','valorant':'','discord':'','spotify':''},
 'word_downloads_folder':'',
 'school_username':'','ssh_alias':'','ssh_host':'','ssh_user':'','serial_port':'','headset_microphone':'',
 'ai_model':'','ai_key_service':'hackpad-openai','capcut_process':'',
 'capcut_shortcuts':({'play_pause':['space'],'undo':['command','z'],'redo':['command','shift','z'],'import':['command','i'],'export':['command','e']} if sys.platform=='darwin' else {}),
 'browser_attach_enabled':False,'capture_region':None,'latest_export':'','audio_process_aliases':{}}
def location():
 base=pathlib.Path(os.getenv('APPDATA',str(pathlib.Path.home()))) if sys.platform=='win32' else pathlib.Path.home()/'Library'/'Application Support'
 return base/'Hackpad'/'settings.json'
def load(path=None):
 p=pathlib.Path(path) if path else location();d=json.loads(json.dumps(DEFAULT))
 if p.exists():
  saved=json.loads(p.read_text())
  for k,v in saved.items():
   if isinstance(v,dict) and isinstance(d.get(k),dict):d[k].update(v)
   else:d[k]=v
 return d

def save(d,path=None):
 p=pathlib.Path(path) if path else location();p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.replace(p)
