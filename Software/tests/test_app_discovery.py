import pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'helper'))
from app_discovery import find_shortcut
from platform_io import NotReady

class AppDiscoveryTests(unittest.TestCase):
 def test_exact_game_shortcut_not_uninstaller(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'Uninstall VALORANT.lnk').touch();(p/'VALORANT.lnk').touch()
   self.assertEqual(find_shortcut('valorant',[p]).name,'VALORANT.lnk')
 def test_user_shortcut_precedes_shared(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);user=p/'user';shared=p/'shared';user.mkdir();shared.mkdir()
   (user/'Spotify.lnk').touch();(shared/'Spotify.lnk').touch()
   self.assertEqual(find_shortcut('spotify',[user,shared]),user/'Spotify.lnk')
 def test_missing_app_requires_setup(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(NotReady):find_shortcut('fortnite',[d])
