import os,pathlib,sys,tempfile,threading,time,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'helper'))
try:import av
except ImportError:av=None
from video_check import validate_video
from platform_io import NotReady
@unittest.skipUnless(av,'Install helper dependencies for real video checks')
class VideoChecks(unittest.TestCase):
 def make(self,path,w=1080,h=1920,fps=30):
  with av.open(str(path),'w') as out:
   stream=out.add_stream('libx264',rate=fps);stream.width=w;stream.height=h;stream.pix_fmt='yuv420p'
   for _ in range(3):
    frame=av.VideoFrame(w,h,'yuv420p')
    for plane in frame.planes:plane.update(bytes(plane.buffer_size))
    for packet in stream.encode(frame):out.mux(packet)
   for packet in stream.encode():out.mux(packet)
  os.utime(path,(time.time()-5,time.time()-5))
 def test_complete_portrait(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'clip.mp4';self.make(p)
   self.assertEqual(validate_video(p,threading.Event())['decoded_frames'],3)
 def test_landscape_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'clip.mp4';self.make(p,1920,1080)
   with self.assertRaisesRegex(NotReady,'portrait'):validate_video(p,threading.Event())
 def test_wrong_fps_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'clip.mp4';self.make(p,fps=24)
   with self.assertRaisesRegex(NotReady,'30 fps'):validate_video(p,threading.Event())
 def test_partial_file_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'clip.mp4';p.write_bytes(b'incomplete');os.utime(p,(0,0))
   with self.assertRaises(NotReady):validate_video(p,threading.Event())
 def test_cancel_before_upload(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'clip.mp4';self.make(p);cancel=threading.Event();cancel.set()
   with self.assertRaisesRegex(NotReady,'Cancelled'):validate_video(p,cancel)
