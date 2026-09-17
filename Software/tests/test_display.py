import unittest,ast,pathlib,sys,os
ROOT=pathlib.Path(__file__).resolve().parents[1];FW=ROOT/'firmware';sys.path[:0]=[str(FW),str(FW/'lib')]
from engine import Engine
import adafruit_framebuf
class DisplayTests(unittest.TestCase):
 def setUp(self):
  self.old=os.getcwd();os.chdir(FW)
  self.fb=adafruit_framebuf.FrameBuffer(bytearray(512),128,32);self.fb.show=lambda:None
  tree=ast.parse((FW/'code.py').read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('text','grid','draw')]
  self.ns={'oled':self.fb,'engine':Engine(lambda m:None),'notice_until':0,'title_until':0,'status':{}}
  exec(compile(ast.Module(body=functions,type_ignores=[]),'display','exec'),self.ns)
 def tearDown(self):
  if self.fb._font:self.fb._font._font.close()
  os.chdir(self.old)
 def test_grid_dividers(self):
  self.ns['engine'].click();self.ns['engine'].tap(1);self.ns['draw'](1)
  for y in range(32):self.assertEqual(self.fb.pixel(42,y),1);self.assertEqual(self.fb.pixel(85,y),1)
  for x in range(128):self.assertEqual(self.fb.pixel(x,15),1)
 def test_gaming_no_grid(self):
  e=self.ns['engine'];e.page='gaming';self.ns['status']={'app':'Spotify','icon':'spotify','volume':50,'mic':True};self.ns['draw'](1)
  self.assertLess(sum(self.fb.pixel(42,y) for y in range(32)),32)
 def test_non_ascii_result(self):self.ns.update(notice_until=2,notice='x = −4');self.ns['draw'](1)
if __name__=='__main__':unittest.main()
