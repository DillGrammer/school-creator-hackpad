import sys,pathlib,unittest,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'firmware'),str(ROOT/'helper')]
from engine import Engine,ROWS
from actions import copy_unique,valid_url
from platform_io import NotReady
class Controls(unittest.TestCase):
 def setUp(self):self.sent=[];self.e=Engine(self.sent.append);self.e.click()
 def tap(self,k,t=1):self.e.key(k,True,t);self.e.key(k,False,t+.1)
 def test_course_direct(self):self.tap(1);self.tap(2);self.assertEqual(self.sent[-1]['action'],'course.mylab')
 def test_small_selector(self):self.tap(1);self.tap(6);self.e.rotate(1);self.e.click();self.assertEqual(self.sent[-1]['action'],'organizer.event')
 def test_os_switch_clears_old_navigation(self):
  self.e.enter('course');self.e.enter('boot');self.e.click()
  self.assertEqual(self.e.stack,[]);self.assertEqual(self.e.page,'root')
 def test_root_wrap(self):self.e.rotate(-1);self.assertEqual(self.e.roots()[self.e.root],'More')
 def test_back_no_export(self):
  self.e.enter('capcut');self.e.key(6,True,1);self.e.encoder_pressed(1.01);self.e.key(0,False,1.02);self.e.key(6,False,1.03)
  self.assertEqual(self.e.page,'root');self.assertEqual([x['action'] for x in self.sent],['os_changed','cancel'])
 def test_back_release_reverse(self):
  self.e.enter('capcut');self.e.key(6,True,1);self.e.encoder_pressed(1.01);self.e.key(6,False,1.02);self.e.key(0,False,1.03)
  self.assertEqual([x['action'] for x in self.sent],['os_changed','cancel'])
 def test_key6_normal_release(self):self.e.enter('capcut');self.tap(6);self.assertEqual(self.sent[-1]['action'],'capcut.export')
 def test_redo_without_undo(self):
  self.e.enter('capcut');self.e.key(3,True,1);self.e.tick(1.7);self.e.key(3,False,2)
  self.assertEqual([x['action'] for x in self.sent],['os_changed','capcut.redo'])
 def test_volume_modifier_consumes_tap(self):
  self.e.enter('capcut');self.e.key(4,True,1);self.e.rotate(2);self.e.key(4,False,2)
  self.assertEqual(self.e.page,'capcut');self.assertEqual(self.sent[-1]['action'],'capcut.volume')
 def test_nested_rotation_no_category_change(self):self.tap(1);self.e.rotate(2);self.assertEqual(self.e.page,'course');self.assertEqual(self.e.root,0)
 def test_windows_gaming(self):
  e=Engine(self.sent.append,'windows');e.click();e.rotate(2);e.tap(4);e.rotate(-1)
  self.assertEqual(e.page,'gaming');self.assertEqual(self.sent[-1]['action'],'gaming.volume')
 def test_gaming_click_enters_volume(self):
  e=Engine(self.sent.append,'windows');e.click();e.rotate(2);e.click();e.rotate(1)
  self.assertEqual(e.page,'gaming');self.assertEqual(self.sent[-1]['action'],'gaming.volume')
 def test_back_consumes_previous_track(self):
  self.e.enter('gaming');self.e.key(6,True,1);self.e.encoder_pressed(1.1);self.e.key(6,False,1.2);self.e.key(0,False,1.3)
  self.assertNotIn('gaming.previous',[m['action'] for m in self.sent])
 def test_grid_widths(self):
  for row in ROWS:
   for label,_ in row:self.assertLessEqual(len(label)*6,40)
 def test_copy_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'dest').mkdir();f=p/'a.txt';f.write_text('new');(p/'dest'/'a.txt').write_text('old')
   result=copy_unique(f,p/'dest');self.assertEqual(result.name,'a-1.txt');self.assertEqual((p/'dest'/'a.txt').read_text(),'old')
 def test_invalid_url(self):
  for url in ['', 'file:///etc/passwd','javascript:alert(1)']:
   with self.assertRaises(NotReady):valid_url(url)
if __name__=='__main__':unittest.main()
