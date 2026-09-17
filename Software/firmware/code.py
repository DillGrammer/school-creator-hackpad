"""Copy this directory to CIRCUITPY with the libraries listed in README."""
import time,json,board,busio,digitalio,rotaryio,usb_cdc,microcontroller
import adafruit_ssd1306
from engine import Engine
try:
 with open('/device.json') as f:cfg=json.load(f)
except OSError:cfg={}
i2c=busio.I2C(board.D5,board.D4)
oled=adafruit_ssd1306.SSD1306_I2C(128,32,i2c,addr=cfg.get('oled_address',60))
pins=[]
for pin in [board.D0,board.D2,board.D6,board.D1,board.D3,board.D7,board.D8]:
 p=digitalio.DigitalInOut(pin);p.switch_to_input(pull=digitalio.Pull.UP);pins.append(p)
enc=rotaryio.IncrementalEncoder(board.D10,board.D9,divisor=cfg.get('encoder_divisor',4))
serial=usb_cdc.data;serial.timeout=0;serial.write_timeout=0
queue=[];rx=bytearray();seq=0;last_ping=0;last_host=-100;notice='';notice_until=0
status={};last_frame=None;last_page=None;title_until=0;title=''
def emit(msg):
 global seq,notice,notice_until
 seq+=1;msg.update(type='action',id=seq,version=1)
 if msg['action']=='os_changed':microcontroller.nvm[0]=1 if msg['os']=='windows' else 0
 if msg['action']=='cancel':
  notice_until=0
 if time.monotonic()-last_host>4:
  notice='Helper offline';notice_until=time.monotonic()+1.5;return
 if len(queue)<24:queue.append((json.dumps(msg)+'\n').encode())
 else:notice='Busy - retry';notice_until=time.monotonic()+1.5
engine=Engine(emit,'windows' if microcontroller.nvm[0]==1 else 'mac')
raw=[False]*7;stable=raw[:];changed=[0]*7;pos=enc.position;last_draw=0;tx=b''
def text(s,x,y):oled.text(''.join(c if 32<=ord(c)<127 else '?' for c in str(s))[:21],x,y,1)
def grid(labels):
 oled.vline(42,0,32,1);oled.vline(85,0,32,1);oled.hline(0,15,128,1)
 for i,l in enumerate(labels):
  # SSD1306 framebuffer font is 5px ink/6px advance with supplied font5x8.bin.
  x=[0,43,86][i%3];width=[42,42,42][i%3]
  text(l,x+max(0,(width-len(l)*6)//2),4+(i//3)*16)
def draw(now):
 oled.fill(0)
 if now<notice_until:
  text(notice[:21],0,0);text(notice[21:42],0,10);text(notice[42:63],0,20)
 elif now<title_until:text(title,0,12)
 elif engine.page=='boot':text('Choose computer',0,0);text(('> MAC' if engine.index==0 else '  MAC'),0,12);text(('> WINDOWS' if engine.index==1 else '  WINDOWS'),0,24)
 elif engine.page=='selector':
  text(engine.title.upper(),0,0);text('>'+engine.options[engine.index][0],0,12);text(str(engine.index+1)+'/'+str(len(engine.options)),0,24)
 elif engine.page=='adjust':text(engine.title.upper(),0,0);text('Turn to adjust',0,12);text('Click to finish',0,24)
 elif engine.page=='gaming' or (engine.page=='root' and engine.roots()[engine.root]=='Gaming'):
  app=status.get('app','Offline')[:13];text(app,17,1)
  # Simplified monochrome app glyphs; no color assets required.
  icon=status.get('icon','app')
  if icon=='spotify':
   oled.rect(0,1,14,13,1)
   for y,w in [(4,10),(7,8),(10,6)]:oled.hline(2,y,w,1)
  elif icon=='valorant':oled.line(1,2,7,13,1);oled.line(7,13,13,2,1)
  elif icon=='fortnite':text('F',4,3)
  elif icon=='discord':oled.rect(0,3,14,9,1);oled.pixel(4,7,1);oled.pixel(10,7,1)
  else:oled.rect(1,2,12,11,1)
  mute=status.get('mic')
  oled.rect(116,1,5,8,1);oled.line(113,7,113,11,1);oled.hline(113,11,11,1);oled.vline(118,11,4,1)
  if mute is True:oled.line(111,1,125,15,1)
  elif mute is None:text('?',106,0)
  vol=status.get('volume')
  if vol is None:text('No audio' if app!='Offline' else 'Helper offline',0,21)
  else:
   text(str(vol)+'%',0,22);oled.rect(30,22,98,8,1);oled.fill_rect(32,24,int(94*vol/100),4,1)
 else:grid(engine.labels())
 oled.show()
while True:
 now=time.monotonic()
 # Read all key transitions before encoder button so same-scan Back wins.
 for i,p in enumerate(pins):
  v=not p.value
  if v!=raw[i]:raw[i]=v;changed[i]=now
  if v!=stable[i] and now-changed[i]>=.02:
   stable[i]=v;title_until=0
   k=i+1 if i<6 else 0
   if k==0 and v:engine.encoder_pressed(now)
   else:engine.key(k,v,now)
 newpos=enc.position
 if newpos!=pos:
  engine.rotate((newpos-pos)*cfg.get('encoder_direction',1));pos=newpos;title_until=0
 engine.tick(now)
 tag=(engine.page,engine.root,engine.course)
 if tag!=last_page:
  if engine.page in ('root','course','capcut','gaming'):
   title=engine.roots()[engine.root] if engine.page=='root' else engine.title
   title_until=now+.7
  last_page=tag
 if now-last_host>4:status={}
 if serial.connected:
  if now-last_ping>1:
   ping={'type':'hello','device':'hackpad','version':1,'os':engine.os,'generation':engine.generation,'page':engine.page}
   if len(queue)<24:queue.append((json.dumps(ping)+'\n').encode())
   last_ping=now
  if not tx and queue:tx=queue.pop(0)
  if tx:
   try:
    n=serial.write(tx) or 0;tx=tx[n:]
   except OSError:tx=b''
  data=serial.read(256)
  if data:rx.extend(data)
  if len(rx)>4096:rx=bytearray()
  while b'\n' in rx:
   line,_,rx=rx.partition(b'\n');rx=bytearray(rx)
   try:
    msg=json.loads(line)
    if not isinstance(msg,dict) or msg.get('version')!=1:continue
    last_host=now
    if msg.get('type')=='status':status=msg
    elif msg.get('type')=='result' and msg.get('generation')==engine.generation:
     notice=str(msg.get('text',''))[:63]
     if notice:notice_until=now+3
   except (ValueError,TypeError):pass
 else:queue=[];tx=b'';rx=bytearray()
 if now-last_draw>.1:draw(now);last_draw=now
 time.sleep(.002)
